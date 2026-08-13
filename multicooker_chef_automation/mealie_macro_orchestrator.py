"""
=============================================================================
multicooker_chef_automation — Mealie Macro Orchestrator
=============================================================================
Modül 28: Multicooker Chef Automation — Mealie entegrasyonu

Mealie (açık kaynak tarif yöneticisi) + DeepSeek (makro hesabı) +
Xiaomi/Tuya Akıllı Tencere (yerel izole) = Thermomix/Cookidoo rakibi

🎯 MİMARİ:
   Kullanıcı URL yapıştırır → Mealie scrape → tarif veritabanına kaydeder
   DeepSeek → sporcu hedeflerine göre porsiyon/makro hesaplar
   Mealie API → tarif'i dinamik ölçekler (servings, nutrition)
   MQTT → HA → Akıllı Tencere'ye pişirme komutu gönderir

🔗 MEALIE REST API (FastAPI + Swagger):
   POST   /api/auth/token              → Bearer token al
   POST   /api/recipes/create/url      → URL'den tarif scrape et
   GET    /api/recipes/{slug}           → Tarif detayı (malzeme, talimat, besin)
   PUT    /api/recipes/{slug}           → Tarif güncelle (porsiyon ölçekle)
   GET    /api/recipes                  → Tarif ara/listele
   POST   /api/households/mealplans     → Yemek planı oluştur
   POST   /api/parser/ingredients       → Malzeme parse (nlp/brute/openai)

🔗 MODÜL BAĞLANTILARI:
   Modül 13 (Vision Chef — Qwen-VL Max) → Tezgah malzemelerini görür
   Modül 10 (WLED) → VSS dostu pişirme bildirimi
   Modül 29 (Lamba) → Fiziksel onay (başını sallar)
   jarvis_core (DeepSeek V4-Pro) → Makro/porsiyon hesabı
   jarvis_core (MiniMax Speech 2.8 Turbo) → Sesli bildirim

=============================================================================
"""

import os
import re
import json
import asyncio
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

import httpx
import paho.mqtt.client as mqtt

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class MealieConfig:
    """Mealie + Multicooker konfigürasyonu."""

    # Mealie (Docker — yerel)
    MEALIE_URL: str = os.getenv("MEALIE_URL", "http://localhost:9925")
    MEALIE_USER: str = os.getenv("MEALIE_USER", "jarvis@local")
    MEALIE_PASSWORD: str = os.getenv("MEALIE_PASSWORD", "changeme")

    # DeepSeek (makro hesabı)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # HA REST API
    HA_URL: str = os.getenv("HA_URL", "http://homeassistant.local:8123")
    HA_TOKEN: str = os.getenv("HA_TOKEN", "")

    # MQTT (yerel broker)
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "gl-mt3000.local")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

    # Sporcu hedefleri (kullanıcıya göre ayarlanır)
    ATHLETE_WEIGHT_KG: float = float(os.getenv("ATHLETE_WEIGHT_KG", "85"))
    ATHLETE_GOAL: str = os.getenv("ATHLETE_GOAL", "maintenance")  # bulk/cut/maintenance
    PROTEIN_PER_KG: float = 2.0  # g protein per kg bodyweight
    CALORIES_TARGET: int = 2800


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

class AthleteGoal(Enum):
    BULK = "bulk"
    CUT = "cut"
    MAINTENANCE = "maintenance"


@dataclass
class MacroTargets:
    """Sporcu makro hedefleri (gün içinde)."""
    calories: int = 2800
    protein_g: float = 170.0
    carbs_g: float = 350.0
    fat_g: float = 90.0

    @property
    def protein_per_meal(self) -> float:
        """4 öğüne bölünmüş protein."""
        return self.protein_g / 4


@dataclass
class MealieRecipe:
    """Mealie'den gelen tarif verisi."""
    slug: str = ""
    name: str = ""
    description: str = ""
    servings: int = 4
    ingredients: List[Dict] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    nutrition: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    image_url: str = ""

    @property
    def calories_per_serving(self) -> Optional[float]:
        n = self.nutrition
        if n and "calories" in n:
            try:
                return float(re.sub(r"[^\d.]", "", str(n["calories"])))
            except (ValueError, TypeError):
                pass
        return None


@dataclass
class ScaledRecipe:
    """Ölçeklenmiş tarif — pişirme komutu için."""
    recipe: MealieRecipe
    scaled_servings: int
    scaled_ingredients: List[Dict]
    scaled_nutrition: Dict
    cooking_profile: Dict  # multicooker'a gönderilecek


# =============================================================================
# MEALIE MACRO ORCHESTRATOR
# =============================================================================

class MealieMacroOrchestrator:
    """
    Mealie tarif yöneticisi + DeepSeek makro orkestrasyonu.

    Akış:
    1. Kullanıcı URL yapıştırır → Mealie scrape → veritabanına kaydeder
    2. DeepSeek → sporcu hedeflerine göre porsiyon/makro hesaplar
    3. Mealie API → tarif'i dinamik ölçekler
    4. MQTT → HA → Akıllı Tencere'ye pişirme komutu gönderir
    """

    def __init__(self, config: MealieConfig = None):
        self.config = config or MealieConfig()
        self._mealie_token: Optional[str] = None
        self._mqtt: Optional[mqtt.Client] = None
        self._http = httpx.AsyncClient(timeout=30.0)

    # =========================================================================
    # MEALIE REST API
    # =========================================================================

    async def authenticate_mealie(self) -> bool:
        """Mealie'ye giriş yap, bearer token al."""
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "",
            "username": self.config.MEALIE_USER,
            "password": self.config.MEALIE_PASSWORD,
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
            token_data = resp.json()
            self._mealie_token = token_data.get("access_token")
            print(f"[Mealie] Auth başarılı, token alındı")
            return True
        except Exception as e:
            print(f"[Mealie] Auth hatası: {e}")
            return False

    def _mealie_headers(self) -> Dict:
        """Mealie API için auth header'ları."""
        return {
            "Authorization": f"Bearer {self._mealie_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    async def scrape_recipe_from_url(self, url: str) -> Optional[MealieRecipe]:
        """
        URL'den tarif scrape et (Mealie built-in scraper).
        Kullanıcı bir tarif sitesinin URL'ini yapıştırır → Mealie otomatik
        malzeme, talimat, besin değerlerini çıkarır.
        """
        if not self._mealie_token:
            await self.authenticate_mealie()

        data = {"url": url}
        try:
            resp = await self._http.post(
                f"{self.config.MEALIE_URL}/api/recipes/create/url",
                headers=self._mealie_headers(),
                json=data,
            )
            if resp.status_code == 201:
                slug = resp.text.strip('"')
                print(f"[Mealie] Tarif scrape edildi: slug={slug}")
                return await self.get_recipe(slug)
            else:
                print(f"[Mealie] Scrape hatası: {resp.status_code} {resp.text}")
                return None
        except Exception as e:
            print(f"[Mealie] Scrape exception: {e}")
            return None

    async def get_recipe(self, slug: str) -> Optional[MealieRecipe]:
        """Mealie'den tarif detayını al (malzeme, talimat, besin)."""
        try:
            resp = await self._http.get(
                f"{self.config.MEALIE_URL}/api/recipes/{slug}",
                headers=self._mealie_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return MealieRecipe(
                slug=data.get("slug", slug),
                name=data.get("name", ""),
                description=data.get("description", ""),
                servings=data.get("recipeYield", 4),
                ingredients=data.get("recipeIngredient", []),
                instructions=[
                    i.get("text", "") if isinstance(i, dict) else str(i)
                    for i in data.get("recipeInstructions", [])
                ],
                nutrition=data.get("nutrition", {}),
                tags=data.get("tags", []),
                image_url=data.get("image", ""),
            )
        except Exception as e:
            print(f"[Mealie] Get recipe hatası: {e}")
            return None

    async def search_recipes(self, query: str, limit: int = 10) -> List[MealieRecipe]:
        """Mealie'de tarif ara (malzeme veya isim ile)."""
        try:
            resp = await self._http.get(
                f"{self.config.MEALIE_URL}/api/recipes",
                headers=self._mealie_headers(),
                params={"search": query, "perPage": limit},
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            return [
                MealieRecipe(
                    slug=item.get("slug", ""),
                    name=item.get("name", ""),
                    servings=item.get("recipeYield", 4),
                )
                for item in items
            ]
        except Exception as e:
            print(f"[Mealie] Search hatası: {e}")
            return []

    async def update_recipe_servings(
        self, slug: str, new_servings: int
    ) -> Optional[MealieRecipe]:
        """Tarif porsiyon sayısını güncelle (dinamik ölçekleme)."""
        try:
            # Önce mevcut tarif'i al
            recipe = await self.get_recipe(slug)
            if not recipe:
                return None

            # Yeni porsiyon sayısıyla güncelle
            data = {"recipeYield": new_servings}
            resp = await self._http.put(
                f"{self.config.MEALIE_URL}/api/recipes/{slug}",
                headers=self._mealie_headers(),
                json=data,
            )
            resp.raise_for_status()
            print(f"[Mealie] Porsiyon güncellendi: {recipe.servings} → {new_servings}")
            return await self.get_recipe(slug)
        except Exception as e:
            print(f"[Mealie] Update servings hatası: {e}")
            return None

    async def create_meal_plan(
        self, recipe_slug: str, plan_date: date, meal_type: str = "dinner"
    ) -> bool:
        """Mealie'de yemek planı oluştur (takvim)."""
        data = {
            "date": plan_date.isoformat(),
            "entryType": meal_type,
            "recipeId": None,  # slug ile değil ID ile, ama basit tutuyoruz
            "title": recipe_slug,
        }
        try:
            resp = await self._http.post(
                f"{self.config.MEALIE_URL}/api/households/mealplans",
                headers=self._mealie_headers(),
                json=data,
            )
            return resp.status_code == 201
        except Exception as e:
            print(f"[Mealie] Meal plan hatası: {e}")
            return False

    # =========================================================================
    # DEEPSEEK — MAKRO HESABI
    # =========================================================================

    async def compute_macro_targets(
        self, weight_kg: float, goal: AthleteGoal, activity_level: str = "moderate"
    ) -> MacroTargets:
        """
        DeepSeek ile sporcu makro hedeflerini hesapla.
        Kullanıcının kilosu, hedefi (bulk/cut/maintenance) ve aktivite
        seviyesine göre protein/karb/yağ hedeflerini belirler.
        """
        prompt = (
            f"Sen bir spor beslenme uzmanısın. Aşağıdaki bilgilere göre "
            f"günlük makro hedeflerini hesapla ve SADECE JSON döndür:\n\n"
            f"Kilo: {weight_kg} kg\n"
            f"Hedef: {goal.value}\n"
            f"Aktivite: {activity_level}\n\n"
            f"JSON formatı:\n"
            f'{{"calories": int, "protein_g": float, "carbs_g": float, "fat_g": float}}\n'
            f"Sadece JSON, başka metin yok."
        )

        headers = {
            "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.config.DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 200,
        }

        try:
            resp = await self._http.post(
                self.config.DEEPSEEK_URL, headers=headers, json=body
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            # JSON'u extract et
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return MacroTargets(
                    calories=int(data.get("calories", 2800)),
                    protein_g=float(data.get("protein_g", weight_kg * 2.0)),
                    carbs_g=float(data.get("carbs_g", 350)),
                    fat_g=float(data.get("fat_g", 90)),
                )
        except Exception as e:
            print(f"[DeepSeek] Makro hesap hatası: {e}")

        # Fallback: basit hesaplama
        protein = weight_kg * self.config.PROTEIN_PER_KG
        if goal == AthleteGoal.BULK:
            return MacroTargets(calories=3200, protein_g=protein, carbs_g=400, fat_g=100)
        elif goal == AthleteGoal.CUT:
            return MacroTargets(calories=2200, protein_g=protein * 1.2, carbs_g=200, fat_g=70)
        return MacroTargets(calories=2800, protein_g=protein, carbs_g=350, fat_g=90)

    async def scale_recipe_for_athlete(
        self, recipe: MealieRecipe, targets: MacroTargets
    ) -> ScaledRecipe:
        """
        DeepSeek ile tarif'i sporcu hedeflerine göre ölçekle.
        Porsiyon sayısını, malzeme miktarlarını ve besin değerlerini
        kullanıcının makro hedeflerine göre dinamik ayarlar.
        """
        # Mevcut besin değerleri
        current_cal = recipe.calories_per_serving or 500
        current_servings = recipe.servings

        # Hedef: günlük kalorinin ~1/3'ü bu öğün için
        target_cal_per_meal = targets.calories / 3
        target_protein_per_meal = targets.protein_g / 3

        # Kaç porsiyon gerekli?
        scale_factor = target_cal_per_meal / current_cal
        new_servings = max(1, round(current_servings * scale_factor))

        # DeepSeek ile malzeme ölçekleme
        ingredients_text = "\n".join(
            f"- {ing}" for ing in recipe.ingredients
        )
        prompt = (
            f"Sen bir spor beslenme uzmanısın. Aşağıdaki tarifi "
            f"{new_servings} porsiyon için ölçekle.\n\n"
            f"Tarif: {recipe.name}\n"
            f"Mevcut porsiyon: {current_servings}\n"
            f"Hedef porsiyon: {new_servings}\n"
            f"Malzemeler:\n{ingredients_text}\n\n"
            f"Sporcu hedefi: {targets.calories} kcal/gün, "
            f"{targets.protein_g}g protein/gün\n\n"
            f"Ölçeklenmiş malzeme listesini JSON array olarak döndür:\n"
            f'["200g tavuk göğsü", "150g pirinç", ...]\n'
            f"Sadece JSON array, başka metin yok."
        )

        scaled_ingredients = recipe.ingredients  # fallback
        try:
            headers = {
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            body = {
                "model": self.config.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            }
            resp = await self._http.post(
                self.config.DEEPSEEK_URL, headers=headers, json=body
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                scaled_ingredients = json.loads(json_match.group())
        except Exception as e:
            print(f"[DeepSeek] Ölçekleme hatası: {e}")

        # Ölçeklenmiş besin değerleri
        scale_ratio = new_servings / current_servings
        scaled_nutrition = {
            "calories": round(current_cal * scale_ratio),
            "protein_g": round(
                float(
                    re.sub(
                        r"[^\d.]",
                        "",
                        str(recipe.nutrition.get("proteinContent", "30")),
                    )
                    or 30
                )
                * scale_ratio,
                1,
            ),
            "carbs_g": round(
                float(
                    re.sub(
                        r"[^\d.]",
                        "",
                        str(recipe.nutrition.get("carbohydrateContent", "50")),
                    )
                    or 50
                )
                * scale_ratio,
                1,
            ),
            "fat_g": round(
                float(
                    re.sub(
                        r"[^\d.]",
                        "",
                        str(recipe.nutrition.get("fatContent", "15")),
                    )
                    or 15
                )
                * scale_ratio,
                1,
            ),
        }

        # Pişirme profili (multicooker'a gönderilecek)
        cooking_profile = self._determine_cooking_profile(recipe, scaled_nutrition)

        return ScaledRecipe(
            recipe=recipe,
            scaled_servings=new_servings,
            scaled_ingredients=scaled_ingredients,
            scaled_nutrition=scaled_nutrition,
            cooking_profile=cooking_profile,
        )

    def _determine_cooking_profile(
        self, recipe: MealieRecipe, nutrition: Dict
    ) -> Dict:
        """Tarif tipine göre multicooker pişirme profili belirle."""
        name_lower = recipe.name.lower()
        ingredients_text = " ".join(recipe.ingredients).lower()

        # Çorba
        if "çorba" in name_lower or "soup" in name_lower or "broth" in ingredients_text:
            return {"temperature": 100, "mode": "cook", "time_min": 30}

        # Pilav / pirinç
        if "pilav" in name_lower or "rice" in name_lower or "pirinç" in ingredients_text:
            return {"temperature": 105, "mode": "cook", "time_min": 25}

        # Et yemeği
        if "tavuk" in ingredients_text or "chicken" in ingredients_text:
            return {"temperature": 110, "mode": "cook", "time_min": 35}
        if "dana" in ingredients_text or "beef" in ingredients_text:
            return {"temperature": 115, "mode": "stew", "time_min": 45}

        # Sebze
        if "sebze" in name_lower or "vegetable" in name_lower:
            return {"temperature": 100, "mode": "steam", "time_min": 15}

        # Varsayılan
        return {"temperature": 100, "mode": "cook", "time_min": 30}

    # =========================================================================
    # MQTT — MULTICOOKER KOMUTU
    # =========================================================================

    def _connect_mqtt(self) -> None:
        """Yerel MQTT broker'a bağlan."""
        self._mqtt = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="mealie-orchestrator",
        )
        self._mqtt.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self._mqtt.loop_start()

    async def send_cooking_command(self, scaled: ScaledRecipe) -> bool:
        """
        Ölçeklenmiş tarif'in pişirme komutunu MQTT üzerinden
        HA'ya → Akıllı Tencere'ye gönder.
        """
        if not self._mqtt:
            self._connect_mqtt()

        payload = json.dumps({
            "recipe_name": scaled.recipe.name,
            "recipe_slug": scaled.recipe.slug,
            "servings": scaled.scaled_servings,
            "temperature": scaled.cooking_profile["temperature"],
            "mode": scaled.cooking_profile["mode"],
            "time_min": scaled.cooking_profile["time_min"],
            "nutrition": scaled.scaled_nutrition,
            "ingredients": scaled.scaled_ingredients,
            "instructions": scaled.recipe.instructions,
            "source": "mealie",
            "timestamp": datetime.now().isoformat(),
        })

        self._mqtt.publish("multicooker/command", payload)
        print(f"[MQTT] Pişirme komutu gönderildi: {scaled.recipe.name} "
              f"({scaled.scaled_servings} porsiyon, "
              f"{scaled.cooking_profile['temperature']}°C)")

        # HA'ya da REST API ile bildir
        await self._call_ha_service(
            "script.jarvis_vision_cooker_orchestrate",
            {
                "recipe_name": scaled.recipe.name,
                "temperature": scaled.cooking_profile["temperature"],
                "mode": scaled.cooking_profile["mode"],
                "time_min": scaled.cooking_profile["time_min"],
            },
        )
        return True

    async def _call_ha_service(self, service: str, data: Dict) -> None:
        """HA REST API'ye servis çağrısı gönder."""
        headers = {
            "Authorization": f"Bearer {self.config.HA_TOKEN}",
            "Content-Type": "application/json",
        }
        url = f"{self.config.HA_URL}/api/services/{service.replace('.', '/')}"
        try:
            resp = await self._http.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                print(f"[HA] Servis çağrıldı: {service}")
            else:
                print(f"[HA] Servis hatası: {resp.status_code}")
        except Exception as e:
            print(f"[HA] Servis exception: {e}")

    # =========================================================================
    # TAM ORKESTRASYON — VISION-TO-COOK
    # =========================================================================

    async def vision_to_cook(
        self,
        detected_ingredients: List[str],
        user_goal: AthleteGoal = AthleteGoal.MAINTENANCE,
        weight_kg: float = 85,
    ) -> Optional[ScaledRecipe]:
        """
        Vision-to-Cook kapalı döngüsü:

        1. Modül 13 (Qwen-VL) tezgahtaki malzemeleri görür
        2. Jarvis bu malzemeleri Mealie'deki tariflerle eşleştirir
        3. Kullanıcıya danışır (sesli — MiniMax)
        4. Onay alındığında pişirme komutunu tencereye gönderir
        """
        print(f"\n{'='*60}")
        print(f"Vision-to-Cook başlatılıyor...")
        print(f"Malzemeler: {detected_ingredients}")
        print(f"{'='*60}\n")

        # 1. Mealie'de malzemelere uygun tarif ara
        search_query = " ".join(detected_ingredients[:3])
        matching_recipes = await self.search_recipes(search_query, limit=5)

        if not matching_recipes:
            print("[Vision-to-Cook] Mealie'de uygun tarif bulunamadı")
            # DeepSeek'ten tarif oluştur
            recipe = await self._generate_recipe_from_ingredients(
                detected_ingredients
            )
            if not recipe:
                return None
        else:
            recipe = matching_recipes[0]
            recipe = await self.get_recipe(recipe.slug)
            if not recipe:
                return None

        print(f"[Vision-to-Cook] Eşleşen tarif: {recipe.name}")

        # 2. Makro hedeflerini hesapla
        targets = await self.compute_macro_targets(weight_kg, user_goal)
        print(f"[Makro] Hedef: {targets.calories} kcal, "
              f"{targets.protein_g}g protein")

        # 3. Tarifi sporcu hedeflerine göre ölçekle
        scaled = await self.scale_recipe_for_athlete(recipe, targets)
        print(f"[Ölçekleme] {scaled.scaled_servings} porsiyon, "
              f"{scaled.scaled_nutrition['calories']} kcal")

        # 4. Kullanıcıya danış (MQTT → HA → MiniMax sesli)
        await self._ask_user_approval(scaled)

        # 5. Pişirme komutunu gönder
        await self.send_cooking_command(scaled)

        return scaled

    async def _generate_recipe_from_ingredients(
        self, ingredients: List[str]
    ) -> Optional[MealieRecipe]:
        """Mealie'de tarif yoksa DeepSeek'ten tarif oluştur."""
        prompt = (
            f"Şu malzemelerle basit bir tarif oluştur: {', '.join(ingredients)}\n"
            f"JSON formatında döndür:\n"
            f'{{"name": "...", "ingredients": ["..."], '
            f'"instructions": ["..."], "servings": 4}}'
        )
        try:
            headers = {
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            body = {
                "model": self.config.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 500,
            }
            resp = await self._http.post(
                self.config.DEEPSEEK_URL, headers=headers, json=body
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return MealieRecipe(
                    slug=f"generated-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    name=data.get("name", "Özel Tarif"),
                    servings=data.get("servings", 4),
                    ingredients=data.get("ingredients", []),
                    instructions=data.get("instructions", []),
                )
        except Exception as e:
            print(f"[DeepSeek] Tarif oluşturma hatası: {e}")
        return None

    async def _ask_user_approval(self, scaled: ScaledRecipe) -> None:
        """Kullanıcıdan sesli onay iste (MQTT → HA → MiniMax)."""
        if not self._mqtt:
            self._connect_mqtt()

        message = (
            f"Tarif: {scaled.recipe.name}. "
            f"{scaled.scaled_servings} porsiyon, "
            f"{scaled.scaled_nutrition['calories']} kalori, "
            f"{scaled.scaled_nutrition['protein_g']} gram protein. "
            f"Pişirmeye onay veriyor musunuz?"
        )

        payload = json.dumps({
            "message": message,
            "recipe_name": scaled.recipe.name,
            "nutrition": scaled.scaled_nutrition,
            "awaiting_approval": True,
        })

        self._mqtt.publish("jarvis/chef/recipe_suggestion", payload)
        print(f"[Onay] Kullanıcıya soruldu: {message}")

    # =========================================================================
    # URL'DEN TARİF EKLE (kullanıcı yapıştırır)
    # =========================================================================

    async def add_recipe_from_url(self, url: str) -> Optional[MealieRecipe]:
        """
        Kullanıcı bir tarif sitesinin URL'ini yapıştırır.
        Mealie otomatik scrape eder → veritabanına kaydeder.
        "Bu tarifi kaydet" → URL yapıştır → Mealie scrape → kayıt
        """
        print(f"[Mealie] URL scrape ediliyor: {url}")
        recipe = await self.scrape_recipe_from_url(url)
        if recipe:
            print(f"[Mealie] Kaydedildi: {recipe.name} "
                  f"({recipe.servings} porsiyon, "
                  f"{len(recipe.ingredients)} malzeme)")
        return recipe

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
    """Demo: URL'den tarif ekle → makro hesapla → pişir."""
    orchestrator = MealieMacroOrchestrator()

    # 1. Mealie'ye bağlan
    if not await orchestrator.authenticate_mealie():
        print("Mealie bağlantısı başarısız!")
        return

    # 2. URL'den tarif scrape et
    # recipe = await orchestrator.add_recipe_from_url(
    #     "https://www.allrecipes.com/recipe/12345/example"
    # )

    # 3. Vision-to-Cook (malzemeler → tarif → pişir)
    # scaled = await orchestrator.vision_to_cook(
    #     detected_ingredients=["domates", "soğan", "sarımmsak", "tavuk göğsü"],
    #     user_goal=AthleteGoal.MAINTENANCE,
    #     weight_kg=85,
    # )

    await orchestrator.close()
    print("Mealie Macro Orchestrator hazır.")


if __name__ == "__main__":
    asyncio.run(main())