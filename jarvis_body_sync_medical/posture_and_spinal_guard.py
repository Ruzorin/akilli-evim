"""
 =============================================================================
 jarvis_body_sync_medical — Posture & Spinal Guard (Dev Ergonomisi)
 =============================================================================
 2026 Sürümü — MediaPipe Pose Estimation + Servikal Açı Analizi + Tech Neck Tespiti

 Bu script, çalışma masası kamerasından (veya Modül 13 mutfak kamerasundan)
 alınan görüntüde kullanıcının boyun (servikal) açısını analiz eder. Boyun
 15 dereceden fazla öne kaydığında ("Tech Neck") Jarvis'i tetikleyip sesli
 uyarı verir.

 🦴 ORTOPEDİK KORUMA MANTIĞI:
 =============================================================================
 Skolyoz ve ileri baş postürü (Forward Head Posture) için:
 - Boyun öne kaydığında → servikal omurgaya binen yük artar
 - Her 2.5cm öne kayma = ekstra ~2kg yük (kafa ağırlığı artar)
 - Uzun süreli Tech Neck → skolyoz alevlenmesi → boyun ağrısı → baş ağrısı

 "Bir doktor titizliğiyle, omurganızı korur."

 GEREKLİ KÜTÜPHANELER:
   pip install mediapipe opencv-python httpx asyncio

 =============================================================================
"""

import asyncio
import time
import math
import logging
from typing import Optional, Tuple

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
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class PostureGuardConfig:
    """Posture & Spinal Guard konfigürasyonu."""

    # Kamera
    CAMERA_INDEX: int = 0          # Çalışma masası kamerası
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    ANALYSIS_FPS: int = 2          # 2 FPS (CPU tasarrufu — postür her 0.5sn)

    # Servikal açı eşikleri
    NECK_FORWARD_THRESHOLD: float = 15.0   # 15° öne → "Tech Neck"
    NECK_SEVERE_THRESHOLD: float = 25.0   # 25° öne → "Ciddi postür bozukluğu"

    # Uyarı parametreleri
    ALERT_COOLDOWN_SEC: int = 120         # 2 dk cooldown (sürekli uyarı yapma)
    SUSTAINED_DURATION_SEC: int = 30      # 30 sn boyunca bozuksa → uyar

    # HA REST API
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"


# =============================================================================
# POSTURE & SPINAL GUARD
# =============================================================================

class PostureSpinalGuard:
    """
    MediaPipe Pose Estimation ile servikal açı analizi.

    🦴 ORTOPEDİK KORUMA — DOKTOR TİTİZLİĞİ:
    =============================================================================
    Bu sistem, kullanıcının postürünü sürekli izler:
    - MediaPipe Pose → omuz + kulak + kalça landmark'ları
    - Servikal açı hesapla (kulak-omuz açısı)
    - 15° öne → "Tech Neck" → Jarvis uyarı
    - 25° öne → "Ciddi" → Jarvis uyarı + WLED kehribar (rahatlatıcı)
    - 30 sn boyunca bozuksa → uyarı (ani değil, sürekli bozukluk)

    Skolyoz ve ileri baş postürü için:
    - Boyun öne kayma = ekstra kafa yükü (her 2.5cm = ~2kg)
    - Uzun süreli Tech Neck → skolyoz alevlenmesi
    - "Bir doktor titizliğiyle, omurganızı korur."
    """

    def __init__(self, config: PostureGuardConfig = None):
        self.config = config or PostureGuardConfig()
        self.ha_client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
            timeout=5.0,
        )

        # MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Uyarı takibi
        self._last_alert_time = 0
        self._bad_posture_start = 0
        self._is_bad_posture = False

        logging.basicConfig(level=logging.INFO, format='[PostureGuard] %(message)s')
        self.log = logging.getLogger("posture")

        print("[PostureGuard] MediaPipe Pose başlatıldı (2026)")

    # =========================================================================
    # SERVİKAL AÇI HESAPLA
    # =========================================================================
    def calculate_neck_angle(self, landmarks) -> Optional[float]:
        """
        Kulak-omuz açısını hesapla → servikal açı.

        🦴 MANTIK:
        MediaPipe Pose landmark'ları:
        - 11: sol omuz
        - 12: sağ omuz
        - 7: sol kulak
        - 8: sağ kulak

        Açı hesaplama:
        - Omuz ve kulak arasındaki dikey çizgi → referans
        - Kulak öne kaydığında → açı artar
        - 0° = mükemmel postür (kulak omuz üzerinde)
        - 15°+ = Tech Neck
        - 25°+ = ciddi postür bozukluğu

        Skolyoz bağlamı:
        - Uzun boy → servikal bölgeye daha fazla yük
        - İleri baş postürü → skolyoz alevlenme riski
        - "Her 2.5cm öne kayma = ekstra ~2kg kafa yükü"
        """
        try:
            # Omuz ve kulak landmark'ları
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_ear = landmarks[7]
            right_ear = landmarks[8]

            # Omuz orta noktası
            shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

            # Kulak orta noktası
            ear_x = (left_ear.x + right_ear.x) / 2
            ear_y = (left_ear.y + right_ear.y) / 2

            # Açı hesapla (dikey referans çizgisinden sapma)
            dx = ear_x - shoulder_x
            dy = ear_y - shoulder_y

            # Öne kayma: dx > 0 (kulak omuzdan öne)
            # Açı = arctan(dx / |dy|) → derece
            if abs(dy) < 0.01:
                return None  # Hesaplanamaz

            angle_rad = math.atan2(abs(dx), abs(dy))
            angle_deg = math.degrees(angle_rad)

            # Öne kayma yönü
            if dx > 0:
                return angle_deg  # Öne kayma
            else:
                return -angle_deg  # Geriye (nadir)

        except (IndexError, AttributeError):
            return None

    # =========================================================================
    # KAMERA DÖNGÜSÜ — Postür Analizi
    # =========================================================================
    async def run_posture_loop(self) -> None:
        """
        Sürekli döngü: 2 FPS'de kamera karesi al → MediaPipe Pose →
        servikal açı hesapla → Tech Neck tespiti → Jarvis uyarı.

        🦴 DOKTOR TİTİZLİĞİ:
        Sistem her 0.5 saniyede postürü kontrol eder — sessizce.
        Normal → sessiz. 15° öne → 30 sn bekle → uyarı.
        25° öne → hemen uyarı + WLED kehribar (rahatlatıcı).
        "Bir doktor titizliğiyle, omurganızı korur."
        """
        cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.FRAME_HEIGHT)

        print("[PostureGuard] Postür döngüsü başlatıldı (2 FPS)")

        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    await asyncio.sleep(1)
                    continue

                # MediaPipe Pose
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)

                if results.pose_landmarks:
                    # Servikal açı hesapla
                    angle = self.calculate_neck_angle(results.pose_landmarks.landmark)

                    if angle is not None:
                        await self._check_posture(angle)

            except Exception as e:
                self.log.error(f"Döngü hatası: {e}")

            await asyncio.sleep(0.5)  # 2 FPS

    # =========================================================================
    # POSTÜR KONTROL — Tech Neck Tespiti
    # =========================================================================
    async def _check_posture(self, angle: float) -> None:
        """
        Servikal açıya göre postür değerlendirmesi ve uyarı.

        🦴 MANTIK:
        - 0-15°: Normal postür → sessiz
        - 15-25°: Tech Neck → 30 sn sürerse → uyarı
        - 25°+: Ciddi → hemen uyarı + WLED kehribar

        Cooldown: 2 dk (sürekli uyarı yapma → sürücüyü rahatsız etme)
        """
        current_time = time.time()

        # Normal postür
        if abs(angle) < self.config.NECK_FORWARD_THRESHOLD:
            if self._is_bad_posture:
                self._is_bad_posture = False
                self._bad_posture_start = 0
                self.log.info(f"✅ Postür düzeldi (açı: {angle:.1f}°)")
            return

        # Tech Neck (15-25°)
        if abs(angle) < self.config.NECK_SEVERE_THRESHOLD:
            if not self._is_bad_posture:
                self._is_bad_posture = True
                self._bad_posture_start = current_time
                self.log.warning(f"⚠️ Tech Neck tespit edildi (açı: {angle:.1f}°)")

            # 30 sn boyunca bozuksa → uyarı
            if current_time - self._bad_posture_start >= self.config.SUSTAINED_DURATION_SEC:
                if current_time - self._last_alert_time >= self.config.ALERT_COOLDOWN_SEC:
                    await self._alert_tech_neck(angle)
                    self._last_alert_time = current_time

        # Ciddi postür bozukluğu (25°+)
        else:
            self.log.error(f"🚨 Ciddi postür bozukluğu (açı: {angle:.1f}°)")
            if current_time - self._last_alert_time >= self.config.ALERT_COOLDOWN_SEC:
                await self._alert_severe_posture(angle)
                self._last_alert_time = current_time

    # =========================================================================
    # UYARI — Tech Neck
    # =========================================================================
    async def _alert_tech_neck(self, angle: float) -> None:
        """Tech Neck uyarısı → Jarvis sesli."""
        await self._call_ha_service(
            "tts.speak",
            "tts.jarvis_voice",
            {"message": "Servikal omurganıza binen yük artıyor. Postürünüzü düzeltin — omuzlarınızı geri alın ve çenenizi içe çekin."}
        )
        self.log.warning(f"📢 Tech Neck uyarısı gönderildi (açı: {angle:.1f}°)")

    # =========================================================================
    # UYARI — Ciddi Postür
    # =========================================================================
    async def _alert_severe_posture(self, angle: float) -> None:
        """Ciddi postür bozukluğu → Jarvis + WLED kehribar (rahatlatıcı)."""
        await self._call_ha_service(
            "tts.speak",
            "tts.jarvis_voice",
            {"message": "Ciddi postür bozukluğu tespit edildi. Lütfen hemen doğrulun. Omuzlarınızı geri alın, başınızı dik tutun. 30 saniye mola vermenizi öneririm."}
        )

        # WLED → kehribar (rahatlatıcı, VSS güvenli)
        await self._call_ha_service(
            "light.turn_on",
            "light.wled_ambient",
            {"rgb_color": [191, 128, 0], "brightness": 100, "transition": 3}
        )

        self.log.error(f"🚨 Ciddi postür uyarısı + WLED kehribar (açı: {angle:.1f}°)")

    # =========================================================================
    # HA SERVİS ÇAĞRISI
    # =========================================================================
    async def _call_ha_service(self, service: str, entity_id: str, data: dict) -> None:
        parts = service.split(".")
        if len(parts) != 2:
            return
        domain, service_name = parts
        url = f"/api/services/{domain}/{service_name}"
        data["entity_id"] = entity_id
        try:
            await self.ha_client.post(url, json=data)
        except Exception as e:
            self.log.error(f"HA hatası: {e}")

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        self.pose.close()
        await self.ha_client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Posture Guard test."""
    guard = PostureSpinalGuard()
    await guard.run_posture_loop()
    await guard.close()


if __name__ == "__main__":
    asyncio.run(main())