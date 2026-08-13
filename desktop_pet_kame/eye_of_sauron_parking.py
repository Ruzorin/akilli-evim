"""
 =============================================================================
 desktop_pet_kame — Eye of Sauron Otonom Şarj Park Sistemi
 =============================================================================
 2026 Sürümü — Tapo C200 IP Kamera + OpenCV + Closed-Loop Park

 🦅 "EYE OF SAURON" MANTIĞI:
    Masaya yukarıdan bakan Tapo C200 (Modül 13) IP kamera, Kame'nin
    masadaki konumunu sürekli izler. Kame'nin şarjı %20'nin altına
    düştüğünde, Jarvis "Eye of Sauron" modunu aktive eder:

    1. Tapo C200 → RTSP stream → OpenCV ile Kame'nin konumunu tespit et
    2. Qi şarj pedinin konumu SABİT (kalibrasyon sırasında belirlenir)
    3. Jarvis, Kame'ye MQTT komutları gönderir (ileri, sağa dön, ileri...)
    4. Kame her hareketten sonra durur → kamera yeni konumu okur
    5. Kame şarj pedi üzerine gelene kadar döngü devam eder
    6. Qi ped teması → şarj başlar → Kame çömelir (uyku modu)

 🧠 KAPALI DÖNGÜ (CLOSED-LOOP):
    Kamera → Konum → Hata Vektörü → Komut → Hareket → Yeni Konum → ...
    Kame'nin kendi sensörü YOK — dış göz (Tapo C200) ile kapalı döngü.

 GEREKLİ KÜTÜPHANELER:
    pip install opencv-python httpx numpy

 =============================================================================
"""

import asyncio
import time
import math
import json
import logging
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError("opencv-python gerekli: pip install opencv-python numpy")

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

@dataclass
class SauronConfig:
    """Eye of Sauron park sistemi konfigürasyonu."""

    # Tapo C200 RTSP (Modül 13)
    RTSP_URL: str = "rtsp://admin:password@192.168.1.107:554/stream1"

    # Qi şarj pedi konumu (masa koordinat sistemi — kalibrasyon gerekir)
    # Bu değerler, kamera yukarıdan baktığında masanın görüntüsünde
    # Qi pedinin piksel koordinatları olarak belirlenir
    CHARGE_PAD_X: float = 0.5    # 0-1 normalize (görüntü genişliği)
    CHARGE_PAD_Y: float = 0.8    # 0-1 normalize (görüntü yüksekliği)
    CHARGE_PAD_RADIUS: float = 0.05  # Park toleransı (normalize)

    # Kame tespiti — renk tabanlı (Kame'nin rengi belirgin olmalı)
    # Kame'nin gövdesine belirgin renkli bir işaretleyici yapıştırılır
    KAME_COLOR_LOWER: Tuple[int, int, int] = (0, 100, 100)    # HSV alt
    KAME_COLOR_UPPER: Tuple[int, int, int] = (20, 255, 255)  # HSV üst (turuncu)

    # Park parametreleri
    MAX_PARK_STEPS: int = 20          # Maksimum hareket adımı
    STEP_FORWARD_DISTANCE: float = 0.05  # Bir adım ileri = %5 görüntü
    TURN_THRESHOLD_DEG: float = 15.0  # Bu açıdan az ise düz git
    POSITION_THRESHOLD: float = 0.05  # Park toleransı (normalize)

    # MQTT (Kame'ye komut gönder)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_COMMAND: str = "kame/command/move"
    MQTT_TOPIC_BATTERY: str = "kame/status/battery"

    # HA REST API (şarj durumu)
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # Batarya eşiği
    LOW_BATTERY_THRESHOLD: int = 20  # %20 altında → park modu


# =============================================================================
# PARK DURUMU
# =============================================================================

class ParkState(Enum):
    """Otonom park durumu makinesi."""
    IDLE = "idle"                    # Bekle
    SCANNING = "scanning"            # Kamera ile Kame'yi ara
    PLANNING = "planning"            # Hesapla: ne tarafa, kaç adım
    MOVING = "moving"                # Kame'ye komut gönder
    VERIFYING = "verifying"          # Yeni konumu doğrula
    PARKED = "parked"                # Şarj pedinde — şarj oluyor
    FAILED = "failed"                # Park başarısız


# =============================================================================
# EYE OF SAURON — KAPALI DÖNGÜ PARK SİSTEMİ
# =============================================================================

class EyeOfSauron:
    """
    Tapo C200 + OpenCV ile Kame'nin masadaki konumunu izler ve
    şarj pedine otonom olarak park ettirir.

    🦅 "Eye of Sauron" — yukarıdan bakan göz:
    Kamera → Kame konumu → Hata vektörü → MQTT komut → Hareket → Tekrar

    🧠 KAPALI DÖNGÜ MİMARİSİ:
    1. SCANNING: Kamera karesi al → OpenCV renk filtre → Kame konumu
    2. PLANNING: Kame ↔ Qi ped arası hata vektörü hesapla
    3. MOVING: MQTT ile Kame'ye komut gönder (ileri/sağa/sola)
    4. VERIFYING: 2 sn bekle → yeni kamera karesi → yeni konum
    5. DÖNGÜ: Hata < tolerans → PARKED, değilse → PLANNING
    """

    def __init__(self, config: SauronConfig = None):
        self.config = config or SauronConfig()
        self.state = ParkState.IDLE
        self._step_count = 0
        self._kame_position: Optional[Tuple[float, float]] = None
        self._pad_position: Tuple[float, float] = (
            self.config.CHARGE_PAD_X, self.config.CHARGE_PAD_Y
        )

        # Kamera
        self.cap = cv2.VideoCapture(self.config.RTSP_URL)

        # MQTT client
        try:
            import paho.mqtt.client as mqtt
            self.mqtt = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
                client_id="eye-of-sauron"
            )
        except ImportError:
            raise ImportError("paho-mqtt gerekli: pip install paho-mqtt")

        logging.basicConfig(level=logging.INFO, format='[Sauron] %(message)s')
        self.log = logging.getLogger("sauron")
        self.log.info("Eye of Sauron park sistemi başlatıldı")

    # =========================================================================
    # KAME TESPİTİ — OpenCV Renk Filtre
    # =========================================================================
    def detect_kame(self) -> Optional[Tuple[float, float]]:
        """
        Tapo C200'den kare al, Kame'nin masadaki konumunu tespit et.

        🎯 MANTIK:
        Kame'nin gövdesine turuncu renkli işaretleyici yapıştırılır.
        OpenCV HSV renk filtresi ile bu işaretleyiciyi bul → centroid = Kame konumu.

        Returns:
            (x, y) normalize koordinat (0-1), veya None (bulunamadı)
        """
        # RTSP buffer'ı temizle
        for _ in range(3):
            self.cap.grab()

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.log.warning("Kamera karesi alınamadı")
            return None

        # HSV'ye çevir
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Renk filtre (turuncu işaretleyici)
        lower = np.array(self.config.KAME_COLOR_LOWER)
        upper = np.array(self.config.KAME_COLOR_UPPER)
        mask = cv2.inRange(hsv, lower, upper)

        # Gürültü temizle
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        # Kontur bul
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            self.log.warning("Kame bulunamadı — işaretleyici görünmüyor")
            return None

        # En büyük kontur = Kame
        largest = max(contours, key=cv2.contourArea)

        # Minimum alan kontrolü (gürültü filtre)
        if cv2.contourArea(largest) < 100:
            self.log.warning("Kame çok küçük — kamera menzil dışı?")
            return None

        # Centroid hesapla
        M = cv2.moments(largest)
        if M["m00"] == 0:
            return None

        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]

        # Normalize (0-1)
        h, w = frame.shape[:2]
        norm_x = cx / w
        norm_y = cy / h

        self._kame_position = (norm_x, norm_y)
        self.log.info(f"Kame konumu: ({norm_x:.2f}, {norm_y:.2f})")
        return (norm_x, norm_y)

    # =========================================================================
    # HATA VEKTÖRÜ HESAPLA
    # =========================================================================
    def compute_error_vector(self) -> Optional[Tuple[float, float, float]]:
        """
        Kame ↔ Qi ped arasındaki hata vektörünü hesapla.

        Returns:
            (dx, dy, distance) — normalize koordinat
            dx > 0: ped sağda, dx < 0: ped solda
            dy > 0: ped aşağıda (kamera perspektifi), dy < 0: ped yukarıda
            distance: normalize mesafe (0-1)
        """
        if self._kame_position is None:
            return None

        kx, ky = self._kame_position
        px, py = self._pad_position

        dx = px - kx
        dy = py - ky
        distance = math.sqrt(dx**2 + dy**2)

        return (dx, dy, distance)

    # =========================================================================
    # KOMUT PLANLAMA
    # =========================================================================
    def plan_command(self, dx: float, dy: float, distance: float) -> Dict:
        """
        Hata vektörüne göre Kame'ye gönderilecek komutu planla.

        🧠 MANTIK:
        - Mesafe < tolerans → PARKED (şarj pedinde)
        - |dx| > |dy| → yatay hareket (sağa/sola dön)
        - |dy| > |dx| → dikey hareket (ileri/geri)
        - Açı hesapla → dönme miktarı belirle

        Kamera yukarıdan baktığı için:
        - dy > 0 (ped aşağıda) → Kame ileri gitmeli
        - dx > 0 (ped sağda) → Kame sağa dönmeli
        """
        if distance < self.config.POSITION_THRESHOLD:
            return {"action": "parked", "message": "Şarj pedinde!"}

        # Açı hesapla (kamera koordinat → robot koordinat)
        angle = math.degrees(math.atan2(dx, dy))  # 0° = ileri, 90° = sağ

        # Komut belirle
        if abs(angle) < self.config.TURN_THRESHOLD_DEG:
            # Düz ileri
            return {
                "action": "move",
                "dir": "forward",
                "steps": 1,
                "angle": angle
            }
        elif angle > 0:
            # Sağa dön
            turn_steps = max(1, int(abs(angle) / 30))
            return {
                "action": "move",
                "dir": "right",
                "steps": turn_steps,
                "angle": angle
            }
        else:
            # Sola dön
            turn_steps = max(1, int(abs(angle) / 30))
            return {
                "action": "move",
                "dir": "left",
                "steps": turn_steps,
                "angle": angle
            }

    # =========================================================================
    # MQTT KOMUT GÖNDER
    # =========================================================================
    def send_command(self, command: Dict) -> bool:
        """Kame'ye MQTT komut gönder."""
        payload = json.dumps(command)
        result = self.mqtt.publish(
            self.config.MQTT_TOPIC_COMMAND,
            payload,
            qos=1
        )
        self.log.info(f"Komut gönderildi: {payload}")
        return result.rc == 0

    # =========================================================================
    # OTONOM PARK DÖNGÜSÜ — KAPALI DÖNGÜ
    # =========================================================================
    async def autonomous_park(self) -> bool:
        """
        Kame'yi otonom olarak Qi şarj pedine park et.

        🦅 EYE OF SAURON KAPALI DÖNGÜSÜ:
        1. Kame konumunu tespit et (OpenCV)
        2. Hata vektörü hesapla (Kame ↔ ped)
        3. Komut planla (ileri/sağa/sola)
        4. MQTT ile komut gönder
        5. 2 sn bekle (Kame hareket etsin)
        6. Yeni konumu doğrula (OpenCV)
        7. Ped üzerinde mi? → EVET: çömel (şarj), HAYIR: döngü

        Returns:
            True park başarılı, False başarısız
        """
        self.log.info("🦅 Eye of Sauron park modu başlatıldı")
        self.state = ParkState.SCANNING
        self._step_count = 0

        while self._step_count < self.config.MAX_PARK_STEPS:
            self._step_count += 1
            self.log.info(f"--- Adım {self._step_count}/{self.config.MAX_PARK_STEPS} ---")

            # 1. Kame konumunu tespit et
            self.state = ParkState.SCANNING
            kame_pos = self.detect_kame()

            if kame_pos is None:
                self.log.warning("Kame bulunamadı — tekrar deneniyor")
                await asyncio.sleep(2)
                continue

            # 2. Hata vektörü hesapla
            self.state = ParkState.PLANNING
            error = self.compute_error_vector()
            if error is None:
                continue

            dx, dy, distance = error
            self.log.info(f"Hata: dx={dx:.2f}, dy={dy:.2f}, dist={distance:.2f}")

            # 3. Park toleransı içinde mi?
            if distance < self.config.POSITION_THRESHOLD:
                self.state = ParkState.PARKED
                self.log.info("✅ Kame şarj pedinde! Çömelme komutu...")
                self.send_command({"dir": "sit", "steps": 0})
                return True

            # 4. Komut planla
            command = self.plan_command(dx, dy, distance)
            self.log.info(f"Plan: {command}")

            # 5. Komut gönder
            self.state = ParkState.MOVING
            self.send_command(command)

            # 6. Hareketin tamamlanmasını bekle
            await asyncio.sleep(2)

            # 7. Doğrula
            self.state = ParkState.VERIFYING

        # Maksimum adım aşıldı
        self.state = ParkState.FAILED
        self.log.error(f"❌ Park başarısız — {self.config.MAX_PARK_STEPS} adım atıldı")
        return False

    # =========================================================================
    # BATARYA İZLEME
    # =========================================================================
    async def monitor_battery(self):
        """
        Kame'nin batarya seviyesini izle.
        %20 altına düştüğünde otonom park başlat.
        """
        self.log.info("Batarya izleme başlatıldı")

        while True:
            # HA'dan batarya sensörünü oku
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.config.HA_URL}/api/states/sensor.kame_battery",
                        headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"}
                    )

                    if response.status_code == 200:
                        level = int(response.json().get("state", 100))
                        self.log.info(f"Kame batarya: %{level}")

                        if level < self.config.LOW_BATTERY_THRESHOLD:
                            self.log.warning(
                                f"⚠️ Batarya düşük (%{level}) — "
                                f"Eye of Sauron park modu başlatılıyor"
                            )
                            success = await self.autonomous_park()

                            if success:
                                self.log.info("✅ Park başarılı — şarj oluyor")
                            else:
                                self.log.error("❌ Park başarısız — manuel müdahale gerekli")

            except Exception as e:
                self.log.error(f"Batarya izleme hatası: {e}")

            await asyncio.sleep(60)  # Her dakika kontrol et

    # =========================================================================
    # BAĞLANTI
    # =========================================================================
    def connect_mqtt(self):
        self.mqtt.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self.mqtt.loop_start()

    def cleanup(self):
        self.cap.release()
        self.mqtt.loop_stop()
        self.mqtt.disconnect()


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Eye of Sauron test — park döngüsünü çalıştır."""
    sauron = EyeOfSauron()
    sauron.connect_mqtt()

    print("\n=== Eye of Sauron Park Testi ===")
    print("Kame'yi Qi şarj pedine park et...\n")

    success = await sauron.autonomous_park()

    if success:
        print("\n✅ Park başarılı! Kame şarj oluyor.")
    else:
        print("\n❌ Park başarısız.")

    sauron.cleanup()


if __name__ == "__main__":
    asyncio.run(main())