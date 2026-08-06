"""
 =============================================================================
 car_stealth_and_seduction — Sci-Fi Soundspace Augmenter
 =============================================================================
 2026 Sürümü — OBD2 RPM → Fütüristik Uzay Gemisi Sesi (Sound Augmentation)

 Bu modül, OBD2 portundan anlık motor devri (RPM) ve gaz tepkisi verilerini
 okur ve aracın hoparlörlerine senkronize bir "Sci-Fi hum" (uzay gemisi
 motor sesi) yayar. Müziğin altından hissedilecek şekilde, çok düşük
 volümde, fütüristik bir atmosfer yaratır.

 🚀 "SCI-FI SOUNDSPACE" MANTIĞI — GOD MODE:
 =============================================================================
 Gece sürüşünde veya tünel geçişinde:
 - Motor RPM yükseldikçe → Sci-Fi hum frekansı yükselir
 - Gaz bırakıldığında → hum frekansı düşer (idle hum)
 - Müzikten AYRI olarak çalar — "duyulmaz ama hissedilir"
 - Sürücü "uzay gemisi sürüyor" hissi → "God Mode"

 "Premium bir araç bir uzay gemisi gibi ses çıkarır."
 Gerçek motor sesi + fütüristik hum = "sci-fi cockpit" deneyimi.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio numpy sounddevice

 =============================================================================
"""

import asyncio
import time
import math
from typing import Optional

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")

try:
    import numpy as np
except ImportError:
    raise ImportError("numpy gerekli: pip install numpy")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class SciFiSoundspaceConfig:
    """Sci-Fi Soundspace konfigürasyonu."""

    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # OBD2 okuma aralığı (saniye)
    OBD2_POLL_INTERVAL: float = 0.5  # 500ms — RPM değişimini yakala

    # Ses parametreleri
    SAMPLE_RATE: int = 44100          # CD kalitesi
    BASE_FREQ_IDLE: float = 55.0      # Idle hum frekansı (Hz) — düşük bas
    BASE_FREQ_MAX: float = 220.0      # Maks RPM'de frekans (Hz) — orta bas
    VOLUME: float = 0.08              # %8 — çok düşük (müzikten ayrı)
    WAVEFORM: str = "sawtooth"        # Testere dalga — "fütüristik" his

    # RPM aralığı
    RPM_IDLE: int = 800               # Idle RPM
    RPM_MAX: int = 6500               # Maks RPM

    # Aktif olma koşulları
    NIGHT_ONLY: bool = True           # Sadece gece (after sunset)
    TUNNEL_BOOST: bool = True         # Tünelde boost (GPS + harita)


# =============================================================================
# SCI-FI SOUNDSPACE AUGMENTER
# =============================================================================

class SciFiSoundspaceAugmenter:
    """
    OBD2 RPM verisinden fütüristik uzay gemisi sesi üretir.

    🚀 "GOD MODE" MANTIĞI:
    =============================================================================
    Sürücü gaz verir → RPM yükselir → Sci-Fi hum frekansı yükselir.
    Sürücü gaz bırakır → RPM düşer → hum idle frekansına döner.
    Müzikten AYRI olarak çalar — "duyulmaz ama hissedilir".

    "Premium bir araç bir uzay gemisi gibi ses çıkarır."
    Gerçek motor sesi + fütüristik hum = "sci-fi cockpit" deneyimi.
    Sürücü "God Mode" hisseder — araç bir araç değil, bir uzay gemisi.

    Ses üretimi:
    - Sawtooth dalga (testere) → "fütüristik/mekanik" his
    - RPM → frekans mapping (idle 55Hz → max 220Hz)
    - Volume %8 → müzikten ayrı, "hissedilir ama duyulmaz"
    - Gece only → gündüz gereksiz (trafikte dikkat dağıtır)
    """

    def __init__(self, config: SciFiSoundspaceConfig = None):
        self.config = config or SciFiSoundspaceConfig()
        self.ha_client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
            timeout=3.0,
        )

        # Mevcut RPM
        self._current_rpm: int = 0
        self._target_freq: float = self.config.BASE_FREQ_IDLE
        self._current_freq: float = self.config.BASE_FREQ_IDLE
        self._is_active: bool = False

        print("[SciFiSoundspace] Fütüristik Ses Modülü başlatıldı (2026)")

    # =========================================================================
    # OBD2'DEN RPM OKU
    # =========================================================================
    async def read_rpm(self) -> int:
        """HA'dan OBD2 RPM sensörünü oku."""
        try:
            resp = await self.ha_client.get("/api/states/sensor.car_rpm")
            if resp.status_code == 200:
                return int(float(resp.json().get("state", 0)))
        except Exception:
            pass
        return 0

    # =========================================================================
    # GECE Mİ? (Sci-Fi ses sadece gece)
    # =========================================================================
    async def is_night(self) -> bool:
        """HA'dan güneş durumunu kontrol et."""
        try:
            resp = await self.ha_client.get("/api/states/sun.sun")
            if resp.status_code == 200:
                return resp.json().get("state") == "below_horizon"
        except Exception:
            pass
        return True  # Varsayılan: gece

    # =========================================================================
    # RPM → FREKANS MAPPING
    # =========================================================================
    def rpm_to_freq(self, rpm: int) -> float:
        """
        RPM'i Sci-Fi hum frekansına map'le.

        🚀 MANTIK:
        - Idle (800 RPM) → 55 Hz (düşük bas hum — "uzay gemisi idle")
        - Maks (6500 RPM) → 220 Hz (orta bas — "uzay gemisi turbo")
        - Linear mapping + hafif exponential curve → "fütüristik" his

        Frekans aralığı: 55-220 Hz → insan vücudunda hissedilebilir
        (göğüs kafesi rezonansı ~60-100 Hz). "Hissedilir ama duyulmaz."
        """
        if rpm <= self.config.RPM_IDLE:
            return self.config.BASE_FREQ_IDLE

        # Normalize: 0.0 (idle) → 1.0 (max)
        normalized = (rpm - self.config.RPM_IDLE) / (self.config.RPM_MAX - self.config.RPM_IDLE)
        normalized = max(0.0, min(1.0, normalized))

        # Hafif exponential curve → "turbo" hissi
        curved = normalized ** 1.5

        # Frekans hesapla
        freq = self.config.BASE_FREQ_IDLE + curved * (self.config.BASE_FREQ_MAX - self.config.BASE_FREQ_IDLE)
        return freq

    # =========================================================================
    # SES ÜRET — MQTT → Araç Hoparlörü
    # =========================================================================
    async def emit_sci_fi_hum(self, freq: float) -> None:
        """
        Fütüristik hum sesini araç hoparlörüne gönder.

        🚀 MANTIK:
        - MQTT → araç içi ses sunucusu (Pi Zero / Android)
        - Sunucu, sawtooth dalga üretir → hoparlör
        - Volume %8 → müzikten ayrı, "hissedilir ama duyulmaz"

        Frekans değiştikçe → hum pitch'i değişir → "motor tepkisi" hissi.
        """
        # MQTT ile frekans + volume gönder
        # Araç içi ses sunucusu (Python sounddevice / Android AudioTrack) dinler
        await self._publish_mqtt(
            "jarvis/car/scifi_freq",
            f"{freq:.1f}"
        )
        await self._publish_mqtt(
            "jarvis/car/scifi_volume",
            f"{self.config.VOLUME}"
        )

    # =========================================================================
    # MQTT PUBLISH
    # =========================================================================
    async def _publish_mqtt(self, topic: str, payload: str) -> None:
        """HA üzerinden MQTT publish."""
        try:
            await self.ha_client.post(
                "/api/services/mqtt/publish",
                json={"topic": topic, "payload": payload}
            )
        except Exception:
            pass

    # =========================================================================
    # ANA DÖNGÜ — RPM → Frekans → Ses
    # =========================================================================
    async def run_soundspace_loop(self) -> None:
        """
        Sürekli döngü: 500ms'de bir RPM oku → frekans hesapla → ses gönder.

        🚀 "GOD MODE" DÖNGÜSÜ:
        Sürücü gaz verir → 500ms sonra hum frekansı yükselir.
        Sürücü gaz bırakır → 500ms sonra hum idle'a döner.
        "Motor tepkisi" hissi → "uzay gemisi sürüyor" deneyimi.

        Gece only → gündüz çalışmaz (trafikte dikkat dağıtır).
        """
        print("[SciFiSoundspace] Ses döngüsü başlatıldı (500ms aralık)")

        while True:
            try:
                # Gece mi?
                if self.config.NIGHT_ONLY:
                    night = await self.is_night()
                    if not night:
                        # Gündüz → sessiz
                        if self._is_active:
                            await self._publish_mqtt("jarvis/car/scifi_volume", "0")
                            self._is_active = False
                        await asyncio.sleep(5)
                        continue

                # RPM oku
                rpm = await self.read_rpm()

                # Frekans hesapla
                self._target_freq = self.rpm_to_freq(rpm)

                # Yumuşak geçiş (frekans değişimi ani değil)
                freq_diff = self._target_freq - self._current_freq
                self._current_freq += freq_diff * 0.3  # %30 adım → yumuşak

                # Ses gönder
                await self.emit_sci_fi_hum(self._current_freq)

                if not self._is_active:
                    self._is_active = True
                    print(f"[SciFiSoundspace] 🚀 Aktif — RPM: {rpm} → Freq: {self._current_freq:.1f}Hz")
                else:
                    # Sadece önemli değişimlerde log
                    if abs(freq_diff) > 10:
                        print(f"[SciFiSoundspace] RPM: {rpm} → Freq: {self._current_freq:.1f}Hz")

            except Exception as e:
                print(f"[SciFiSoundspace] Döngü hatası: {e}")

            await asyncio.sleep(self.config.OBD2_POLL_INTERVAL)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.ha_client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Sci-Fi Soundspace test."""
    augmenter = SciFiSoundspaceAugmenter()

    # Test: RPM → Frekans mapping
    for rpm in [800, 1500, 3000, 5000, 6500]:
        freq = augmenter.rpm_to_freq(rpm)
        print(f"RPM: {rpm} → Freq: {freq:.1f} Hz")

    await augmenter.close()


if __name__ == "__main__":
    asyncio.run(main())