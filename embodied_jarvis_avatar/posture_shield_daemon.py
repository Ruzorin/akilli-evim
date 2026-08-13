"""
 =============================================================================
 embodied_jarvis_avatar — Postür Kalkanı Daemon (Pi Edge)
 =============================================================================
 2026 Sürümü — MediaPipe Pose + Servikal Açı Analizi + MQTT Bridge

 Bu daemon Raspberry Pi 4'te YEREL olarak çalışır:
 1. Pi Camera V2'den kare al (2 FPS)
 2. MediaPipe Pose ile omuz + kulak landmark'larını tespit et
 3. Servikal açı (kulak-omuz açısı) hesapla
 4. Açıyı MQTT ile Cloud VPS'e gönder
 5. Cloud VPS (HA otomasyonu) → lamba hareketi + sesli uyarı

 🧠 NEDEN Pİ'DE (CLOUD'DA DEĞİL)?
    - 1080p kare = ~6MB → Tailscale üzerinden göndermek yavaş
    - MediaPipe Pose Pi 4'te 15-20 FPS → 2 FPS yeterli
    - Sadece AÇI değeri (float) MQTT → ~20 byte/kare

 🦴 VSS BAĞLAMI:
    Kullanıcı 210 cm boyunda, VSS ile mücadele ediyor.
    Tech Neck = baş öne kayar → servikal yük artar → VSS alevlenir.
    Bu daemon, postürü sürekli izler ve Cloud VPS'e raporlar.

 GEREKLİ KÜTÜPHANELER:
    pip install mediapipe opencv-python paho-mqtt

 =============================================================================
"""

import time
import math
import json
import logging
from typing import Optional, Dict
from enum import Enum

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError("opencv-python gerekli: pip install opencv-python numpy")

try:
    import mediapipe as mp
except ImportError:
    raise ImportError("mediapipe gerekli: pip install mediapipe")

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError("paho-mqtt gerekli: pip install paho-mqtt")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class PostureDaemonConfig:
    """Postür Kalkanı daemon konfigürasyonu."""

    # Kamera
    CAMERA_INDEX: int = 0       # Pi Camera V2 (CSI-2)
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    ANALYSIS_FPS: int = 2       # 2 FPS (CPU tasarrufu)

    # MediaPipe Pose
    MODEL_COMPLEXITY: int = 1
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5

    # Servikal açı eşikleri
    TECH_NECK_THRESHOLD: float = 15.0   # 15° öne → Tech Neck
    SEVERE_THRESHOLD: float = 25.0     # 25° öne → Ciddi
    SUSTAINED_DURATION_SEC: int = 30    # 30 sn bozuksa → uyar

    # Cooldown
    ALERT_COOLDOWN_SEC: int = 120       # 2 dk

    # MQTT (Cloud VPS)
    MQTT_BROKER: str = "100.x.x.x"     # Cloud VPS Tailscale IP
    MQTT_PORT: int = 1883
    MQTT_TOPIC: str = "jarvis/lamp/posture/angle"
    MQTT_CLIENT_ID: str = "jarvis-lamp-posture-daemon"


# =============================================================================
# POSTÜR SEVERITY
# =============================================================================

class PostureSeverity(Enum):
    """Postür durum seviyeleri."""
    GOOD = "good"              # < 15° — mükemmel postür
    TECH_NECK = "tech_neck"    # 15-25° — Tech Neck
    SEVERE = "severe"          # > 25° — ciddi postür bozukluğu
    NO_PERSON = "no_person"    # Kullanıcı yok


# =============================================================================
# POSTÜR KALKANI DAEMON
# =============================================================================

class PostureShieldDaemon:
    """
    MediaPipe Pose ile servikal açı analizi + MQTT bridge.

    🦴 ORTOPEDİK KORUMA — 210 cm KULLANICI İÇİN:
    - MediaPipe Pose → omuz (11,12) + kulak (7,8) landmark'ları
    - Servikal açı = kulak-omuz dikey açısı
    - 0° = mükemmel (kulak omuz üzerinde)
    - 15°+ = Tech Neck → Cloud VPS'e rapor
    - 25°+ = Ciddi → Cloud VPS güçlü müdahale

    "Bir doktor titizliğiyle, omurganızı korur."
    """

    def __init__(self, config: PostureDaemonConfig = None):
        self.config = config or PostureDaemonConfig()

        # MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=self.config.MODEL_COMPLEXITY,
            smooth_landmarks=True,
            min_detection_confidence=self.config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.MIN_TRACKING_CONFIDENCE,
        )

        # Kamera
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.FRAME_HEIGHT)

        # MQTT
        self.mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id=self.config.MQTT_CLIENT_ID
        )
        self.mqtt_client.on_connect = self._on_mqtt_connect

        # Durum takibi
        self._bad_posture_start: float = 0
        self._last_alert_time: float = 0
        self._current_severity: PostureSeverity = PostureSeverity.NO_PERSON
        self._sustained_seconds: float = 0

        logging.basicConfig(level=logging.INFO, format='[PostureDaemon] %(message)s')
        self.log = logging.getLogger("posture_daemon")
        self.log.info("Postür Kalkanı Daemon başlatıldı (MediaPipe Pose)")

    # =========================================================================
    # MQTT BAĞLANTI
    # =========================================================================
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.log.info(f"✅ MQTT bağlandı: {self.config.MQTT_BROKER}")
        else:
            self.log.error(f"❌ MQTT hata: {rc}")

    def connect_mqtt(self):
        self.mqtt_client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self.mqtt_client.loop_start()

    # =========================================================================
    # SERVİKAL AÇI HESAPLA
    # =========================================================================
    def calculate_neck_angle(self, landmarks) -> Optional[float]:
        """
        Kulak-omuz açısını hesapla → servikal açı.

        MediaPipe Pose landmark'ları:
          11: sol omuz, 12: sağ omuz
          7: sol kulak, 8: sağ kulak

        Açı hesaplama:
          - Omuz ve kulak arasındaki dikey çizgi → referans
          - Kulak öne kaydığında → açı artar
          - 0° = mükemmel postür (kulak omuz üzerinde)
          - 15°+ = Tech Neck
          - 25°+ = ciddi

        210 cm kullanıcı bağlamı:
          - Uzun boy → servikal bölgeye daha fazla yük
          - İleri baş postürü → skolyoz alevlenme riski
          - "Her 2.5cm öne kayma = ekstra ~2kg kafa yükü"
        """
        try:
            # Sağ tarafı kullan (kullanıcı sağ dönükse)
            shoulder = landmarks[12]  # sağ omuz
            ear = landmarks[8]        # sağ kulak

            # Sol taraf (fallback)
            if shoulder.visibility < 0.5:
                shoulder = landmarks[11]
                ear = landmarks[7]

            if shoulder.visibility < 0.5 or ear.visibility < 0.5:
                return None

            # Açı hesapla
            # Vektör: omuz → kulak
            dx = ear.x - shoulder.x
            dy = ear.y - shoulder.y

            # Dikey referansa göre açı (kulak öne kayma)
            angle = math.degrees(math.atan2(abs(dx), abs(dy)))

            return angle

        except Exception as e:
            self.log.error(f"Açı hesaplama hatası: {e}")
            return None

    # =========================================================================
    # SEVERITY BELİRLE
    # =========================================================================
    def determine_severity(self, angle: Optional[float]) -> PostureSeverity:
        """Açıya göre severity belirle."""
        if angle is None:
            return PostureSeverity.NO_PERSON

        if angle >= self.config.SEVERE_THRESHOLD:
            return PostureSeverity.SEVERE
        elif angle >= self.config.TECH_NECK_THRESHOLD:
            return PostureSeverity.TECH_NECK
        else:
            return PostureSeverity.GOOD

    # =========================================================================
    # MQTT PUBLISH
    # =========================================================================
    def publish_posture(self, angle: Optional[float], severity: PostureSeverity):
        """Postür verisini Cloud VPS'e gönder."""
        payload = {
            "angle": round(angle, 1) if angle is not None else None,
            "severity": severity.value,
            "sustained_seconds": round(self._sustained_seconds, 1),
            "timestamp": time.time(),
        }

        self.mqtt_client.publish(
            self.config.MQTT_TOPIC,
            json.dumps(payload),
            qos=1
        )

    # =========================================================================
    # ANA DÖNGÜ
    # =========================================================================
    def run(self):
        """
        Sürekli postür analizi döngüsü.

        2 FPS → her 500ms'de bir kare al, analiz et, MQTT gönder.
        """
        self.log.info("Postür analizi döngüsü başladı (2 FPS)")
        frame_interval = 1.0 / self.config.ANALYSIS_FPS

        while True:
            start_time = time.time()

            # Kare al
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.log.warning("Kare alınamadı — kamera hatası")
                time.sleep(1)
                continue

            # MediaPipe Pose analizi
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                angle = self.calculate_neck_angle(results.pose_landmarks.landmark)
                severity = self.determine_severity(angle)

                # Sürekli bozukluk takibi
                if severity in [PostureSeverity.TECH_NECK, PostureSeverity.SEVERE]:
                    if self._bad_posture_start == 0:
                        self._bad_posture_start = time.time()
                    self._sustained_seconds = time.time() - self._bad_posture_start
                else:
                    self._bad_posture_start = 0
                    self._sustained_seconds = 0

                # Severity değiştiyse log
                if severity != self._current_severity:
                    self.log.info(
                        f"Postür değişti: {self._current_severity.value} → "
                        f"{severity.value} (açı: {angle:.1f}°)"
                    )
                    self._current_severity = severity

                # MQTT gönder
                self.publish_posture(angle, severity)

            else:
                # Kullanıcı yok
                if self._current_severity != PostureSeverity.NO_PERSON:
                    self.log.info("Kullanıcı algılanmadı")
                    self._current_severity = PostureSeverity.NO_PERSON
                    self._bad_posture_start = 0
                    self._sustained_seconds = 0
                    self.publish_posture(None, PostureSeverity.NO_PERSON)

            # FPS kontrolü
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            time.sleep(sleep_time)

    # =========================================================================
    # TEMİZLE
    # =========================================================================
    def cleanup(self):
        """Kaynakları serbest bırak."""
        self.cap.release()
        self.pose.close()
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.log.info("Postür daemon temizlendi")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Daemon'ı başlat."""
    daemon = PostureShieldDaemon()
    daemon.connect_mqtt()

    try:
        daemon.run()
    except KeyboardInterrupt:
        print("\n[PostureDaemon] Durduruldu")
    finally:
        daemon.cleanup()


if __name__ == "__main__":
    main()