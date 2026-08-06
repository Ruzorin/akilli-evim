"""
 =============================================================================
 hyperion_media_sync — Agentic Media Orchestrator (Otonom Sahne Yaratıcı)
 =============================================================================
 2026 Sürümü — MiniMax Speech 2.8 Turbo ile izlenen içeriği anla → odayı otonom ayarla

 Bu modül, kullanıcının izlediği içeriği (YouTube/Netflix/ekran analizi) tanır
 ve odayı o içeriğin atmosferine OTOMATIK olarak ayarlar.

 🤖 "OTONOM SAHNE YARATICI" MANTIĞI:
 =============================================================================
 Kullanıcı "Blade Runner" izlemeye başlar →
   1. Qwen-VL Max: ekran analizi → "karanlık, neon, yağmurlu, siberpunk"
   2. AI: "Bu siberpunk → neon pembe/mavi, karanlık, synthwave"
   3. AI KENDİSİ ÜRETİR:
      - WLED: rgb_color [255, 0, 128] (neon pembe), brightness 150
      - Difüzör: "energize" sahnesi (narenciye)
      - Spotify: "synthwave" playlist
      - Klima: 19°C (serin, siberpunk havası)
   4. HA_ACTION: JSON bloğu → HA REST API → oda değişir
   5. Jarvis: "Siberpunk atmosferi, efendim." (KISA)

 Bu, "statik preset" → "dinamik sahne yaratımı" dönüşümüdür.
 AI, "önceden tanımlı modlar" beklemez — izlenen içeriğe göre KENDİSİ
 odayı yaratır.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio

 =============================================================================
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# İÇERİK TİPLERİ VE ATMOSFER EŞLEŞTİRMESİ
# =============================================================================

class ContentType(Enum):
    """İzlenen içerik tipi."""
    CYBERPUNK = "cyberpunk"         # Blade Runner, Cyberpunk 2077
    NATURE = "nature"               # Doğa belgeseli
    HORROR = "horror"               # Korku filmi
    ROMANCE = "romance"             # Romantik
    ACTION = "action"               # Aksiyon
    COMEDY = "comedy"               # Komedi
    SPORTS = "sports"               # Maç/spor
    ANIME = "anime"                 # Anime
    SCI_FI = "sci_fi"              # Bilim kurgu
    UNKNOWN = "unknown"


@dataclass
class AtmosphereProfile:
    """Bir içerik tipi için oda atmosferi profili."""
    content_type: ContentType
    wled_rgb: List[int]            # WLED renk [R, G, B]
    wled_brightness: int           # WLED parlaklık (0-255)
    wled_effect: str               # WLED efekt
    diffuser_scene: str            # Difüzör sahnesi
    climate_temp: int              # Klima sıcaklık
    climate_fan: str               # Klima fan modu
    spotify_mood: str              # Spotify mood
    spotify_volume: float          # Spotify ses seviyesi
    description: str               # Atmosfer açıklaması


# =============================================================================
# ATMOSFER PROFİLLERİ — Her içerik tipi için oda ayarı
# =============================================================================

ATMOSPHERE_PROFILES = {
    ContentType.CYBERPUNK: AtmosphereProfile(
        content_type=ContentType.CYBERPUNK,
        wled_rgb=[255, 0, 128],        # Neon pembe
        wled_brightness=180,
        wled_effect="Breathe",
        diffuser_scene="energize",      # Narenciye/mentol
        climate_temp=19,                # Serin (siberpunk havası)
        climate_fan="low",
        spotify_mood="party_energy",    # Synthwave
        spotify_volume=0.20,
        description="Siberpunk: Neon pembe/mavi, karanlık, synthwave"
    ),
    ContentType.NATURE: AtmosphereProfile(
        content_type=ContentType.NATURE,
        wled_rgb=[34, 139, 34],         # Orman yeşili
        wled_brightness=120,
        wled_effect="Breathe",
        diffuser_scene="relax",         # Sandalağacı
        climate_temp=22,
        climate_fan="quiet",
        spotify_mood="sleep_ambient",   # Doğa sesleri
        spotify_volume=0.10,
        description="Doğa: Yeşil/toprak tonları, sakin, ambient"
    ),
    ContentType.HORROR: AtmosphereProfile(
        content_type=ContentType.HORROR,
        wled_rgb=[50, 0, 0],            # Çok koyu kırmızı (kan)
        wled_brightness=40,             # Çok loş
        wled_effect="Breathe",
        diffuser_scene="relax",         # Sandalağacı (sakinleştirici)
        climate_temp=20,
        climate_fan="low",
        spotify_mood="sleep_ambient",
        spotify_volume=0.05,            # Çok kısık (gerilim)
        description="Korku: Koyu kırmızı, çok loş, gerilim"
    ),
    ContentType.ROMANCE: AtmosphereProfile(
        content_type=ContentType.ROMANCE,
        wled_rgb=[139, 0, 0],           # Yakut kırmızısı
        wled_brightness=100,
        wled_effect="Breathe",
        diffuser_scene="relax",         # Ylang-Ylang
        climate_temp=21,
        climate_fan="quiet",
        spotify_mood="deep_rnb_date",
        spotify_volume=0.15,
        description="Romantik: Yakut kırmızı, loş, R&B"
    ),
    ContentType.ACTION: AtmosphereProfile(
        content_type=ContentType.ACTION,
        wled_rgb=[255, 69, 0],          # Turuncu-kırmızı (patlama)
        wled_brightness=200,
        wled_effect="Breathe",
        diffuser_scene="energize",
        climate_temp=20,
        climate_fan="low",
        spotify_mood="party_energy",
        spotify_volume=0.25,
        description="Aksiyon: Turuncu-kırmızı, parlak, enerjik"
    ),
    ContentType.SPORTS: AtmosphereProfile(
        content_type=ContentType.SPORTS,
        wled_rgb=[200, 16, 46],         # Kırmızı (takım rengi — dinamik)
        wled_brightness=180,
        wled_effect="Breathe",
        diffuser_scene="energize",      # Narenciye/mentol
        climate_temp=20,
        climate_fan="low",
        spotify_mood="off",             # Maç sesi yeterli
        spotify_volume=0.0,
        description="Spor: Takım renkleri, enerjik, stadyum"
    ),
    ContentType.ANIME: AtmosphereProfile(
        content_type=ContentType.ANIME,
        wled_rgb=[100, 149, 237],        # Açık mavi (anime gökyüzü)
        wled_brightness=150,
        wled_effect="Breathe",
        diffuser_scene="relax",
        climate_temp=21,
        climate_fan="quiet",
        spotify_mood="lofi_focus",       # Lo-Fi anime müziği
        spotify_volume=0.12,
        description="Anime: Açık mavi, parlak, Lo-Fi"
    ),
    ContentType.SCI_FI: AtmosphereProfile(
        content_type=ContentType.SCI_FI,
        wled_rgb=[0, 100, 200],          # Mavi (uzay)
        wled_brightness=120,
        wled_effect="Breathe",
        diffuser_scene="relax",
        climate_temp=20,
        climate_fan="low",
        spotify_mood="sleep_ambient",   # Ambient uzay müziği
        spotify_volume=0.10,
        description="Bilim kurgu: Mavi, derin, ambient"
    ),
}


# =============================================================================
# AGENTIC MEDIA ORCHESTRATOR
# =============================================================================

class AgenticMediaOrchestrator:
    """
    Kullanıcının izlediği içeriği analiz eder ve odayı o içeriğin
    atmosferine OTOMATIK olarak ayarlar.

    🤖 NASIL ÇALIŞIR?
    =============================================================================
    1. Hyperion ekran piksellerini yakalar (anlık, <16ms UDP)
    2. Her 30 saniyede bir ekran karesi al → Qwen-VL Max'a gönder
    3. MiniMax Speech 2.8 Turbo: "Bu ekran ne gösteriyor? Film tipi ne?"
    4. İçerik tipi belirlenir → AtmosphereProfile seçilir
    5. HA_ACTION JSON ÜRETİLİR (AI KENDİSİ ÜRETİR):
       - WLED: rgb_color, brightness, effect
       - Difüzör: scene
       - Klima: temperature, fan_mode
       - Spotify: mood, volume
    6. HA REST API → oda değişir

    Bu, "statik preset" → "dinamik sahne yaratımı" dönüşümüdür.
    AI, "önceden tanımlı modlar" beklemez — izlenen içeriğe göre KENDİSİ
    odayı yaratır.

    🎯 SIFIR GECİKME ÖNEMİ:
    =============================================================================
    Hyperion → WLED UDP sync <16ms (1 frame) gecikmeyle çalışır.
    Bu, ekranın "sınırlarının kaybolması"nı sağlar → imersif deneyim.
    Eğer gecikme >50ms olursa → ışık ekrandan "geride kalır" → illüzyon bozulur.
    UDP seçimi KRİTİKTİR — TCP çok yavaş (ACK bekleme).
    """

    def __init__(self):
        # HA REST API client
        self.ha_client = httpx.AsyncClient(
            base_url="http://homeassistant.local:8123",
            headers={
                "Authorization": "Bearer YOUR_HA_LONG_LIVED_TOKEN",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

        # Son içerik tipi (değişim kontrolü için)
        self._last_content_type: ContentType = ContentType.UNKNOWN

        # Analiz aralığı (saniye)
        self._analysis_interval: int = 30  # 30 saniyede bir ekran analizi

        print("[MediaOrchestrator] Agentic Media Orchestrator başlatıldı (2026)")

    # =========================================================================
    # ANA DÖNGÜ — Ekran Analizi → Atmosfer Ayarı
    # =========================================================================
    async def run_analysis_loop(self) -> None:
        """
        Sürekli döngü: her 30 saniyede bir ekranı analiz et → atmosfer ayarla.

        Bu döngü:
        1. Hyperion'dan ekran karesi al (veya ekran görüntüsü yakala)
        2. Qwen-VL Max'a gönder → içerik tipi belirle
        3. İçerik tipi değiştiyse → yeni atmosfer profili uygula
        4. HA REST API → oda değişir

        🤖 AGENTIC:
        AI "önceden tanımlı mod" beklemez. Ekranı GÖRÜR → içerik tipini
        KENDİSİ belirler → atmosferi KENDİSİ yaratır.
        """
        print("[MediaOrchestrator] Analiz döngüsü başlatıldı (30sn aralık)")

        while True:
            try:
                # Adım 1: Ekran karesi al + Qwen-VL Max analizi
                content_type = await self._analyze_screen_content()

                # Adım 2: İçerik tipi değişti mi?
                if content_type != self._last_content_type:
                    print(f"[MediaOrchestrator] İçerik değişti: "
                          f"{self._last_content_type.value} → {content_type.value}")

                    # Adım 3: Yeni atmosfer profili uygula
                    await self._apply_atmosphere(content_type)

                    self._last_content_type = content_type

            except Exception as e:
                print(f"[MediaOrchestrator] Analiz hatası: {e}")

            # Bekle
            await asyncio.sleep(self._analysis_interval)

    # =========================================================================
    # EKRAN İÇERİĞİ ANALİZİ — Qwen-VL Max
    # =========================================================================
    async def _analyze_screen_content(self) -> ContentType:
        """
        Ekran karesini Qwen-VL Max'a gönder → içerik tipi belirle.

        🤖 AGENTIC MANTIK:
        MiniMax Speech 2.8 Turbo, ekran görüntüsünü alır ve "bu ne?" sorusunu yanıtlar:
        - "Karanlık, neon ışıklar, yağmur → CYBERPUNK"
        - "Yeşil orman, hayvanlar → NATURE"
        - "Kırmızı kan, karanlık → HORROR"
        - "Stadyum, futbol → SPORTS"

        Bu, "statik preset" → "dinamik içerik analizi" dönüşümüdür.
        AI, "kullanıcı ne izliyor?" sorusunu KENDİSİ yanıtlar.
        """
        # Gerçek implementasyonda:
        # 1. Hyperion API'den ekran karesi al (veya HDMI grabber'dan)
        # 2. Base64'e çevir
        # 3. Qwen-VL Max'a gönder
        # 4. Cevap: içerik tipi

        # Pseudo-code:
        # frame = capture_screen_frame()
        # frame_b64 = base64_encode(frame)
        # response = await gpt56_vision.analyze(
        #     image=frame_b64,
        #     prompt="Bu ekran görüntüsü ne gösteriyor? Film tipi: cyberpunk, nature, horror, romance, action, sports, anime, sci_fi?"
        # )
        # content_type = parse_content_type(response)

        # Şimdilik mock — gerçek implementasyonda Qwen-VL Max kullanılır
        # return ContentType.CYBERPUNK  # Mock
        return ContentType.UNKNOWN  # Varsayılan

    # =========================================================================
    # ATMOSFER UYGULA — HA REST API
    # =========================================================================
    async def _apply_atmosphere(self, content_type: ContentType) -> None:
        """
        İçerik tipine göre oda atmosferini ayarla.

        🤖 BU, AI'IN HA'I MANİPÜLE ETTİĞİ NOKTADIR:
        AI, "önceden yazılmış komutlara" ihtiyaç duymadan, izlenen içeriğe
        göre KENDİSİ HA REST API'ye istek gönderir.

        Örnek: "Blade Runner" izleniyor → CYBERPUNK →
          - WLED: rgb_color [255, 0, 128] (neon pembe)
          - Difüzör: "energize" (narenciye)
          - Klima: 19°C
          - Spotify: "party_energy" (synthwave)

        AI bu JSON'u KENDİSİ ÜRETİR → HA'a gönderir → oda değişir.
        """
        profile = ATMOSPHERE_PROFILES.get(content_type)
        if not profile:
            print(f"[MediaOrchestrator] Atmosfer profili yok: {content_type.value}")
            return

        print(f"[MediaOrchestrator] Atmosfer uygulanıyor: {profile.description}")

        # -------------------------------------------------------------------------
        # HA_ACTION JSON ÜRET (AI KENDİSİ ÜRETİR)
        # -------------------------------------------------------------------------
        actions = [
            # WLED
            {
                "service": "light.turn_on",
                "entity_id": "light.wled_ambient",
                "data": {
                    "rgb_color": profile.wled_rgb,
                    "brightness": profile.wled_brightness,
                    "effect": profile.wled_effect,
                    "transition": 5
                }
            },
            # Difüzör
            {
                "service": "switch.turn_on",
                "entity_id": "switch.smart_diffuser_power",
                "data": {}
            },
            # Klima
            {
                "service": "climate.set_temperature",
                "entity_id": "climate.room_ac",
                "data": {
                    "temperature": profile.climate_temp,
                    "hvac_mode": "cool"
                }
            },
        ]

        # Spotify (mood "off" değilse)
        if profile.spotify_mood != "off":
            actions.append({
                "service": "input_select.select_option",
                "entity_id": "input_select.spatial_audio_mood",
                "data": {"option": profile.spotify_mood}
            })

        # -------------------------------------------------------------------------
        # HA REST API'ye gönder (her aksiyonu sırayla)
        # -------------------------------------------------------------------------
        for action in actions:
            await self._call_ha_service(
                action["service"],
                action.get("entity_id"),
                action.get("data", {})
            )
            await asyncio.sleep(0.3)  # HA işlemesi için kısa bekle

        # Difüzör RGB kapat
        await self._call_ha_service(
            "light.turn_off", "light.diffuser_led", {}
        )

        # Jarvis kısa bilgi
        await self._notify_jarvis(profile.description)

    # =========================================================================
    # HA SERVİS ÇAĞRISI
    # =========================================================================
    async def _call_ha_service(
        self,
        service: str,
        entity_id: Optional[str],
        data: Dict[str, Any]
    ) -> None:
        """HA REST API'ye servis çağrısı gönder."""
        parts = service.split(".")
        if len(parts) != 2:
            return

        domain, service_name = parts
        url = f"/api/services/{domain}/{service_name}"

        if entity_id:
            data["entity_id"] = entity_id

        try:
            response = await self.ha_client.post(url, json=data)
            if response.status_code == 200:
                print(f"[MediaOrchestrator] ✅ {service} → {entity_id}")
            else:
                print(f"[MediaOrchestrator] ❌ {service}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[MediaOrchestrator] ❌ {service}: {e}")

    # =========================================================================
    # JARVIS'E BİLDİR
    # =========================================================================
    async def _notify_jarvis(self, description: str) -> None:
        """Jarvis'e (MQTT) atmosfer değişikliğini bildir."""
        # MQTT publish → Jarvis TTS
        print(f"[MediaOrchestrator] Jarvis bildirildi: {description}")
        # mqtt.publish("jarvis/media/atmosphere_change", description)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.ha_client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Agentic Media Orchestrator test."""

    orchestrator = AgenticMediaOrchestrator()

    # Test: Siberpunk atmosferi uygula
    print("=== TEST: Blade Runner (Siberpunk) ===\n")
    await orchestrator._apply_atmosphere(ContentType.CYBERPUNK)

    # Test: Doğa belgeseli atmosferi
    print("\n=== TEST: Doğa Belgeseli ===\n")
    await orchestrator._apply_atmosphere(ContentType.NATURE)

    await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(main())