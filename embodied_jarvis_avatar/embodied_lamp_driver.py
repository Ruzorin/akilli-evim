"""
 =============================================================================
 embodied_jarvis_avatar — PCA9685 MG996R/SG90 Servo Sürücü (Autonomous OS HAL)
 =============================================================================
 2026 Sürümü — Autonomous OS motion driver (MotionService protocol)

 Bu driver, Autonomous OS'in HAL motion capability'si için özel bir
 backend'dir. Orijinal Autonomous Lamp Feetech bus servo kullanır,
 biz MG996R + SG90 + PCA9685 I2C PWM sürücü kullanıyoruz.

 🧠 MANTIK:
    Autonomous OS Skill → motion.move(angles) → HAL route → BU DRIVER
    → PCA9685 I2C → PWM sinyali → Servo pozisyon

    Beyin (Cloud VPS) MQTT ile servo açı komutu gönderir →
    Autonomous OS system/network → HAL motion route →
    PCA9685MotionService.move() → PCA9685 → Servo

 GEREKLİ KÜTÜPHANELER:
    pip install adafruit-circuitpython-pca9685 RPi.GPIO

 =============================================================================
"""

import asyncio
import logging
import math
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
except ImportError:
    raise ImportError(
        "PCA9685 kütüphaneleri gerekli:\n"
        "  pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-motor"
    )


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

@dataclass
class LampKinematics:
    """5-DOF lamba kinematik parametreleri (BCN3D Moveo adaptasyonu)."""

    # Link uzunlukları (mm)
    L1_BASE_HEIGHT: float = 120.0    # Base → Shoulder
    L2_SHOULDER_ELBOW: float = 150.0 # Shoulder → Elbow
    L3_ELBOW_WRIST: float = 120.0    # Elbow → Wrist
    L4_WRIST_HEAD: float = 80.0      # Wrist → Kafa merkezi

    # Servo açı sınırları (derece) — SAFETY.md ile uyumlu
    BASE_MIN: float = 0.0
    BASE_MAX: float = 180.0
    SHOULDER_MIN: float = 30.0
    SHOULDER_MAX: float = 150.0
    ELBOW_MIN: float = 0.0
    ELBOW_MAX: float = 135.0
    WRIST_PITCH_MIN: float = 0.0
    WRIST_PITCH_MAX: float = 180.0
    WRIST_ROLL_MIN: float = 0.0
    WRIST_ROLL_MAX: float = 180.0

    # Hareket hızı (derece/saniye) — yumuşak hareket için
    MAX_SPEED: float = 60.0  # 60°/sn — ani hareket yok


@dataclass
class ServoChannel:
    """PCA9685 kanal → servo eşlemesi."""
    BASE: int = 0          # MG996R — Base rotasyon
    SHOULDER: int = 1      # MG996R — Shoulder (omuz)
    ELBOW: int = 2         # MG996R — Elbow (dirsek)
    WRIST_PITCH: int = 3   # SG90 — Wrist pitch (kafa yukarı/aşağı)
    WRIST_ROLL: int = 4    # SG90 — Wrist roll (kafa sağa/sola)


# =============================================================================
# PCA9685 MOTION SERVICE — Autonomous OS HAL MotionService Protocol
# =============================================================================

class PCA9685MotionService:
    """
    Autonomous OS HAL motion capability için PCA9685 backend.

    MotionService protocol'ünü implement eder (hal/drivers/motors/base.py):
      - move(angles: Dict[str, float]) → bool
      - aim(x: float, y: float, z: float) → bool  (inverse kinematics)
      - home() → bool
      - estop() → None
      - get_position() → Dict[str, float]

    🛡️ GÜVENLIK:
      SAFETY.md sınırları HER ZAMAN uygulanır — LLM üzerinden geçmez.
      estop() çağrıldığında tüm servolar anında durur.
    """

    def __init__(self, kinematics: LampKinematics = None):
        self.kin = kinematics or LampKinematics()
        self.channels = ServoChannel()
        self._estop_active = False

        # I2C bus başlat
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c, address=0x40)
        self.pca.frequency = 50  # 50Hz — servo PWM standardı

        # Servo nesneleri oluştur
        self.servos: Dict[int, servo.Servo] = {}
        for ch in range(5):
            self.servos[ch] = servo.Servo(self.pca.channels[ch])

        # Mevcut pozisyon
        self._current_angles: Dict[int, float] = {
            self.channels.BASE: 90.0,
            self.channels.SHOULDER: 90.0,
            self.channels.EBLOW: 90.0,
            self.channels.WRIST_PITCH: 90.0,
            self.channels.WRIST_ROLL: 90.0,
        }

        logging.basicConfig(level=logging.INFO, format='[LampDriver] %(message)s')
        self.log = logging.getLogger("lamp_driver")
        self.log.info("PCA9685 Motion Service başlatıldı (5-DOF, MG996R×3 + SG90×2)")

    # =========================================================================
    # MOVE — Belirli açılara git
    # =========================================================================
    async def move(self, angles: Dict[str, float]) -> bool:
        """
        Servo açılarını ayarla.

        Args:
            angles: {"base": 90.0, "shoulder": 80.0, ...}

        Returns:
            True başarılı, False güvenlik sınırı aşıldı

        🛡️ Güvenlik: SAFETY.md sınırları uygulanır
        """
        if self._estop_active:
            self.log.warning("E-STOP aktif — hareket reddedildi")
            return False

        # Açıları kanallara eşle ve sınırları uygula
        angle_map = {
            "base": (self.channels.BASE, self.kin.BASE_MIN, self.kin.BASE_MAX),
            "shoulder": (self.channels.SHOULDER, self.kin.SHOULDER_MIN, self.kin.SHOULDER_MAX),
            "elbow": (self.channels.ELBOW, self.kin.ELBOW_MIN, self.kin.ELBOW_MAX),
            "wrist_pitch": (self.channels.WRIST_PITCH, self.kin.WRIST_PITCH_MIN, self.kin.WRIST_PITCH_MAX),
            "wrist_roll": (self.channels.WRIST_ROLL, self.kin.WRIST_ROLL_MIN, self.kin.WRIST_ROLL_MAX),
        }

        for name, angle in angles.items():
            if name not in angle_map:
                self.log.warning(f"Bilinmeyen servo: {name}")
                continue

            ch, min_ang, max_ang = angle_map[name]
            # Güvenlik sınırı uygula
            clamped = max(min_ang, min(max_ang, angle))

            if clamped != angle:
                self.log.warning(f"{name}: {angle}° → {clamped}° (sınır aşıldı)")

            # Yumuşak hareket — hedefe kademeli git
            await self._smooth_move(ch, self._current_angles[ch], clamped)
            self._current_angles[ch] = clamped

        return True

    # =========================================================================
    # AIM — Inverse Kinematics ile hedefe yönel
    # =========================================================================
    async def aim(self, x: float, y: float, z: float) -> bool:
        """
        Kafa modülünü (x, y, z) hedefine yönlendir (inverse kinematics).

        Args:
            x, y, z: Hedef koordinat (metre) — masa yüzeyine göre

        Returns:
            True başarılı, False erişilemez

        🎯 KULLANIM:
          Postür Kalkanı: lamba kullanıcıya "uzanır"
          aim(0.3, 0.0, 0.5) → 30cm ileri, 50cm yukarı
        """
        # İleri kinematik ile erişilebilirlik kontrolü
        reach = math.sqrt(x**2 + y**2 + z**2)
        max_reach = (self.kin.L2_SHOULDER_ELBOW +
                     self.kin.L3_ELBOW_WRIST +
                     self.kin.L4_WRIST_HEAD) / 1000.0  # mm → m

        if reach > max_reach:
            self.log.warning(f"Hedef erişilemez: {reach:.2f}m > {max_reach:.2f}m")
            return False

        # Basit inverse kinematics (2D plan — y ekseni ihmal)
        # θ₁ (base) = atan2(y, x)
        theta1 = math.degrees(math.atan2(y, x)) + 90.0  # 0° = öne

        # 2D plan (x-z düzlemi)
        r = math.sqrt(x**2 + z**2) * 1000.0  # m → mm
        z_mm = z * 1000.0 - self.kin.L1_BASE_HEIGHT

        # θ₂ (shoulder) ve θ₃ (elbow) — 2-link IK
        L2 = self.kin.L2_SHOULDER_ELBOW
        L3 = self.kin.L3_ELBOW_WRIST + self.kin.L4_WRIST_HEAD

        cos_theta3 = (r**2 + z_mm**2 - L2**2 - L3**2) / (2 * L2 * L3)
        cos_theta3 = max(-1.0, min(1.0, cos_theta3))
        theta3 = math.degrees(math.acos(cos_theta3))

        theta2 = math.degrees(math.atan2(z_mm, r) -
                              math.atan2(L3 * math.sin(math.radians(theta3)),
                                         L2 + L3 * math.cos(math.radians(theta3))))

        # Wrist pitch — hedefe bak
        theta4 = 90.0  # Neutral
        theta5 = 90.0  # Neutral

        angles = {
            "base": theta1,
            "shoulder": theta2,
            "elbow": theta3,
            "wrist_pitch": theta4,
            "wrist_roll": theta5,
        }

        return await self.move(angles)

    # =========================================================================
    # HOME — Park pozisyonu
    # =========================================================================
    async def home(self) -> bool:
        """Lambayı park pozisyonuna getir (dik, nötr)."""
        self.log.info("Park pozisyonuna dönülüyor...")
        return await self.move({
            "base": 90.0,
            "shoulder": 90.0,
            "elbow": 90.0,
            "wrist_pitch": 90.0,
            "wrist_roll": 90.0,
        })

    # =========================================================================
    # E-STOP — Acil durdurma (SAFETY.md)
    # =========================================================================
    def estop(self) -> None:
        """
        Tüm servoları anında durdur.

        🛡️ BU FONKSİYON LLM ÜZERİNDEN GEÇMEZ — doğrudan HAL'da uygulanır.
        MQTT "jarvis/lamp/safety/estop" → system/monitor → BU FONKSİYON
        """
        self._estop_active = True
        self.log.warning("🚨 E-STOP! Tüm servolar durduruldu")
        # Servoları mevcut pozisyonda dondur (PWM sinyali kesilir)
        self.pca.deinit()

    def release_estop(self) -> None:
        """E-STOP'u serbest bırak (sadece HA üzerinden manuel)."""
        self._estop_active = False
        self.pca = PCA9685(self.i2c, address=0x40)
        self.pca.frequency = 50
        self.log.info("E-STOP serbest bırakıldı")

    # =========================================================================
    # GET POSITION — Mevcut açıları döndür
    # =========================================================================
    def get_position(self) -> Dict[str, float]:
        """Mevcut servo açılarını döndür."""
        return {
            "base": self._current_angles[self.channels.BASE],
            "shoulder": self._current_angles[self.channels.SHOULDER],
            "elbow": self._current_angles[self.channels.ELBOW],
            "wrist_pitch": self._current_angles[self.channels.WRIST_PITCH],
            "wrist_roll": self._current_angles[self.channels.WRIST_ROLL],
        }

    # =========================================================================
    # YUMUŞAK HAREKET — Kademeli servo geçişi
    # =========================================================================
    async def _smooth_move(self, channel: int, from_angle: float, to_angle: float) -> None:
        """
        Servoyu anında değil, kademeli olarak hedefe götür.

        🎯 Neden?
          Ani servo hareket = mekanik şok → 3D baskı parça kırılabilir
          Yumuşak hareket = 60°/sn → güvenli, pürüzsüz

        Postür Kalkanı için kritik:
          Lamba "sıçramaz" — yavaşça kullanıcıya "uzanır"
        """
        diff = to_angle - from_angle
        steps = max(1, int(abs(diff) / 2.0))  # 2° adım
        delay = 0.03  # 30ms per adım → ~60°/sn

        for i in range(steps):
            if self._estop_active:
                return
            progress = (i + 1) / steps
            angle = from_angle + diff * progress
            self.servos[channel].angle = angle
            await asyncio.sleep(delay)

        # Son pozisyon
        self.servos[channel].angle = to_angle


# =============================================================================
# MQTT BRIDGE — Cloud VPS'ten gelen komutları uygula
# =============================================================================

class LampMQTTBridge:
    """
    Cloud VPS (beyin) → Pi (gövde) MQTT komut köprüsü.

    MQTT topic'leri:
      jarvis/lamp/motion/command → move/aim/home
      jarvis/lamp/light/command  → LED halkası
      jarvis/lamp/safety/estop   → Acil durdurma
    """

    def __init__(self, motion_service: PCA9685MotionService):
        self.motion = motion_service

        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            raise ImportError("paho-mqtt gerekli: pip install paho-mqtt")

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="jarvis-lamp-edge"
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self, broker: str, port: int = 1883):
        self.client.connect(broker, port)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[LampBridge] ✅ MQTT bağlandı")
            client.subscribe([
                ("jarvis/lamp/motion/command", 1),
                ("jarvis/lamp/light/command", 1),
                ("jarvis/lamp/safety/estop", 1),
            ])
        else:
            print(f"[LampBridge] ❌ MQTT hata: {rc}")

    def _on_message(self, client, userdata, msg):
        """Cloud VPS'ten gelen komutu uygula."""
        import json

        try:
            payload = json.loads(msg.payload.decode())

            if msg.topic == "jarvis/lamp/motion/command":
                skill = payload.get("skill")

                if skill == "move":
                    asyncio.create_task(self.motion.move(payload["angles"]))
                elif skill == "aim":
                    asyncio.create_task(self.motion.aim(
                        payload["x"], payload["y"], payload["z"]
                    ))
                elif skill == "home":
                    asyncio.create_task(self.motion.home())

            elif msg.topic == "jarvis/lamp/safety/estop":
                if payload.get("active", True):
                    self.motion.estop()
                else:
                    self.motion.release_estop()

        except Exception as e:
            print(f"[LampBridge] Komut hatası: {e}")


# =============================================================================
# MAIN — Test modu
# =============================================================================

async def main():
    """Driver test — servo hareketlerini doğrula."""
    driver = PCA9685MotionService()

    print("\n=== Jarvis Lamp Driver Test ===")
    print("1. Park pozisyonu...")
    await driver.home()
    await asyncio.sleep(1)

    print("2. Kullanıcıya uzan (30cm ileri, 50cm yukarı)...")
    await driver.aim(0.3, 0.0, 0.5)
    await asyncio.sleep(1)

    print("3. Park pozisyonuna dön...")
    await driver.home()

    print("\nMevcut pozisyon:", driver.get_position())
    print("Test tamam.")


if __name__ == "__main__":
    asyncio.run(main())