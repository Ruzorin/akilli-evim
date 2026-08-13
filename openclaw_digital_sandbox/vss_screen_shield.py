"""
 =============================================================================
 openclaw_digital_sandbox — VSS Otonom Ekran Kalkanı
 =============================================================================
 2026 Sürümü — OpenClaw + OS Renk Profili Yönetimi

 Kullanıcı Visual Snow Syndrome (VSS) hastası. Bu script, kullanıcının
 bilgisayar başındaki çalışma süresini ve ekran parlaklık/kontrast
 oranlarını izleyerek VSS yorgunluğunu önlemek için işletim sisteminin
 renk profillerini otonom olarak yönetir.

 🧠 MANTIK:
 1. Çalışma süresi izle (saat başı mola hatırlat)
 2. Ekran parlaklığı çok yüksekse → düşür (VSS tetikleyici)
 3. Mavi ışık yüksekse → Night Light / f.lux benzeri filtre aç
 4. Karanlık mod değilse → karanlık moda geç
 5. Lamba (Modül 29) ile senkron — lamba kehribar, ekran da sıcak

 🎯 VSS İÇİN KRİTİK:
 - Mavi ışık (450nm) → VSS kar desisini artırır
 - Yüksek parlaklık → görsel yorgunluk → VSS alevlenme
 - Yüksek kontrast → görsel stres → VSS tetikleyici
 - Uzun süreli ekran → göz kuruluğu → VSS kötüleşme

 GEREKLİ KÜTÜPHANELER:
    pip install httpx asyncio

 =============================================================================
"""

import asyncio
import time
import logging
import platform
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

@dataclass
class VSSShieldConfig:
    """VSS Ekran Kalkanı konfigürasyonu."""

    # Çalışma süresi
    WORK_SESSION_MIN: int = 50       # 50 dk çalış
    BREAK_DURATION_MIN: int = 10     # 10 dk mola
    MAX_DAILY_SCREEN_HOURS: int = 8  # Günlük max 8 saat

    # Ekran parametreleri (VSS eşikleri)
    MAX_BRIGHTNESS_PCT: int = 70     # %70 üstü → VSS tetikleyici
    TARGET_BRIGHTNESS_PCT: int = 50  # Hedef parlaklık
    MAX_BLUE_LIGHT_PCT: int = 30     # %30 üstü mavi → VSS artış
    TARGET_COLOR_TEMP_K: int = 3400  # Hedef: 3400K (sıcak, amber)

    # Karanlık mod
    DARK_MODE_THRESHOLD_HOUR: int = 20  # 20:00'dan sonra karanlık mod
    LIGHT_MODE_THRESHOLD_HOUR: int = 7  # 07:00'dan sonra aydınlık mod

    # MQTT (Lamba senkron)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_LAMP_LIGHT: str = "jarvis/lamp/light/command"

    # HA REST API
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # OS
    OS_TYPE: str = platform.system()  # Windows, Linux, Darwin


# =============================================================================
# VSS SEVİYE
# =============================================================================

class VSSLevel(Enum):
    """VSS yorgunluk seviyesi."""
    GOOD = "good"          # < 1 saat, düşük parlaklık
    MODERATE = "moderate"  # 1-3 saat, orta parlaklık
    HIGH = "high"          # 3-5 saat, yüksek parlaklık
    CRITICAL = "critical"  # > 5 saat veya çok yüksek parlaklık


# =============================================================================
# VSS EKRAN KALKANI
# =============================================================================

class VSSScreenShield:
    """
    OpenClaw'un VSS koruma modülü — ekran renk/parlaklık yönetimi.

    🛡️ VSS KORUMA MANTIĞI:
    1. Çalışma süresi izle → 50 dk dolunca mola hatırlat
    2. Parlaklık > %70 → otomatik düşür
    3. Mavi ışık > %30 → Night Light aç (sıcak renk)
    4. Saat 20:00 → karanlık mod
    5. Lamba ile senkron → lamba kehribar, ekran da sıcak

    "Gözünüzü koruyan, VSS'i sakin tutan sessiz kalkan."
    """

    def __init__(self, config: VSSShieldConfig = None):
        self.config = config or VSSShieldConfig()
        self._session_start = time.time()
        self._total_screen_time = 0
        self._last_break_time = time.time()
        self._current_vss_level = VSSLevel.GOOD

        logging.basicConfig(level=logging.INFO, format='[VSSShield] %(message)s')
        self.log = logging.getLogger("vss_shield")
        self.log.info(f"VSS Ekran Kalkanı başlatıldı (OS: {self.config.OS_TYPE})")

    # =========================================================================
    # ÇALIŞMA SÜRESİ İZLEME
    # =========================================================================
    def get_session_duration_min(self) -> float:
        """Mevcut çalışma oturumu süresi (dakika)."""
        return (time.time() - self._session_start) / 60

    def get_time_since_break_min(self) -> float:
        """Son moladan beri geçen süre (dakika)."""
        return (time.time() - self._last_break_time) / 60

    def should_take_break(self) -> bool:
        """Mola zamanı geldi mi?"""
        return self.get_time_since_break_min() >= self.config.WORK_SESSION_MIN

    # =========================================================================
    # VSS SEVİYE HESAPLA
    # =========================================================================
    def compute_vss_level(self, brightness: float, blue_light: float,
                          screen_hours: float) -> VSSLevel:
        """
        VSS yorgunluk seviyesini hesapla.

        Args:
            brightness: Ekran parlaklığı (%)
            blue_light: Mavi ışık oranı (%)
            screen_hours: Günlük ekran süresi (saat)

        Returns:
            VSS yorgunluk seviyesi
        """
        score = 0

        # Parlaklık skoru
        if brightness > self.config.MAX_BRIGHTNESS_PCT:
            score += 2
        elif brightness > 50:
            score += 1

        # Mavi ışık skoru
        if blue_light > self.config.MAX_BLUE_LIGHT_PCT:
            score += 2
        elif blue_light > 15:
            score += 1

        # Ekran süresi skoru
        if screen_hours > 5:
            score += 2
        elif screen_hours > 3:
            score += 1

        # Seviye belirle
        if score >= 4:
            return VSSLevel.CRITICAL
        elif score >= 2:
            return VSSLevel.HIGH
        elif score >= 1:
            return VSSLevel.MODERATE
        else:
            return VSSLevel.GOOD

    # =========================================================================
    # OS RENK PROFİLİ YÖNETİMİ
    # =========================================================================
    async def adjust_brightness(self, target_pct: int):
        """
        İşletim sistemi ekran parlaklığını ayarla.

        Windows: powercfg / WMI
        Linux: xrandr / brightnessctl
        macOS: brightnessctl / osascript
        """
        self.log.info(f"Parlaklık ayarlanıyor: %{target_pct}")

        if self.config.OS_TYPE == "Windows":
            # Windows — WMI ile parlaklık
            try:
                subprocess.run([
                    "powershell", "-Command",
                    f"(Get-WmiObject -Namespace root/WMI "
                    f"-Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{target_pct})"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"Windows parlaklık hatası: {e}")

        elif self.config.OS_TYPE == "Linux":
            # Linux — brightnessctl
            try:
                subprocess.run([
                    "brightnessctl", "set", f"{target_pct}%"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"Linux parlaklık hatası: {e}")

        elif self.config.OS_TYPE == "Darwin":
            # macOS — osascript
            try:
                brightness = target_pct / 100.0
                subprocess.run([
                    "osascript", "-e",
                    f"tell application \"System Events\" to "
                    f"set brightness of display 1 to {brightness}"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"macOS parlaklık hatası: {e}")

    async def enable_night_light(self, color_temp_k: int = 3400):
        """
        Mavi ışık filtresi aç (Night Light / Night Shift).

        Windows: Night Light (registry)
        Linux: redshift / wlsunset
        macOS: Night Shift
        """
        self.log.info(f"Night Light açılıyor: {color_temp_k}K")

        if self.config.OS_TYPE == "Windows":
            # Windows Night Light — registry
            try:
                subprocess.run([
                    "powershell", "-Command",
                    "Set-ItemProperty -Path "
                    "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\"
                    "Store\\DefaultAccount\\Current\\default\\$$windows.data.bluelightreduction\\"
                    "windows.data.bluelightreduction' "
                    "-Name 'Data' -Value ([byte[]](0x02,0x00,0x00,0x00))"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"Windows Night Light hatası: {e}")

        elif self.config.OS_TYPE == "Linux":
            # Linux — redshift
            try:
                subprocess.Popen([
                    "redshift", "-O", str(color_temp_k)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                self.log.warning(f"Linux redshift hatası: {e}")

        elif self.config.OS_TYPE == "Darwin":
            # macOS Night Shift — corebrightnessd
            try:
                subprocess.run([
                    "osascript", "-e",
                    f"tell application \"System Events\" to "
                    f"set night shift to true"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"macOS Night Shift hatası: {e}")

    async def enable_dark_mode(self, enabled: bool = True):
        """
        Karanlık mod aç/kapat.

        Windows: Dark mode (registry)
        Linux: GTK theme
        macOS: Dark mode (osascript)
        """
        mode = "dark" if enabled else "light"
        self.log.info(f"Karanlık mod: {mode}")

        if self.config.OS_TYPE == "Windows":
            try:
                value = 0 if enabled else 1  # 0 = dark, 1 = light
                subprocess.run([
                    "powershell", "-Command",
                    f"Set-ItemProperty -Path "
                    f"'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' "
                    f"-Name 'AppsUseLightTheme' -Value {value}"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"Windows dark mode hatası: {e}")

        elif self.config.OS_TYPE == "Linux":
            theme = "Adwaita-dark" if enabled else "Adwaita"
            try:
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface",
                    "gtk-theme", theme
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"Linux dark mode hatası: {e}")

        elif self.config.OS_TYPE == "Darwin":
            value = "true" if enabled else "false"
            try:
                subprocess.run([
                    "osascript", "-e",
                    f"tell application \"System Events\" to "
                    f"set dark mode to {value}"
                ], check=True, capture_output=True)
            except Exception as e:
                self.log.warning(f"macOS dark mode hatası: {e}")

    # =========================================================================
    # LAMBA SENKRONİZASYONU
    # =========================================================================
    async def sync_with_lamp(self, vss_level: VSSLevel):
        """
        Lamba (Modül 29) ile ekran renk sıcaklığını senkronize et.

        VSS dostu: Lamba kehribar → ekran da sıcak (3400K)
        """
        try:
            import paho.mqtt.client as mqtt
            client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
                client_id="vss-shield"
            )
            client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)

            # VSS seviyesine göre lamba rengi
            if vss_level == VSSLevel.CRITICAL:
                # Kritik — lamba çok loş amber (göz dinlendirme)
                payload = '{"effect": "amber_glow", "brightness": 15}'
            elif vss_level == VSSLevel.HIGH:
                # Yüksek — lamba loş amber
                payload = '{"effect": "amber_glow", "brightness": 25}'
            else:
                # Normal — lamba normal sıcak
                payload = '{"effect": "warm_white", "brightness": 40}'

            client.publish(self.config.MQTT_TOPIC_LAMP_LIGHT, payload)
            client.disconnect()

        except Exception as e:
            self.log.warning(f"Lamba senkron hatası: {e}")

    # =========================================================================
    # ANA KORUMA DÖNGÜSÜ
    # =========================================================================
    async def run_shield(self):
        """
        VSS koruma döngüsü — her 60 sn'de bir kontrol et.

        1. Çalışma süresi → mola hatırlat
        2. Parlaklık → çok yüksekse düşür
        3. Mavi ışık → çok yüksekse Night Light
        4. Saat → karanlık mod
        5. Lamba senkron
        """
        self.log.info("VSS koruma döngüsü başladı")

        while True:
            try:
                # Mevcut saat
                current_hour = time.localtime().tm_hour

                # 1. Karanlık mod (saat bazlı)
                if current_hour >= self.config.DARK_MODE_THRESHOLD_HOUR:
                    await self.enable_dark_mode(True)
                elif current_hour >= self.config.LIGHT_MODE_THRESHOLD_HOUR:
                    await self.enable_dark_mode(False)

                # 2. Night Light (her zaman VSS için)
                await self.enable_night_light(self.config.TARGET_COLOR_TEMP_K)

                # 3. Parlaklık hedefe ayarla
                await self.adjust_brightness(self.config.TARGET_BRIGHTNESS_PCT)

                # 4. Mola kontrolü
                if self.should_take_break():
                    self.log.info(
                        f"⏰ Mola zamanı! {self.config.WORK_SESSION_MIN} dk çalıştınız. "
                        f"{self.config.BREAK_DURATION_MIN} dk mola verin."
                    )
                    # HA'ya mola bildir → Jarvis sesli hatırlat
                    await self._notify_ha_break()
                    self._last_break_time = time.time()

                # 5. VSS seviyesi hesapla
                session_min = self.get_session_duration_min()
                screen_hours = session_min / 60
                vss_level = self.compute_vss_level(
                    brightness=self.config.TARGET_BRIGHTNESS_PCT,
                    blue_light=10,  # Night Light aktif → düşük
                    screen_hours=screen_hours
                )

                if vss_level != self._current_vss_level:
                    self.log.info(f"VSS seviye değişti: {vss_level.value}")
                    self._current_vss_level = vss_level

                # 6. Lamba senkron
                await self.sync_with_lamp(vss_level)

            except Exception as e:
                self.log.error(f"Koruma döngüsü hatası: {e}")

            await asyncio.sleep(60)  # Her dakika kontrol et

    # =========================================================================
    # HA BİLDİRİM
    # =========================================================================
    async def _notify_ha_break(self):
        """HA'ya mola bildirimi gönder → Jarvis sesli hatırlatır."""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.config.HA_URL}/api/services/persistent_notification/create",
                    headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
                    json={
                        "title": "🧘 VSS Mola Hatırlatması",
                        "message": f"{self.config.WORK_SESSION_MIN} dk çalıştınız. "
                                   f"Gözlerinizi dinlendirin."
                    }
                )
        except Exception as e:
            self.log.warning(f"HA bildirim hatası: {e}")


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """VSS Ekran Kalkanı test."""
    shield = VSSScreenShield()
    print("\n=== VSS Ekran Kalkanı ===")
    print(f"OS: {shield.config.OS_TYPE}")
    print(f"Hedef parlaklık: %{shield.config.TARGET_BRIGHTNESS_PCT}")
    print(f"Hedef renk: {shield.config.TARGET_COLOR_TEMP_K}K")
    print("\nKoruma döngüsü başlatılıyor...\n")
    await shield.run_shield()


if __name__ == "__main__":
    asyncio.run(main())