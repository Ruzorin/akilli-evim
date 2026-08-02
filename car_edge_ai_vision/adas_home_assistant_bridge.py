"""
 =============================================================================
 car_edge_ai_vision — ADAS Home Assistant Bridge (MQTT & WLED Entegrasyonu)
 =============================================================================
 2026 Sürümü — Jetson Nano → MQTT → HA → WLED + Sesli Uyarı

 Bu script, Jetson Nano üzerinde çalışan ADAS yapay zekasının algıladığı
 tehlikeleri (ani fren, şeritten çıkma, ön çarpışma) MQTT üzerinden
 Home Assistant'a iletir. HA, bu sinyali alarak:
 - Araç içi WLED şeritlerini kırmızı yanıp söndürür
 - Araç ses sisteminden sesli uyarı verir
 - Jarvis TTS ile "Ön çarpışma tehlikesi!" der

 🚀 MİLİSANİYELİK GECİKME — TENSORRT + MQTT:
 =============================================================================
 TensorRT FP16: 30ms/frame inference → tehlike tespiti anında
 MQTT publish: <10ms (yerel ağ → GL-MT3000)
 HA otomasyon: <50ms (trigger → action)
 WLED yanıp sönme: <20ms (MQTT → ESP32 → LED)

 Toplam gecikme: ~110ms (tehlike → WLED kırmızı)
 "Milisaniyelik gecikme = hayat kurtarır."

 GEREKLİ KÜTÜPHANELER:
   pip install paho-mqtt asyncio

 =============================================================================
"""

import json
import time
import threading
from typing import Optional, Dict
from enum import Enum

try:
    import paho.mqtt.client as mqtt
except ImportError:
    raise ImportError("paho-mqtt gerekli: pip install paho-mqtt")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class ADASBridgeConfig:
    """ADAS → HA MQTT köprüsü konfigürasyonu."""

    # MQTT Broker (GL-MT3000)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883

    # MQTT Topic'ler
    TOPIC_ADAS_WARNING: str = "jarvis/car/adas/warning"       # Jetson → HA
    TOPIC_ADAS_LANE: str = "jarvis/car/adas/lane_status"       # Şerit durumu
    TOPIC_ADAS_OBJECTS: str = "jarvis/car/adas/objects"       # Algılanan nesneler
    TOPIC_WLED_CONTROL: str = "jarvis/car/wled"                # HA → WLED
    TOPIC_TTS_WARNING: str = "jarvis/car/tts_warning"          # HA → TTS

    # Uyarı tipleri
    COOLDOWN_SECONDS: float = 3.0  # Aynı uyarı tipi için 3sn cooldown


# =============================================================================
# UYARI TİPLERİ
# =============================================================================

class WarningType(Enum):
    """ADAS uyarı tipleri."""
    FCW = "FCW"                    # Forward Collision Warning (ön çarpışma)
    LDW = "LDW"                    # Lane Departure Warning (şeritten çıkma)
    AEB = "AEB"                    # Autonomous Emergency Braking (acil fren)
    PEDESTRIAN = "PEDESTRIAN"      # Yaya algılama
    TAILGATING = "TAILGATING"      # Takip mesafesi çok kısa


# =============================================================================
# ADAS → HA MQTT KÖPRÜSÜ
# =============================================================================

class ADASHomeAssistantBridge:
    """
    Jetson Nano ADAS → MQTT → HA → WLED + Sesli uyarı köprüsü.

    🚀 MİLİSANİYELİK GECİKME MANTIĞI:
    =============================================================================
    TensorRT FP16 inference: 30ms → tehlike tespiti
    MQTT publish: <10ms → HA'a sinyal
    HA otomasyon: <50ms → WLED + TTS tetik
    WLED kırmızı strobe: <20ms → ESP32 → LED

    Toplam: ~110ms (tehlike → kırmızı ışık + sesli uyarı)
    "Milisaniyelik gecikme = hayat kurtarır."

    Bu köprü, Jetson Nano'nun "gördüğü" tehlikeyi HA'a "fısıldar".
    HA, aracın içini (WLED, ses, Jarvis) kontrol eder.
    """

    def __init__(self, config: ADASBridgeConfig = None):
        self.config = config or ADASBridgeConfig()

        # MQTT client
        self.client = mqtt.Client(client_id="adas_bridge")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Cooldown tracking
        self._last_warning_time: Dict[str, float] = {}

        # Bağlan
        self.client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self.client.loop_start()

        print("[ADASBridge] MQTT köprüsü başlatıldı — HA'a bağlandı")

    # =========================================================================
    # MQTT BAĞLANTI
    # =========================================================================
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT bağlantısı kurulduğunda."""
        if rc == 0:
            print(f"[ADASBridge] ✅ MQTT bağlandı: {self.config.MQTT_BROKER}")
            # HA'dan WLED/TTS komutlarını dinle (opsiyonel)
            client.subscribe(self.config.TOPIC_WLED_CONTROL)
        else:
            print(f"[ADASBridge] ❌ MQTT bağlantı hatası: {rc}")

    def _on_message(self, client, userdata, msg):
        """HA'dan gelen mesajları işle (opsiyonel — WLED durum geri bildirimi)."""
        pass

    # =========================================================================
    # TEHLİKE UYARISI GÖNDER — MQTT → HA
    # =========================================================================
    def send_warning(self, warning_type: WarningType, message: str,
                     severity: str = "warning") -> bool:
        """
        ADAS tehlike uyarısını MQTT üzerinden HA'a gönder.

        🚀 MANTIK:
        Jetson Nano bir tehlike algılar (FCW, LDW, AEB) →
        bu fonksiyon MQTT'ye publish eder →
        HA otomasyonu dinler → WLED kırmızı strobe + TTS sesli uyarı.

        Cooldown: Aynı uyarı tipi 3 saniye içinde tekrar gönderilmez
        (sürekli tekrar → sürücüyü rahatsız etme).

        Severity:
        - "info": bilgi (şerit durumu)
        - "warning": uyarı (FCW, LDW)
        - "critical": kritik (AEB, acil fren)
        """
        # Cooldown kontrolü
        key = f"{warning_type.value}_{severity}"
        current_time = time.time()

        if key in self._last_warning_time:
            if current_time - self._last_warning_time[key] < self.config.COOLDOWN_SECONDS:
                return False  # Cooldown içinde → gönderme

        self._last_warning_time[key] = current_time

        # MQTT payload
        payload = json.dumps({
            "type": warning_type.value,
            "message": message,
            "severity": severity,
            "timestamp": current_time
        })

        # Publish
        self.client.publish(self.config.TOPIC_ADAS_WARNING, payload)
        print(f"[ADASBridge] ⚠️ UYARI: {warning_type.value} → {message} ({severity})")

        return True

    # =========================================================================
    # ŞERİT DURUMU GÖNDER
    # =========================================================================
    def send_lane_status(self, lane_left: bool, lane_right: bool,
                        lane_departure: bool = False) -> None:
        """
        Şerit takip durumunu MQTT'ye gönder.

        lane_left: Sol şerit algılandı mı?
        lane_right: Sağ şerit algılandı mı?
        lane_departure: Şeritten çıkma tespit edildi mi?
        """
        payload = json.dumps({
            "lane_left": lane_left,
            "lane_right": lane_right,
            "lane_departure": lane_departure,
            "timestamp": time.time()
        })

        self.client.publish(self.config.TOPIC_ADAS_LANE, payload)

        # Şeritten çıkma → uyarı
        if lane_departure:
            self.send_warning(
                WarningType.LDW,
                "Şeritten çıkma tespit edildi!",
                "warning"
            )

    # =========================================================================
    # NESNE DURUMU GÖNDER
    # =========================================================================
    def send_object_status(self, objects: list) -> None:
        """
        Algılanan nesneleri MQTT'ye gönder (araç, yaya, tabela).

        objects: [{"class": "car", "confidence": 0.95, "distance": 50}, ...]
        """
        payload = json.dumps({
            "objects": objects,
            "count": len(objects),
            "timestamp": time.time()
        })

        self.client.publish(self.config.TOPIC_ADAS_OBJECTS, payload)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    def close(self):
        """MQTT bağlantısını kapat."""
        self.client.loop_stop()
        self.client.disconnect()
        print("[ADASBridge] MQTT köprüsü kapatıldı")


# =============================================================================
# HA OTOMASYON — WLED + SESLİ UYARI (YAML olarak HA'a yüklenecek)
# =============================================================================
# Bu bölüm, HA'a yüklenecek otomasyon YAML'ini içerir.
# Jetson Nano → MQTT → HA → WLED kırmızı strobe + TTS sesli uyarı.
#
# Aşağıdaki YAML, HA configuration.yaml'a veya packages/ klasörüne konulur:
#
# automation:
#   - id: adas_wled_warning
#     alias: "ADAS — WLED Kırmızı Uyarı + Sesli"
#     trigger:
#       - platform: mqtt
#         topic: "jarvis/car/adas/warning"
#         id: adas_warning
#     condition: []
#     action:
#       - variables:
#           warning_type: "{{ trigger.payload_json.type }}"
#           message: "{{ trigger.payload_json.message }}"
#           severity: "{{ trigger.payload_json.severity }}"
#
#       # WLED → kırmızı strobe (ani yanıp sönme)
#       - service: light.turn_on
#         target:
#           entity_id:
#             - light.car_wled_footwell
#             - light.car_wled_door
#         data:
#           rgb_color: [255, 0, 0]     # Kırmızı
#           brightness: 255              # Tam parlaklık
#           effect: "Strobe"            # Yanıp sönme
#           transition: 0              # Anında (gecikme yok)
#
#       # Jarvis sesli uyarı
#       - service: tts.speak
#         target:
#           entity_id: tts.jarvis_voice
#         data:
#           message: "{{ message }}"
#
#       # Kritik ise mobil bildirim
#       - choose:
#           - conditions:
#               - condition: template
#                 value_template: "{{ severity == 'critical' }}"
#             sequence:
#               - service: notify.mobile_app
#                 data:
#                   title: "🚨 ADAS Kritik"
#                   message: "{{ message }}"
#                   data:
#                     push:
#                       interruption_level: "critical"
#
#       # 5 saniye sonra WLED normale döndür
#       - delay:
#           seconds: 5
#       - service: light.turn_on
#         target:
#           entity_id:
#             - light.car_wled_footwell
#             - light.car_wled_door
#         data:
#           rgb_color: [139, 0, 0]     # Derin kırmızı (seduction modu)
#           brightness: 100
#           effect: "Breathe"
#           transition: 2
# =============================================================================


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

def main():
    """ADAS Bridge test."""
    bridge = ADASHomeAssistantBridge()

    # Test: FCW uyarısı gönder
    bridge.send_warning(
        WarningType.FCW,
        "Ön çarpışma tehlikesi! Yavaşlayın!",
        "critical"
    )

    # Test: Şerit durumu
    bridge.send_lane_status(
        lane_left=True,
        lane_right=True,
        lane_departure=False
    )

    # Test: Şeritten çıkma
    time.sleep(1)
    bridge.send_lane_status(
        lane_left=False,
        lane_right=True,
        lane_departure=True
    )

    time.sleep(2)
    bridge.close()
    print("[ADASBridge] Test tamamlandı")


if __name__ == "__main__":
    main()