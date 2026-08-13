"""
=============================================================================
openclaw_digital_sandbox — Mealie Recipe Hunter
=============================================================================
Modül 27: OpenClaw Digital Hands — Otonom Tarif Avcısı

OpenClaw'un tarif bulma, doğrulama ve Mealie'ye kaydetme workflow'sunun
Python implementasyonu. Browser MCP + Context7 MCP + Mealie API + MQTT.

🎯 AKIŞ:
   1. Browser MCP → 10+ kaynak tara, tarif URL'leri topla
   2. Context7 MCP → her tarifin makro/besin doğruluğunu sorgula
   3. Mealie API → doğrulanan tarifleri veritabanına POST et
   4. MQTT → Lamba (Modül 29) başını salla + yeşil ışık
   5. MiniMax → kısa sesli özet

🔒 ZERO TRUST:
   - Sadece Mealie POST /api/recipes/create/url izni var
   - DELETE/PUT yasak (mevcut tarifleri silemez)
   - Login/ödeme adımları yasak
   - Ekranda pencere açma YASAK (görünmez çalış)

🔗 MODÜL BAĞLANTILARI:
   Modül 28 (Mealie) → tarif kaydı
   Modül 29 (Lamba) → fiziksel onay (nod + green)
   jarvis_core (DeepSeek) → makro doğrulama
   jarvis_core (MiniMax) → sesli özet

=============================================================================
"""

import os
import re
import json
import asyncio
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import httpx
import paho.mqtt.client as mqtt

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# LOGGING — Sadece sistem log'una, ekrana YAZMA
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [OpenClaw Recipe Hunter] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("recipe_hunter")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class HunterConfig:
    """Tarif avcısı konfigürasyonu."""

    # Mealie API
    MEALIE_URL: str = os.getenv("MEALIE_URL", "http://localhost:9925")
    MEALIE_USER: str = os.getenv("MEALIE_USER", "jarvis@local")
    MEALIE_PASSWORD: str = os.getenv("MEALIE_PASSWORD", "changeme")

    # DeepSeek (makro doğrulama)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # MQTT (Lamba'ya sinyal)
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "gl-mt3000.local")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

    # HA REST API (MiniMax sesli bildirim)
    HA_URL: str = os.getenv("HA_URL", "http://homeassistant.local:8123")
    HA_TOKEN: str = os.getenv("HA_TOKEN", "")

    # Sporcu hedefleri
    ATHLETE_WEIGHT_KG: float = float(os.getenv("ATHLETE_WEIGHT_KG", "125"))
    MIN_PROTEIN_PER_SERVING: float = 25.0  # g protein minimum
    MAX_RECIPES_TO_HUNT: int = 10  # bir seferde max tarif
    MAX_RECIPES_TO_IMPORT: int = 20  # Mealie'ye max kayıt


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

@dataclass
class RecipeCandidate:
    """Tarif adayı (Browser'dan bulunan)."""
    url: str
    title: str = ""
    source: str = ""
    protein_g: Optional[float] = None
    calories: Optional[int] = None
    verified: bool = False
    rejection_reason: str = ""


@dataclass
class HuntResult:
    """Tarif avı sonucu."""
    concept: str
    total_found: int = 0
    total_verified: int = 0
    total_imported: int = 0
    rejected: List[str] = field(default_factory=list)
    imported_slugs: List[str] = field(default_factory=list)
    duration_sec: float = 0.0


# =============================================================================
# MEALIE RECIPE HUNTER
# =============================================================================

class MealieRecipeHunter:
    """
    OpenClaw'un otonom tarif avcısı.

    Browser MCP → Context7 MCP → Mealie API → MQTT (Lamba)
    """

    # Yasak siteler (clickbait, login, ödeme)
    BLOCKED_DOMAINS = [
        "facebook.com",
        "instagram.com",
        "pinterest.com",
        "tiktok.com",
    ]

    def __init__(self, config: HunterConfig = None):
        self.config = config or HunterConfig()
        self._mealie_token: Optional[str] = None
        self._mqtt: Optional[mqtt.Client] = None
        self._http = httpx.AsyncClient(timeout=30.0)

    # =========================================================================
    # ADIM 1: BROWSER MCP — TARİF ARA
    # =========================================================================

    async def hunt_recipes(self, concept: str, count: int = 10) -> List[RecipeCandidate]:
        """
        Browser MCP kullanarak internetten tarif ara.
        Gerçek implementasyonda Browser MCP aracı çağrılır.
        Burada simüle edilmiş akış var.
        """
        log.info(f"Ararma başlatıldı: '{concept}' (hedef: {count} tarif)")

        # Gerçek implementasyonda:
        # 1. Browser MCP → Google'da "high protein {concept} recipe" ara
        # 2. İlk 20 sonucu tara
        # 3. Schema.org/Recipe içeren sayfaları seç
        # 4. Yasak domain'leri ele

        search_queries = [
            f"high protein {concept} recipe",
            f"sporcu {concept} tarif",
            f"athlete {concept} meal prep",
            f"protein rich {concept} healthy",
        ]

        candidates: List[RecipeCandidate] = []

        # Simüle edilmiş sonuçlar (gerçek Browser MCP çağrısı ile değiştir)
        simulated_sources = [
            ("allrecipes.com", "High Protein Chicken Bowl", 35, 450),
            ("seriouseats.com", "Grilled Salmon with Quinoa", 40, 520),
            ("eatingwell.com", "Turkey Vegetable Stir Fry", 32, 380),
            ("bbcgoodfood.com", "Beef and Broccoli", 38, 490),
            ("nefisyemektarifleri.com", "Yüksek Proteinli Tavuk Yemeği", 30, 420),
            ("healthline.com", "Greek Yogurt Protein Bowl", 28, 350),
            ("yemek.com", "Izgara Somon ve Sebze", 42, 540),
            ("allrecipes.com", "Diet Chocolate Cake", 5, 800),  # Reddedilecek
            ("eatingwell.com", "Lentil Protein Soup", 22, 300),
            ("seriouseats.com", "Steak and Sweet Potato", 45, 620),
        ]

        for source_domain, title, protein, calories in simulated_sources[:count]:
            url = f"https://www.{source_domain}/recipe/{title.lower().replace(' ', '-')}"

            # Yasak domain kontrolü
            if any(blocked in url for blocked in self.BLOCKED_DOMAINS):
                log.warning(f"Yasak site atlandı: {url}")
                continue

            candidate = RecipeCandidate(
                url=url,
                title=title,
                source=source_domain,
                protein_g=float(protein),
                calories=calories,
            )
            candidates.append(candidate)
            log.info(f"[Browser] Aday: {title} ({source_domain}, {protein}g protein)")

        log.info(f"Toplam {len(candidates)} tarif adayı bulundu")
        return candidates

    # =========================================================================
    # ADIM 2: CONTEXT7 MCP — DOĞRULAMA
    # =========================================================================

    async def verify_recipe(self, candidate: RecipeCandidate) -> bool:
        """
        Context7 MCP ile tarifin doğruluğunu sorgula.
        Protein oranı, malzeme kalitesi, makro gerçekçiliği.
        """
        # Hızlı kontrol: minimum protein
        if candidate.protein_g and candidate.protein_g < self.config.MIN_PROTEIN_PER_SERVING:
            candidate.rejection_reason = (
                f"Düşük protein ({candidate.protein_g}g < "
                f"{self.config.MIN_PROTEIN_PER_SERVING}g minimum)"
            )
            log.warning(f"❌ {candidate.title}: {candidate.rejection_reason}")
            return False

        # DeepSeek ile derin doğrulama
        prompt = (
            f"Bir sporcu tarifini doğrula. Kullanıcı {self.config.ATHLETE_WEIGHT_KG}kg, "
            f"sporcu. Tarif: {candidate.title} ({candidate.source}). "
            f"İddia edilen protein: {candidate.protein_g}g, kalori: {candidate.calories}. "
            f"Bu değerler gerçekçi mi? Sentetik malzeme var mı? "
            f"SADECE 'EVET' veya 'HAYIR' + kısa neden döndür."
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            body = {
                "model": self.config.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 100,
            }
            resp = await self._http.post(
                self.config.DEEPSEEK_URL, headers=headers, json=body
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].upper()

            if "EVET" in content or "YES" in content:
                candidate.verified = True
                log.info(f"✅ {candidate.title}: Doğrulandı")
                return True
            else:
                candidate.rejection_reason = f"Context7/DeepSeek reddi: {content[:80]}"
                log.warning(f"❌ {candidate.title}: {candidate.rejection_reason}")
                return False
        except Exception as e:
            log.error(f"Doğrulama hatası ({candidate.title}): {e}")
            # Hata durumunda protein kontrolü yeterli sayılır
            if candidate.protein_g and candidate.protein_g >= self.config.MIN_PROTEIN_PER_SERVING:
                candidate.verified = True
                return True
            return False

    async def verify_all(self, candidates: List[RecipeCandidate]) -> List[RecipeCandidate]:
        """Tüm adayları doğrula, sadece geçenleri döndür."""
        log.info(f"Doğrulama başlıyor ({len(candidates)} tarif)...")
        verified: List[RecipeCandidate] = []

        for candidate in candidates:
            if await self.verify_recipe(candidate):
                verified.append(candidate)

        log.info(f"Doğrulama tamam: {len(verified)}/{len(candidates)} geçti")
        return verified

    # =========================================================================
    # ADIM 3: MEALIE API — KAYIT
    # =========================================================================

    async def authenticate_mealie(self) -> bool:
        """Mealie'ye giriş yap, bearer token al."""
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": self.config.MEALIE_USER,
            "password": self.config.MEALIE_PASSWORD,
            "grant_type": "",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }
        try:
            resp = await self._http.post(
                f"{self.config.MEALIE_URL}/api/auth/token",
                headers=headers,
                data=data,
            )
            resp.raise_for_status()
            self._mealie_token = resp.json().get("access_token")
            log.info("Mealie auth başarılı")
            return True
        except Exception as e:
            log.error(f"Mealie auth hatası: {e}")
            return False

    async def import_to_mealie(self, candidate: RecipeCandidate) -> Optional[str]:
        """
        Doğrulanan tarif URL'sini Mealie'ye POST et.
        Sadece POST /api/recipes/create/url izni var (Zero Trust).
        """
        if not self._mealie_token:
            await self.authenticate_mealie()

        headers = {
            "Authorization": f"Bearer {self._mealie_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"url": candidate.url}

        try:
            resp = await self._http.post(
                f"{self.config.MEALIE_URL}/api/recipes/create/url",
                headers=headers,
                json=data,
            )
            if resp.status_code == 201:
                slug = resp.text.strip('"')
                log.info(f"[Mealie] ✅ Kaydedildi: {candidate.title} → slug: {slug}")
                return slug
            else:
                log.error(f"[Mealie] ❌ Kayıt hatası: {resp.status_code}")
                return None
        except Exception as e:
            log.error(f"[Mealie] ❌ Exception: {e}")
            return None

    async def import_all(
        self, candidates: List[RecipeCandidate]
    ) -> List[str]:
        """Tüm doğrulanan tarifleri Mealie'ye kaydet."""
        log.info(f"Mealie'ye kayıt başlıyor ({len(candidates)} tarif)...")

        # Zero Trust: max kayıt limiti
        if len(candidates) > self.config.MAX_RECIPES_TO_IMPORT:
            log.warning(
                f"Limit aşımı: {len(candidates)} > "
                f"{self.config.MAX_RECIPES_TO_IMPORT} max. İlk "
                f"{self.config.MAX_RECIPES_TO_IMPORT} kaydedilecek."
            )
            candidates = candidates[: self.config.MAX_RECIPES_TO_IMPORT]

        imported_slugs: List[str] = []
        for candidate in candidates:
            slug = await self.import_to_mealie(candidate)
            if slug:
                imported_slugs.append(slug)

        log.info(f"Kayıt tamam: {len(imported_slugs)}/{len(candidates)} başarılı")
        return imported_slugs

    # =========================================================================
    # ADIM 4: MQTT — LAMBA FİZİKSEL ONAY
    # =========================================================================

    def _connect_mqtt(self) -> None:
        """Yerel MQTT broker'a bağlan."""
        self._mqtt = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="openclaw-recipe-hunter",
        )
        self._mqtt.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self._mqtt.loop_start()

    def signal_lamp_done(self) -> None:
        """Lamba'ya 'Görev Tamamlandı' sinyali gönder (nod + green)."""
        if not self._mqtt:
            self._connect_mqtt()

        payload = json.dumps({
            "action": "nod",
            "color": "green",
            "brightness": 50,
        })
        self._mqtt.publish("jarvis/lamp/motion/command", payload)
        log.info("[MQTT] Lamba'ya sinyal: nod + green")

    def signal_lamp_error(self) -> None:
        """Lamba'ya 'Hata' sinyali gönder (shake + red)."""
        if not self._mqtt:
            self._connect_mqtt()

        payload = json.dumps({
            "action": "shake",
            "color": "red",
            "brightness": 60,
        })
        self._mqtt.publish("jarvis/lamp/motion/command", payload)
        log.info("[MQTT] Lamba'ya sinyal: shake + red")

    # =========================================================================
    # ADIM 5: MINIMAX — SESLİ ÖZET
    # =========================================================================

    async def notify_user(self, result: HuntResult) -> None:
        """Kullanıcıya kısa sesli özet gönder (MiniMax üzerinden HA)."""
        message = (
            f"Tarif araması tamamlandı efendim. "
            f"{result.total_found} tarif bulundu, "
            f"{result.total_verified} tanesi doğrulandı, "
            f"{result.total_imported} tanesi kütüphanenize kaydedildi."
        )

        headers = {
            "Authorization": f"Bearer {self.config.HA_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {"message": message}

        try:
            await self._http.post(
                f"{self.config.HA_URL}/api/services/tts/speak",
                headers=headers,
                json=data,
            )
            log.info(f"[MiniMax] Sesli özet: {message}")
        except Exception as e:
            log.error(f"[MiniMax] Bildirim hatası: {e}")

    # =========================================================================
    # TAM WORKFLOW — OTONOM TARİF AVI
    # =========================================================================

    async def run_hunt(self, concept: str) -> HuntResult:
        """
        Tam otonom tarif avı workflow'u:
        1. Browser MCP → tarif ara
        2. Context7 MCP → doğrula
        3. Mealie API → kaydet
        4. MQTT → Lamba'ya sinyal
        5. MiniMax → sesli özet
        """
        start_time = datetime.now()
        log.info(f"{'='*60}")
        log.info(f"Tarif avı başlatıldı: '{concept}'")
        log.info(f"{'='*60}")

        result = HuntResult(concept=concept)

        # ADIM 1: Browser MCP — Ara
        candidates = await self.hunt_recipes(concept, self.config.MAX_RECIPES_TO_HUNT)
        result.total_found = len(candidates)

        if not candidates:
            log.warning("Tarif bulunamadı!")
            self.signal_lamp_error()
            return result

        # ADIM 2: Context7 MCP — Doğrula
        verified = await self.verify_all(candidates)
        result.total_verified = len(verified)
        result.rejected = [c.title for c in candidates if not c.verified]

        if not verified:
            log.warning("Hiçbir tarif doğrulanamadı!")
            self.signal_lamp_error()
            return result

        # ADIM 3: Mealie API — Kaydet
        imported_slugs = await self.import_all(verified)
        result.total_imported = len(imported_slugs)
        result.imported_slugs = imported_slugs

        # ADIM 4: MQTT — Lamba'ya sinyal
        if result.total_imported > 0:
            self.signal_lamp_done()
        else:
            self.signal_lamp_error()

        # ADIM 5: MiniMax — Sesli özet
        await self.notify_user(result)

        result.duration_sec = (datetime.now() - start_time).total_seconds()
        log.info(f"{'='*60}")
        log.info(
            f"Tamamlandı: {result.total_found} bulundu, "
            f"{result.total_verified} doğrulandı, "
            f"{result.total_imported} kaydedildi "
            f"({result.duration_sec:.1f}sn)"
        )
        log.info(f"{'='*60}")

        return result

    # =========================================================================
    # CLEANUP
    # =========================================================================

    async def close(self) -> None:
        """Kaynakları temizle."""
        await self._http.aclose()
        if self._mqtt:
            self._mqtt.loop_stop()
            self._mqtt.disconnect()


# =============================================================================
# ANA PROGRAM
# =============================================================================

async def main():
    """Demo: Otonom tarif avı."""
    hunter = MealieRecipeHunter()

    # "Bana tarif bul" → "Ege usulü yüksek protein"
    result = await hunter.run_hunt("Ege usulü yüksek protein")

    print(f"\nSonuç: {result.total_found} bulundu, "
          f"{result.total_verified} doğrulandı, "
          f"{result.total_imported} kaydedildi")

    await hunter.close()


if __name__ == "__main__":
    asyncio.run(main())