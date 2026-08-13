"""
=============================================================================
openclaw_digital_sandbox — Yemeksepeti Macro Injector
=============================================================================
Modül 27: OpenClaw — Yemeksepeti siparişinden otomatik makro enjeksiyonu

Kullanıcı Yemeksepeti'den sipariş verdiğinde OpenClaw:
1. Tarayıcıda sepet özetini okur (DOM scraping — browser-use)
2. DeepSeek'e "2 lahmacun + 1 ayran" gönderir → makro tahmini
3. Modül 16 (Life OS) günlük kalori hedefine MQTT ile ekler

🎯 "BIO-HACKING ZİRVESİ":
   "Sipariş verdim" dersin → kalori/makro hedefin arka planda güncellenir
   Sen tek bir tuşa basmazsın.

🔗 AKIŞ:
   Yemeksepeti sepet → OpenClaw (browser-use DOM okuma)
   → DeepSeek (makro tahmini: "2 lahmacun ~700 kcal, 28g protein")
   → MQTT jarvis/lifeos/nutrition/inject → Modül 16 (Life OS)
   → Günlük kalori hedefi otomatik güncellenir

🔗 MODÜL BAĞLANTILARI:
   Modül 16 (Holistic Life OS) → günlük kalori/makro takibi
   jarvis_core (DeepSeek V4-Pro) → makro tahmini
   jarvis_core (MiniMax Speech 2.8 Turbo) → sesli onay

=============================================================================
"""

import os
import re
import json
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

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

class InjectorConfig:
    """Yemeksepeti makro enjektör konfigürasyonu."""

    # DeepSeek (makro tahmini)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # MQTT (Modül 16'ya enjeksiyon)
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "gl-mt3000.local")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

    # HA REST API (MiniMax sesli onay)
    HA_URL: str = os.getenv("HA_URL", "http://homeassistant.local:8123")
    HA_TOKEN: str = os.getenv("HA_TOKEN", "")


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

@dataclass
class CartItem:
    """Yemeksepeti sepet öğesi."""
    name: str
    quantity: int
    price: Optional[float] = None


@dataclass
class MacroEstimate:
    """DeepSeek'ten gelen makro tahmini."""
    calories: int = 0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    items: List[Dict] = None  # her öğe için ayrı makro


# =============================================================================
# YEMEKSEPETI MACRO INJECTOR
# =============================================================================

class YemeksepetiMacroInjector:
    """
    OpenClaw'un Yemeksepeti siparişinden otomatik makro enjeksiyonu.

    Akış:
    1. browser-use ile Yemeksepeti sepet DOM'unu oku
    2. DeepSeek'e sepet içeriğini gönder → makro tahmini al
    3. MQTT ile Modül 16 (Life OS) günlük kaloriye ekle
    4. MiniMax ile sesli onay ver
    """

    def __init__(self, config: InjectorConfig = None):
        self.config = config or InjectorConfig()
        self._mqtt: Optional[mqtt.Client] = None
        self._http = httpx.AsyncClient(timeout=30.0)

    # =========================================================================
    # ADIM 1: BROWSER-USE — SEPET DOM OKUMA
    # =========================================================================

    async def read_cart_from_dom(self) -> List[CartItem]:
        """
        browser-use ile Yemeksepeti sepet özetini oku.
        OpenClaw, kullanıcının sipariş onayladığı sayfadaki DOM'dan
        sepet içeriğini çıkarır.

        Gerçek implementasyonda browser-use kütüphanesi çağrılır.
        Burada simüle edilmiş akış var.
        """
        # Gerçek implementasyon:
        # from browser_use import Agent
        # agent = Agent(
        #     task="Yemeksepeti sepet sayfasındaki tüm öğeleri oku.
        #           Her öğenin adını ve adedini çıkar.",
        #     llm=deepseek_llm,
        #     headless=True,  # Ekranda pencere AÇILMAZ
        # )
        # result = await agent.run()

        # Simüle edilmiş sepet içeriği
        simulated_cart = [
            CartItem(name="Lahmacun", quantity=2, price=120.0),
            CartItem(name="Ayran", quantity=1, price=25.0),
        ]

        print(f"[Browser] Sepet okundu: {len(simulated_cart)} öğe")
        for item in simulated_cart:
            print(f"  → {item.quantity}x {item.name}")

        return simulated_cart

    # =========================================================================
    # ADIM 2: DEEPSEEK — MAKRO TAHMİNİ
    # =========================================================================

    async def estimate_macros(self, cart: List[CartItem]) -> MacroEstimate:
        """
        DeepSeek'e sepet içeriğini gönder, makro tahmini al.
        "2 lahmacun + 1 ayran → ~700 kcal, 28g protein, 60g karb, 35g yağ"
        """
        items_text = "\n".join(
            f"- {item.quantity}x {item.name}" for item in cart
        )

        prompt = (
            f"Sen bir spor beslenme uzmanısın. Aşağıdaki siparişin "
            f"toplam makro değerlerini tahmin et:\n\n"
            f"{items_text}\n\n"
            f"JSON formatında döndür:\n"
            f'{{"calories": int, "protein_g": float, '
            f'"carbs_g": float, "fat_g": float, '
            f'"items": [{{"name": "...", "calories": int, '
            f'"protein_g": float}}]}}\n'
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
            "max_tokens": 300,
        }

        try:
            resp = await self._http.post(
                self.config.DEEPSEEK_URL, headers=headers, json=body
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                estimate = MacroEstimate(
                    calories=int(data.get("calories", 0)),
                    protein_g=float(data.get("protein_g", 0)),
                    carbs_g=float(data.get("carbs_g", 0)),
                    fat_g=float(data.get("fat_g", 0)),
                    items=data.get("items", []),
                )
                print(f"[DeepSeek] Makro tahmini: {estimate.calories} kcal, "
                      f"{estimate.protein_g}g protein, "
                      f"{estimate.carbs_g}g karb, "
                      f"{estimate.fat_g}g yağ")
                return estimate
        except Exception as e:
            print(f"[DeepSeek] Makro tahmin hatası: {e}")

        # Fallback: basit tahmin
        return MacroEstimate(
            calories=700, protein_g=28, carbs_g=60, fat_g=35
        )

    # =========================================================================
    # ADIM 3: MQTT — MODÜL 16'YA ENJEKSİYON
    # =========================================================================

    def _connect_mqtt(self) -> None:
        """Yerel MQTT broker'a bağlan."""
        self._mqtt = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id="openclaw-yemeksepeti-injector",
        )
        self._mqtt.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self._mqtt.loop_start()

    async def inject_to_life_os(self, estimate: MacroEstimate,
                                 cart: List[CartItem]) -> bool:
        """
        Modül 16 (Holistic Life OS) günlük kalori hedefine makro ekle.
        MQTT üzerinden jarvis/lifeos/nutrition/inject topic'ine gönder.
        """
        if not self._mqtt:
            self._connect_mqtt()

        payload = json.dumps({
            "source": "yemeksepeti",
            "timestamp": datetime.now().isoformat(),
            "items": [
                {"name": item.name, "quantity": item.quantity}
                for item in cart
            ],
            "nutrition": {
                "calories": estimate.calories,
                "protein_g": estimate.protein_g,
                "carbs_g": estimate.carbs_g,
                "fat_g": estimate.fat_g,
            },
            "action": "add_to_daily_intake",
        })

        self._mqtt.publish("jarvis/lifeos/nutrition/inject", payload)
        print(f"[MQTT] Modül 16'ya enjekte edildi: "
              f"{estimate.calories} kcal, {estimate.protein_g}g protein")
        return True

    # =========================================================================
    # ADIM 4: MINIMAX — SESLİ ONAY
    # =========================================================================

    async def notify_user(self, estimate: MacroEstimate,
                          cart: List[CartItem]) -> None:
        """Kullanıcıya sesli onay ver (MiniMax üzerinden HA)."""
        items_summary = ", ".join(
            f"{item.quantity}x {item.name}" for item in cart
        )

        message = (
            f"Siparişiniz sisteme eklendi efendim. "
            f"{items_summary} — yaklaşık {estimate.calories} kalori, "
            f"{int(estimate.protein_g)} gram protein. "
            f"Günlük hedefiniz güncellendi."
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
            print(f"[MiniMax] Sesli onay: {message}")
        except Exception as e:
            print(f"[MiniMax] Bildirim hatası: {e}")

    # =========================================================================
    # TAM WORKFLOW — SIPARIŞTEN MAKROYA
    # =========================================================================

    async def process_order(self) -> MacroEstimate:
        """
        Tam otonom sipariş-makro workflow'u:
        1. Browser-use → sepet DOM oku
        2. DeepSeek → makro tahmini
        3. MQTT → Modül 16'ya enjekte
        4. MiniMax → sesli onay
        """
        print(f"\n{'='*60}")
        print(f"Yemeksepeti Macro Injector başlatıldı")
        print(f"{'='*60}\n")

        # ADIM 1: Sepet oku
        cart = await self.read_cart_from_dom()
        if not cart:
            print("Sepet boş!")
            return MacroEstimate()

        # ADIM 2: Makro tahmini
        estimate = await self.estimate_macros(cart)

        # ADIM 3: Modül 16'ya enjekte
        await self.inject_to_life_os(estimate, cart)

        # ADIM 4: Sesli onay
        await self.notify_user(estimate, cart)

        print(f"\n{'='*60}")
        print(f"Tamamlandı: {estimate.calories} kcal → Modül 16")
        print(f"{'='*60}\n")

        return estimate

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
    """Demo: Sipariş → makro → Life OS."""
    injector = YemeksepetiMacroInjector()

    # "Sipariş verdim" → otomatik makro enjeksiyon
    estimate = await injector.process_order()

    print(f"Sonuç: {estimate.calories} kcal, "
          f"{estimate.protein_g}g protein → Modül 16'ya eklendi")

    await injector.close()


if __name__ == "__main__":
    asyncio.run(main())