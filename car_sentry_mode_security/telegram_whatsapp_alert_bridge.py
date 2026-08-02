"""
 =============================================================================
 car_sentry_mode_security — Telegram/WhatsApp Alert Bridge
 =============================================================================
 2026 Sürümü — Anlık fotoğraf → Telegram Bot API / WhatsApp Business API

 Sentry Mode tetiklendiğinde, kameradan alınan yüksek çözünürlüklü anlık
 fotoğrafı (snapshot) base64'e çevirir ve kullanıcının telefonuna
 "⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı."
 metniyle birlikte gönderir.

 📱 "TESLA SENTRY MODE" MANTIĞI:
 =============================================================================
 Tesla, Sentry Mode'da bir tehdit algıladığında:
 1. Kamera kaydı başlatır
 2. Kullanıcıya anlık bildirim gönderir
 3. Fotoğraf/video kaydeder

 Bu modül aynı mantığı uygular:
 1. PIR/Şok tetikleme → kamera snapshot
 2. Telegram Bot API → fotoğraf + uyarı metni → telefona anlık gönder
 3. WhatsApp Business API → alternatif kanal (opsiyonel)
 4. MQTT → HA → SuperApp'te güvenlik paneli güncelle

 GEREKLİ KÜTÜPHANELER:
   pip install httpx asyncio

 =============================================================================
"""

import asyncio
import base64
import json
import time
import logging
from typing import Optional

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class AlertBridgeConfig:
    """Telegram/WhatsApp alert bridge konfigürasyonu."""

    # Telegram Bot API
    TELEGRAM_BOT_TOKEN: str = "YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID: str = "YOUR_TELEGRAM_CHAT_ID"  # Kullanıcının chat ID'si

    # WhatsApp Business API (opsiyonel — Meta Business)
    WHATSAPP_TOKEN: str = "YOUR_WHATSAPP_TOKEN"
    WHATSAPP_PHONE_ID: str = "YOUR_WHATSAPP_PHONE_ID"
    WHATSAPP_RECIPIENT: str = "YOUR_PHONE_NUMBER"  # +905551234567

    # MQTT (HA'a bildirim)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_ALERT: str = "jarvis/car/sentry/alert"

    # Fotoğraf
    SNAPSHOT_DIR: str = "/tmp/sentry_snapshots/"
    MAX_PHOTO_SIZE_KB: int = 500  # Telegram limit ~10MB ama hız için 500KB


# =============================================================================
# TELEGRAM/WHATSAPP ALERT BRIDGE
# =============================================================================

class TelegramWhatsAppAlertBridge:
    """
    Sentry tetiklemesi → anlık fotoğraf → Telegram/WhatsApp → telefon.

    📱 "TESLA SENTRY MODE" MANTIĞI:
    =============================================================================
    1. Sentry daemon → tetikleme → snapshot al
    2. Bu bridge: snapshot'ı base64'e çevir → Telegram Bot API'ye gönder
    3. Kullanıcı telefonunda anlık bildirim alır:
       "⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı."
       + fotoğraf
    4. MQTT → HA → SuperApp güvenlik paneli güncellenir

    "Tony Stark'ın aracı tehdit algıladığında, o an telefonda görür."
    """

    def __init__(self, config: AlertBridgeConfig = None):
        self.config = config or AlertBridgeConfig()
        self.client = httpx.AsyncClient(timeout=30.0)

        logging.basicConfig(level=logging.INFO, format='[AlertBridge] %(message)s')
        self.log = logging.getLogger("alert_bridge")

        print("[AlertBridge] Telegram/WhatsApp Bridge başlatıldı (2026)")

    # =========================================================================
    # ANA FONKSİYON: Tetikleme → Fotoğraf → Telegram + WhatsApp
    # =========================================================================
    async def send_alert(
        self,
        snapshot_path: str,
        trigger_type: str,
        message: str = "⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı."
    ) -> bool:
        """
        Sentry tetiklemesini Telegram + WhatsApp üzerinden telefona gönder.

        📱 MANTIK:
        1. Snapshot dosyasını oku → base64
        2. Telegram Bot API → sendPhoto (fotoğraf + mesaj)
        3. WhatsApp Business API → send message (metin, opsiyonel fotoğraf)
        4. MQTT → HA → SuperApp güvenlik paneli

        Hız: ~2-5 saniye (fotoğraf yükleme + API çağrısı)
        "Tehlike anından 5 saniye sonra telefonda fotoğraf görürsün."
        """
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"{message}\n🕐 {timestamp}\n📍 Tetikleme: {trigger_type}"

        success = True

        # -------------------------------------------------------------------------
        # 1. Telegram Bot API → sendPhoto
        # -------------------------------------------------------------------------
        try:
            tg_success = await self._send_telegram_photo(snapshot_path, full_message)
            if tg_success:
                self.log.info(f"📱 Telegram'a fotoğraf gönderildi: {trigger_type}")
            else:
                self.log.error("❌ Telegram gönderimi başarısız")
                success = False
        except Exception as e:
            self.log.error(f"❌ Telegram hatası: {e}")
            success = False

        # -------------------------------------------------------------------------
        # 2. WhatsApp Business API → sendMessage (opsiyonel)
        # -------------------------------------------------------------------------
        if self.config.WHATSAPP_TOKEN != "YOUR_WHATSAPP_TOKEN":
            try:
                wa_success = await self._send_whatsapp_message(full_message)
                if wa_success:
                    self.log.info(f"📱 WhatsApp'a mesaj gönderildi")
            except Exception as e:
                self.log.error(f"❌ WhatsApp hatası: {e}")

        # -------------------------------------------------------------------------
        # 3. MQTT → HA → SuperApp güvenlik paneli
        # -------------------------------------------------------------------------
        try:
            await self._send_mqtt_alert(snapshot_path, trigger_type, full_message)
        except Exception as e:
            self.log.error(f"❌ MQTT hatası: {e}")

        return success

    # =========================================================================
    # TELEGRAM BOT API — sendPhoto
    # =========================================================================
    async def _send_telegram_photo(self, photo_path: str, caption: str) -> bool:
        """
        Telegram Bot API ile fotoğraf + mesaj gönder.

        📱 MANTIK:
        Telegram Bot API → sendPhoto endpoint:
        POST https://api.telegram.org/bot{TOKEN}/sendPhoto
        - chat_id: kullanıcının chat ID'si
        - photo: fotoğraf dosyası (multipart/form-data)
        - caption: uyarı mesajı

        Kullanıcı telefonunda anlık bildirim alır:
        "⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı."
        + fotoğraf
        """
        url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendPhoto"

        try:
            with open(photo_path, "rb") as photo_file:
                files = {"photo": photo_file}
                data = {
                    "chat_id": self.config.TELEGRAM_CHAT_ID,
                    "caption": caption,
                    "parse_mode": "HTML"
                }

                response = await self.client.post(url, data=data, files=files)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        return True
                    else:
                        self.log.error(f"Telegram API hatası: {result.get('description')}")
                        return False
                else:
                    self.log.error(f"Telegram HTTP {response.status_code}")
                    return False

        except FileNotFoundError:
            self.log.error(f"Fotoğraf bulunamadı: {photo_path}")
            return False

    # =========================================================================
    # WHATSAPP BUSINESS API — sendMessage (opsiyonel)
    # =========================================================================
    async def _send_whatsapp_message(self, message: str) -> bool:
        """
        WhatsApp Business API ile mesaj gönder (opsiyonel).

        📱 MANTIK:
        Meta Graph API → WhatsApp Business:
        POST https://graph.facebook.com/v18.0/{PHONE_ID}/messages
        - messaging_product: "whatsapp"
        - to: alıcı telefon numarası
        - type: "text"
        - text: { "body": message }

        Not: WhatsApp Business API, Meta Developer hesabı + onaylı numara gerektirir.
        Telegram daha kolay (BotFather → token → hazır).
        """
        url = f"https://graph.facebook.com/v18.0/{self.config.WHATSAPP_PHONE_ID}/messages"

        headers = {
            "Authorization": f"Bearer {self.config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": self.config.WHATSAPP_RECIPIENT,
            "type": "text",
            "text": {"body": message}
        }

        response = await self.client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return True
        else:
            self.log.error(f"WhatsApp HTTP {response.status_code}: {response.text}")
            return False

    # =========================================================================
    # MQTT → HA → SuperApp Güvenlik Paneli
    # =========================================================================
    async def _send_mqtt_alert(
        self,
        snapshot_path: str,
        trigger_type: str,
        message: str
    ) -> None:
        """
        MQTT üzerinden HA'a alert gönder → SuperApp güvenlik paneli güncellenir.

        📱 MANTIK:
        MQTT → jarvis/car/sentry/alert → HA otomasyon →
        SuperApp'te "Sentry Alert" kartı görünür →
        Son ihlal fotoğrafı + zaman + tetikleme tipi gösterilir.
        """
        import paho.mqtt.client as mqtt

        client = mqtt.Client()
        client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)

        payload = json.dumps({
            "type": trigger_type,
            "message": message,
            "snapshot": snapshot_path,
            "timestamp": time.time()
        })

        client.publish(self.config.MQTT_TOPIC_ALERT, payload)
        client.disconnect()

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Alert bridge test."""
    bridge = TelegramWhatsAppAlertBridge()

    # Test: sahte snapshot gönder
    # Önce bir test fotoğrafı oluştur
    import cv2
    import numpy as np

    # Boş bir test görüntüsü oluştur
    test_img = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.putText(test_img, "SENTRY TEST", (400, 360),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    test_path = "/tmp/sentry_test.jpg"
    cv2.imwrite(test_path, test_img)

    # Telegram'a gönder
    success = await bridge.send_alert(
        snapshot_path=test_path,
        trigger_type="PIR_MOTION",
        message="⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı."
    )

    if success:
        print("✅ Alert gönderildi!")
    else:
        print("❌ Alert gönderimi başarısız (Telegram token kontrol et)")

    await bridge.close()


if __name__ == "__main__":
    asyncio.run(main())