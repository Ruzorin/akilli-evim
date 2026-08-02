"""
 =============================================================================
 jarvis_core 3.0 — Agentic Home Assistant API (Kendi Kendini Kodlayan Oda)
 =============================================================================
 2026 Sürümü — Statik intent'ler YOK. GPT-5.6 HA REST API'yi doğrudan manipüle eder.

 Bu modül, GPT-5.6'ya Home Assistant'ın TAM REST API kontrolünü verir.
 Artık "önceden yazılmış komutlara" ihtiyaç YOK.

 🤖 "AGENTIC" MANTIK — NEDEN DEVRİMCİ?
 =============================================================================
 Eski sistem (v1/v2):
   Kullanıcı: "Işıkları kırmızı yap"
   HA: input_select → script → light.turn_on (ÖNCEDEN YAZILMIŞ)

 Yeni sistem (v3.0 Agentic):
   Kullanıcı: "Bize cyberpunk bir ortam yap"
   GPT-5.6: [DÜŞÜNÜR] → "Cyberpunk = neon mor/yeşil, karanlık, synthwave"
   GPT-5.6: [KOD ÜRETİR] → WLED JSON: {"rgb_color": [128, 0, 255], "brightness": 180}
   GPT-5.6: [API ÇAĞIRIR] → POST /api/services/light/turn_on
   GPT-5.6: [MÜZİK BULUR] → Spotify search "synthwave" → play
   GPT-5.6: [KLİMA AYARLAR] → POST /api/services/climate/set_temperature (18°C)
   GPT-5.6: "Cyberpunk modu aktif, efendim." (KISA cevap)

 FARK:
   Eski: Sistem sadece "önceden tanımlı" komutları anlar
   Yeni: Sistem "herhangi" soyut komutu anlar ve KENDİSİ eylem planlar

 Bu, "statik otomasyon" → "yaşayan zihin" dönüşümüdür.
 GPT-5.6, HA'ı bir yazılım geliştiricisi gibi manipüle eder.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio

 =============================================================================
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class AgenticHAConfig:
    """Agentic HA API konfigürasyonu."""

    # Home Assistant REST API
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # Spotify API (müzik arama için)
    SPOTIFY_CLIENT_ID: str = "YOUR_SPOTIFY_CLIENT_ID"
    SPOTIFY_CLIENT_SECRET: str = "YOUR_SPOTIFY_CLIENT_SECRET"

    # Güvenlik — izin verilen servisler
    ALLOWED_SERVICES: List[str] = [
        "light.turn_on", "light.turn_off",
        "switch.turn_on", "switch.turn_off",
        "climate.set_temperature", "climate.set_fan_mode",
        "media_player.play_media", "media_player.volume_set",
        "cover.set_cover_position",
        "input_boolean.turn_on", "input_boolean.turn_off",
        "input_select.select_option",
        "script.turn_on",
    ]

    # Yasaklı servisler (güvenlik)
    BLOCKED_SERVICES: List[str] = [
        "homeassistant.restart",
        "homeassistant.stop",
        "config.entry_reload",
    ]


# =============================================================================
# AGENTIC HOME ASSISTANT API
# =============================================================================

class AgenticHomeAssistantAPI:
    """
    GPT-5.6'ya Home Assistant REST API'sini doğrudan kullanma yetkisi verir.

    🤖 NASIL ÇALIŞIR?
    =============================================================================
    1. GPT-5.6, kullanıcı komutunu alır (örn: "Bize cyberpunk ortamı yap")
    2. GPT-5.6, "HA_ACTIONS:" etiketiyle JSON kod bloğu üretir:
       HA_ACTION:
       [
         {"service": "light.turn_on", "entity_id": "light.wled_ambient",
          "data": {"rgb_color": [128, 0, 255], "brightness": 180}},
         {"service": "media_player.play_media", "entity_id": "media_player.spotify",
          "data": {"media_content_type": "playlist",
           "media_content_id": "spotify:search:synthwave"}},
         {"service": "climate.set_temperature", "entity_id": "climate.room_ac",
          "data": {"temperature": 18, "hvac_mode": "cool"}}
       ]
    3. Bu sınıf, JSON'u parse eder
    4. Her aksiyonu HA REST API'ye gönderir (async)
    5. Sonucu GPT-5.6'a döndürür
    6. GPT-5.6, kullanıcıya KISA cevap verir

    🚨 GÜVENLİK:
    - Sadece ALLOWED_SERVICES listesindeki servisler çağrılabilir
    - BLOCKED_SERVICES (restart, stop) ASLA çağrılamaz
    - Her aksiyon loglanır (audit trail)
    - Maksimum 10 aksiyon/komut (sonsuz döngü önleme)
    """

    def __init__(self, config: AgenticHAConfig = None):
        self.config = config or AgenticHAConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={
                "Authorization": f"Bearer {self.config.HA_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        print("[AgenticHA] Home Assistant Agentic API başlatıldı")

    # =========================================================================
    # ANA FONKSİYON: Agentic Aksiyon Çalıştır
    # =========================================================================
    async def execute_agentic_action(
        self,
        model_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        GPT-5.6'nın ürettiği HA_ACTION JSON bloğunu parse edip HA'a gönderir.

        Bu, "kendi kendini kodlayan oda"nın kalbidir. GPT-5.6:
        1. Soyut komutu alır ("cyberpunk ortamı")
        2. Hangi cihazların nasıl ayarlanacağını KENDİSİ DÜŞÜNÜR
        3. HA REST API çağrılarını KENDİSİ ÜRETİR
        4. Bu fonksiyon onları ÇALIŞTIRIR

        Args:
            model_response: GPT-5.6'nın cevabı (HA_ACTION: [...] içerir)
            context: Bağlam (aktif modüller, sensör verisi)

        Returns:
            Jarvis'in kullanıcıya verdiği cevap (KISA)
        """
        # HA_ACTION bloğunu parse et
        actions = self._parse_ha_actions(model_response)

        if not actions:
            # HA aksiyonu yok → model cevabını direkt döndür
            return model_response.replace("HA_ACTION:", "").strip()

        print(f"[AgenticHA] {len(actions)} agentic aksiyon tespit edildi")

        # Güvenlik kontrolü
        validated = self._validate_actions(actions)
        if not validated:
            return "Efendim, bu aksiyonları gerçekleştiremiyorum. Güvenlik protokolü."

        # Aksiyonları sırayla çalıştır (async)
        results = []
        for i, action in enumerate(validated):
            print(f"[AgenticHA] Aksiyon {i+1}/{len(validated)}: {action['service']} → {action.get('entity_id', '?')}")
            result = await self._call_ha_service(
                action["service"],
                action.get("entity_id"),
                action.get("data", {})
            )
            results.append(result)
            # Aksiyonlar arası kısa bekleme (HA işlemesi için)
            await asyncio.sleep(0.3)

        # Başarı özeti
        success_count = sum(1 for r in results if r["success"])
        print(f"[AgenticHA] {success_count}/{len(results)} aksiyon başarılı")

        # Modelin metin cevabını döndür (HA_ACTION bloğu hariç)
        text_response = model_response.split("HA_ACTION:")[0].strip()
        if not text_response:
            text_response = "Elbette, efendim."

        return text_response

    # =========================================================================
    # HA_ACTION BLOĞUNU PARSE ET
    # =========================================================================
    def _parse_ha_actions(self, response: str) -> List[Dict]:
        """
        GPT-5.6'nın cevabından HA_ACTION JSON bloğunu çıkar.

        GPT-5.6 şu formatta cevap üretir:
        "Cyberpunk modu aktif, efendim.
         HA_ACTION:
         [
           {"service": "light.turn_on", "entity_id": "light.wled_ambient",
            "data": {"rgb_color": [128, 0, 255], "brightness": 180}},
           ...
         ]"

        Bu fonksiyon, JSON kısmını parse eder ve liste döndürür.
        """
        if "HA_ACTION:" not in response:
            return []

        # HA_ACTION: sonrasını al
        action_part = response.split("HA_ACTION:")[1].strip()

        # JSON array'i parse et
        try:
            # JSON bloğunu bul (ilk [ ile son ] arası)
            start = action_part.find("[")
            end = action_part.rfind("]") + 1
            if start == -1 or end == 0:
                return []

            json_str = action_part[start:end]
            actions = json.loads(json_str)
            return actions

        except json.JSONDecodeError as e:
            print(f"[AgenticHA] JSON parse hatası: {e}")
            return []

    # =========================================================================
    # GÜVENLİK VALIDASYONU
    # =========================================================================
    def _validate_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Aksiyonları güvenlik açısından kontrol et.

        🚨 GÜVENLİK KURALLARI:
        1. Sadece ALLOWED_SERVICES listesindeki servisler
        2. BLOCKED_SERVICES (restart, stop) ASLA
        3. Maksimum 10 aksiyon (sonsuz döngü önleme)
        4. Her aksiyon loglanır
        """
        validated = []

        for action in actions[:10]:  # Maks 10 aksiyon
            service = action.get("service", "")

            # Yasaklı servis kontrolü
            if service in self.config.BLOCKED_SERVICES:
                print(f"[AgenticHA] ⛔ YASAKLI servis engellendi: {service}")
                continue

            # İzinli servis kontrolü
            if service not in self.config.ALLOWED_SERVICES:
                print(f"[AgenticHA] ⚠️ İzin verilmeyen servis: {service}")
                continue

            validated.append(action)
            print(f"[AgenticHA] ✅ Onaylandı: {service}")

        return validated

    # =========================================================================
    # HA REST API ÇAĞRISI
    # =========================================================================
    async def _call_ha_service(
        self,
        service: str,
        entity_id: Optional[str],
        data: Dict[str, Any]
    ) -> Dict:
        """
        Home Assistant REST API'ye servis çağrısı gönder.

        🤖 BU, GPT-5.6'NIN HA'I MANİPÜLE ETTİĞİ NOKTADIR:
        GPT-5.6, "önceden yazılmış komutlara" ihtiyaç duymadan,
        doğrudan HA REST API'ye istek gönderir. Bu, "statik otomasyon"
        → "yaşayan zihin" dönüşümüdür.

        HA REST API formatı:
        POST /api/services/{domain}/{service}
        Body: {"entity_id": "...", "rgb_color": [...], ...}
        """
        # Servisi domain/service olarak böl (örn: light.turn_on → light/turn_on)
        parts = service.split(".")
        if len(parts) != 2:
            return {"success": False, "error": f"Invalid service: {service}"}

        domain, service_name = parts
        url = f"/api/services/{domain}/{service_name}"

        # Entity ID'yi data'ya ekle
        if entity_id:
            data["entity_id"] = entity_id

        try:
            response = await self.client.post(url, json=data)
            if response.status_code == 200:
                print(f"[AgenticHA] ✅ {service} → {entity_id}: Başarılı")
                return {"success": True, "service": service, "entity_id": entity_id}
            else:
                print(f"[AgenticHA] ❌ {service}: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"[AgenticHA] ❌ {service}: {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # HA STATE SORGULAMA (GPT-5.6 için)
    # =========================================================================
    async def get_ha_state(self, entity_id: str) -> Optional[Dict]:
        """
        Bir HA entity'sinin mevcut durumunu sorgula.

        GPT-5.6, aksiyon almadan önce "odada ne oluyor?" sorusunu
        bu fonksiyonla yanıtlar. Örnek:
        - get_ha_state("sensor.bed_activity_level") → 45
        - get_ha_state("climate.room_ac") → 22°C, cool
        """
        try:
            response = await self.client.get(f"/api/states/{entity_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[AgenticHA] State sorgu hatası: {e}")
            return None

    # =========================================================================
    # HA SERVİS LİSTESİ (GPT-5.6 için tool tanımı)
    # =========================================================================
    async def list_available_services(self) -> List[str]:
        """
        HA'da kullanılabilir tüm servisleri listele.

        GPT-5.6, bu listeyi alıp "hangi servis hangi işe yarar" bilgisini
        system prompt'undan çıkararak dinamik aksiyon planlar.
        """
        try:
            response = await self.client.get("/api/services")
            if response.status_code == 200:
                services = response.json()
                return [s["service"] for s in services]
            return []
        except Exception:
            return []

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        """HTTP client'ı kapat."""
        await self.client.close()


# =============================================================================
# GPT-5.6 TOOL TANIMLARI (Agentic Framework için)
# =============================================================================
# Bu tool tanımları, GPT-5.6'ya "HA'ı nasıl manipüle edeceğini" söyler.
# GPT-5.6, bu tool'ları kullanarak dinamik aksiyon planlar.

HA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "ha_call_service",
            "description": """
                Home Assistant servisini çağır. Bu, oda içindeki herhangi bir
                cihazı kontrol etmeni sağlar. Soyut komutları (örn: 'cyberpunk
                ortamı') somut HA aksiyonlarına çevir.

                Örnek: Kullanıcı 'cyberpunk ortamı' istiyorsa:
                1. WLED'i neon mor yap: light.turn_on, rgb_color [128, 0, 255]
                2. Spotify'dan synthwave çal: media_player.play_media
                3. Klimayı serin yap: climate.set_temperature, 18°C
                4. Işıkları kapat: light.turn_off

                KENDİ KARARINI VER — önceden tanımlı komut bekleme.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "HA servis adı (örn: light.turn_on, climate.set_temperature)"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "HA entity ID (örn: light.wled_ambient, climate.room_ac)"
                    },
                    "data": {
                        "type": "object",
                        "description": "Servis parametreleri (rgb_color, brightness, temperature, vb.)"
                    }
                },
                "required": ["service"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ha_get_state",
            "description": """
                Bir HA entity'sinin mevcut durumunu sorgula.
                Aksiyon almadan önce oda durumunu kontrol etmek için kullan.
                Örnek: 'Oda sıcak mı?' → ha_get_state('climate.room_ac')
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Sorgulanacak entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        }
    }
]


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Agentic HA API test."""

    api = AgenticHomeAssistantAPI()

    # Test: GPT-5.6'nın ürettiği bir "cyberpunk" aksiyon bloğu
    mock_gpt_response = """
    Cyberpunk modu aktif, efendim.

    HA_ACTION:
    [
        {"service": "light.turn_on", "entity_id": "light.wled_ambient",
         "data": {"rgb_color": [128, 0, 255], "brightness": 180, "effect": "Breathe"}},
        {"service": "light.turn_off", "entity_id": "light.ceiling_light",
         "data": {}},
        {"service": "climate.set_temperature", "entity_id": "climate.room_ac",
         "data": {"temperature": 18, "hvac_mode": "cool"}},
        {"service": "media_player.play_media", "entity_id": "media_player.spotify",
         "data": {"media_content_type": "playlist", "media_content_id": "spotify:playlist:37i9dQZF1DX4PP3DA4J0N8"}}
    ]
    """

    print("=== TEST: Cyberpunk ortamı (Agentic) ===\n")
    result = await api.execute_agentic_action(mock_gpt_response)
    print(f"\nJarvis: {result}")

    await api.close()


if __name__ == "__main__":
    asyncio.run(main())