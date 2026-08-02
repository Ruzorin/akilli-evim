"""
 =============================================================================
 car_omniscience_copilot — Fatigue & Ergonomic Guard (Biyometrik Gözetmen)
 =============================================================================
 2026 Sürümü — PERCLOS + Omurga Stresi + Dalgınlık Müdahalesi

 Bu modül, sürücünün uzun yolculuklardaki bel/omurga stresini (2.10m/125kg
 bağlamında) hesaplar ve PERCLOS (göz kırpma oranı) ile dalgınlığı tespit eder.
 Dalgınlık tespit edildiğinde → HA servis çağrıları ile klima -2°C, difüzör
 nane/limon, koltuk bel desteği şişir.

 🧬 "TANRI KOMPLEKSİ" TİTİZLİĞİ:
 =============================================================================
 Sistem sürücüyü "görür" (IR kamera), "hisseder" (akıllı saat) ve "anlar"
 (Gemini 3.6). Normal → sessiz. Dalgın → uyarı. Kritik → müdahale.
 Sürücü farkında olmadan korunur — "Tanrı" gibi gözetler ama "uşak" gibi
 müdahale eder. Zarif, sessiz, hayat kurtarıcı.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio opencv-python numpy

 =============================================================================
"""

import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class FatigueGuardConfig:
    """Fatigue & Ergonomic Guard konfigürasyonu."""

    # HA REST API
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # Sürücü anatomisi (2.10m / 125kg)
    DRIVER_HEIGHT_CM: int = 210
    DRIVER_WEIGHT_KG: int = 125

    # PERCLOS eşikleri
    PERCLOS_WARNING: float = 0.15    # %15 göz kapalı → uyarı
    PERCLOS_CRITICAL: float = 0.25   # %25 göz kapalı → kritik

    # Omurga stresi eşikleri (sürüş süresine bağlı)
    SPINE_STRESS_WARNING_MIN: int = 90   # 90 dk → uyarı
    SPINE_STRESS_CRITICAL_MIN: int = 150  # 150 dk → kritik

    # Müdahale parametreleri
    CLIMATE_DROP_DEGREES: float = 2.0  # Klima -2°C düşür
    DIFFUSER_SCENT: str = "energize"   # Nane/limon (uyanıklık)


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

class FatigueLevel(Enum):
    """Sürücü dalgınlık seviyesi."""
    ALERT = "alert"          # Uyanık
    MILD = "mild"            # Hafif dalgınlık
    WARNING = "warning"      # Uyarı (PERCLOS > %15)
    CRITICAL = "critical"    # Kritik (PERCLOS > %25)


@dataclass
class DriverState:
    """Sürücü durumu (sensor fusion sonucu)."""
    perclos: float              # Göz kapalı oranı (0.0-1.0)
    yawn_count: int            # Son 5 dk esneme sayısı
    heart_rate: int             # Nabız (akıllı saat)
    hrv: float                  # Kalp atış varyabilitesi (stres göstergesi)
    drive_time_minutes: int     # Sürüş süresi (dk)
    spine_stress_score: float   # Omurga stres skoru (0-100)

    @property
    def fatigue_level(self) -> FatigueLevel:
        """Dalgınlık seviyesi hesapla."""
        if self.perclos >= FatigueGuardConfig.PERCCLOS_CRITICAL:
            return FatigueLevel.CRITICAL
        elif self.perclos >= FatigueGuardConfig.PERCCLOS_WARNING:
            return FatigueLevel.WARNING
        elif self.perclos > 0.08 or self.yawn_count > 3:
            return FatigueLevel.MILD
        else:
            return FatigueLevel.ALERT


# =============================================================================
# FATIGUE & ERGONOMIC GUARD
# =============================================================================

class FatigueErgonomicGuard:
    """
    Sürücü dalgınlığını ve omurga stresini izler, müdahale eder.

    🧬 "TANRI KOMPLEKSİ" MANTIĞI:
    =============================================================================
    Bu sistem sürücüyü "görür" (IR kamera → PERCLOS), "hisseder" (akıllı saat
    → nabız/HRV) ve "anlar" (sürüş süresi → omurga stresi).

    2.10m boy / 125kg için omurga stresi hesaplaması:
    - Uzun boy → bel bölgesine daha fazla yük biner (fiziksel gerçek)
    - 125kg → koltuk bel desteği kritik (anatomik gerçek)
    - Sürüş süresi > 90 dk → omurga stres skoru artar
    - Stres skoru > 70 → koltuk bel desteği şişir (HA → MQTT → koltuk motoru)

    Müdahale hiyerarşisi:
    - ALERT → sessiz (kayıt only)
    - MILD → sessiz (kayıt only)
    - WARNING → klima -2°C + difüzör nane/limon + Jarvis "Mola verin"
    - CRITICAL → tüm uyarılar + koltuk bel desteği şişir + Jarvis "Mola zorunlu"
    """

    def __init__(self, config: FatigueGuardConfig = None):
        self.config = config or FatigueGuardConfig()
        self.ha_client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
            timeout=5.0,
        )
        self._last_intervention_time: float = 0
        self._intervention_cooldown: float = 300  # 5 dk cooldown
        print("[FatigueGuard] Biyometrik Gözetmen başlatıldı (2026)")

    # =========================================================================
    # OMURGA STRESİ HESAPLAMA (2.10m / 125kg bağlamı)
    # =========================================================================
    def compute_spine_stress(self, drive_time_minutes: int) -> float:
        """
        2.10m boy / 125kg için omurga stres skoru hesapla (0-100).

        🧬 BİYOLOJİK BAĞLAM:
        Uzun boy (2.10m) → bel bölgesine binen yük daha fazla.
        125kg → koltuk bel desteği kritik (ağırlık merkezi farklı).
        Sürüş süresi arttıkça → omurga stresi artar.

        Skala:
        - 0-30: rahat (kısa sürüş)
        - 30-60: orta (90+ dk)
        - 60-80: yüksek (120+ dk)
        - 80-100: kritik (150+ dk) → bel desteği şişir
        """
        # Boy faktörü: 2.10m → normalden %30 daha fazla bel yükü
        height_factor = (self.config.DRIVER_HEIGHT_CM - 170) / 40  # 170cm = normal

        # Kilo faktörü: 125kg → normalden %25 daha fazla basınç
        weight_factor = (self.config.DRIVER_WEIGHT_KG - 70) / 55  # 70kg = normal

        # Süre faktörü: 60 dk = 30 puan, 120 dk = 60 puan, 180 dk = 90 puan
        time_factor = min(drive_time_minutes / 2.0, 100)

        # Birleşik stres skoru
        stress = time_factor * (1 + height_factor * 0.3 + weight_factor * 0.25)
        return min(stress, 100.0)

    # =========================================================================
    # PERCLOS HESAPLAMA (IR kamera → göz kırpma oranı)
    # =========================================================================
    async def get_perclos_from_ir_camera(self) -> float:
        """
        IR kameradan PERCLOS (Percentage of Eye Closure) değerini al.

        PERCLOS: Son 1 dakikada gözlerin kapalı olduğu süre oranı.
        - < %8: uyanık
        - %8-15: hafif dalgınlık
        - %15-25: uyarı (müdahale gerekir)
        - > %25: kritik (mola zorunlu)

        IR kamera → GPT-5.6 Vision → göz açık/kapalı tespiti → oran hesapla
        """
        # Gerçek implementasyonda:
        # 1. IR kameradan 10 FPS kare al
        # 2. GPT-5.6 Vision → "göz açık mı kapalı mı?"
        # 3. Son 60 saniyede kapalı oranı = PERCLOS

        # HA'dan sensör oku (Android webhook → HA sensor)
        response = await self.ha_client.get("/api/states/sensor.perclos")
        if response.status_code == 200:
            return float(response.json().get("state", 0))
        return 0.0

    # =========================================================================
    # SÜRÜCÜ DURUMU TOPLA (Sensor Fusion)
    # =========================================================================
    async def gather_driver_state(self) -> DriverState:
        """
        Tüm sensörlerden veri topla → DriverState oluştur (Sensor Fusion).

        Kaynaklar:
        - IR kamera → PERCLOS (göz kırpma oranı)
        - Akıllı saat → nabız, HRV (stres)
        - Sürüş süresi → omurga stres skoru
        """
        perclos = await self.get_perclos_from_ir_camera()

        # Akıllı saat verisi (HA webhook → sensor)
        hr_response = await self.ha_client.get("/api/states/sensor.car_heart_rate")
        heart_rate = int(hr_response.json().get("state", 70)) if hr_response.status_code == 200 else 70

        hrv_response = await self.ha_client.get("/api/states/sensor.car_hrv")
        hrv = float(hrv_response.json().get("state", 50)) if hrv_response.status_code == 200 else 50

        # Sürüş süresi (HA → sensor.car_drive_time)
        time_response = await self.ha_client.get("/api/states/sensor.car_drive_time")
        drive_time = int(time_response.json().get("state", 0)) if time_response.status_code == 200 else 0

        # Omurga stres skoru
        spine_stress = self.compute_spine_stress(drive_time)

        # Esneme sayısı (IR kamera → GPT-5.6 Vision → yawn detection)
        yawn_response = await self.ha_client.get("/api/states/sensor.yawn_count_5min")
        yawn_count = int(yawn_response.json().get("state", 0)) if yawn_response.status_code == 200 else 0

        state = DriverState(
            perclos=perclos,
            yawn_count=yawn_count,
            heart_rate=heart_rate,
            hrv=hrv,
            drive_time_minutes=drive_time,
            spine_stress_score=spine_stress
        )

        print(f"[FatigueGuard] PERCLOS: {perclos:.2f} | HR: {heart_rate} | "
              f"Sürüş: {drive_time}dk | Omurga: {spine_stress:.0f}/100 | "
              f"Seviye: {state.fatigue_level.value}")

        return state

    # =========================================================================
    # MÜDAHALE — Dalgınlık Tespiti → HA Servis Çağrıları
    # =========================================================================
    async def intervene_fatigue(self, state: DriverState) -> None:
        """
        Dalgınlık tespit edildiğinde HA'a müdahale komutları gönder.

        🧬 MÜDAHALE HİYERARŞİSİ ("Tanrı Kompleksi" titizliği):
        - ALERT → sessiz (sürücü uyanık, müdahale yok)
        - MILD → sessiz (hafif dalgınlık, kayıt only)
        - WARNING → klima -2°C + difüzör nane/limon + Jarvis "Mola verin"
        - CRITICAL → tüm uyarılar + koltuk bel desteği şişir + "Mola zorunlu"

        Cooldown: 5 dk (sürekli müdahale etme → sürücüyü rahatsız etme)
        """
        current_time = time.time()

        # Cooldown kontrolü
        if current_time - self._last_intervention_time < self._intervention_cooldown:
            return

        level = state.fatigue_level

        if level == FatigueLevel.ALERT or level == FatigueLevel.MILD:
            return  # Sessiz — müdahale yok

        print(f"[FatigueGuard] ⚠️ MÜDAHALE: {level.value}")

        # -------------------------------------------------------------------------
        # WARNING: Klima -2°C + Difüzör nane/limon + Jarvis uyarı
        # -------------------------------------------------------------------------
        if level == FatigueLevel.WARNING:
            # Klima 2 derece düşür (serin → uyanıklık)
            await self._call_ha_service(
                "climate.set_temperature",
                "climate.car_ac",
                {"temperature": 19, "hvac_mode": "cool"}  # -2°C
            )

            # Difüzör → nane/limon (enerjik, uyanıklık)
            await self._call_ha_service(
                "switch.turn_on",
                "switch.car_diffuser",
                {}
            )

            # Jarvis sesli uyarı
            await self._call_ha_service(
                "tts.speak",
                "tts.jarvis_voice",
                {"message": "Efendim, yorgun görünüyorsunuz. Klimayı serinlettim ve nane kokusu açtım. 15 dakika mola vermenizi öneririm."}
            )

        # -------------------------------------------------------------------------
        # CRITICAL: Tüm uyarılar + Koltuk bel desteği şişir + Mola zorunlu
        # -------------------------------------------------------------------------
        elif level == FatigueLevel.CRITICAL:
            # Klima 2 derece düşür
            await self._call_ha_service(
                "climate.set_temperature",
                "climate.car_ac",
                {"temperature": 18, "hvac_mode": "cool"}
            )

            # Difüzör → nane/limon
            await self._call_ha_service(
                "switch.turn_on",
                "switch.car_diffuser",
                {}
            )

            # Koltuk bel desteği şişir (omurga stresi → bel desteği maksimum)
            # 🧬 2.10m/125kg → bel desteği KRİTİK
            await self._call_ha_service(
                "mqtt.publish",
                None,
                {"topic": "jarvis/car/seat_lumbar", "payload": "100"}  # %100 bel desteği
            )

            # Jarvis sesli uyarı — KRİTİK
            await self._call_ha_service(
                "tts.speak",
                "tts.jarvis_voice",
                {"message": "Efendim, dalgınlık seviyesi kritik. Bel desteğinizi maksimuma çıkardım. Lütfen güvenli bir yerde durun ve mola verin. Bu bir tavsiye değil, bir uyarıdır."}
            )

            # Mobil bildirim (kritik)
            await self._call_ha_service(
                "notify.mobile_app",
                None,
                {
                    "title": "🚨 Dalgınlık Uyarısı",
                    "message": "Kritik dalgınlık tespit edildi. Mola verin!",
                    "data": {"push": {"interruption_level": "critical"}}
                }
            )

        self._last_intervention_time = current_time

    # =========================================================================
    # OMURGA STRESİ MÜDAHALESİ (sürüş süresi > 90 dk)
    # =========================================================================
    async def intervene_spine_stress(self, state: DriverState) -> None:
        """
        Omurga stres skoru yüksekse → koltuk bel desteği şişir.

        🧬 2.10m / 125kg BAĞLAMI:
        Uzun boy + ağır vücut → bel bölgesine binen yük normalden %55 daha fazla.
        Sürüş > 90 dk → omurga stres skoru > 60 → bel desteği şişir.
        Sürüş > 150 dk → stres > 80 → bel desteği maksimum + Jarvis "Oturun, gerinin".
        """
        if state.spine_stress_score > 70:
            # Bel desteği seviyesi = stres skoruna orantılı
            lumbar_level = int(state.spine_stress_score)

            await self._call_ha_service(
                "mqtt.publish",
                None,
                {"topic": "jarvis/car/seat_lumbar", "payload": str(lumbar_level)}
            )

            print(f"[FatigueGuard] 🦴 Omurga stresi: {state.spine_stress_score:.0f}/100 → Bel desteği: {lumbar_level}%")

            if state.spine_stress_score > 85:
                await self._call_ha_service(
                    "tts.speak",
                    "tts.jarvis_voice",
                    {"message": "Efendim, omurga stresiniz yüksek. Bel desteğini maksimuma çıkardım. Bir sonraki mola noktasında gerinmenizi öneririm."}
                )

    # =========================================================================
    # HA SERVİS ÇAĞRISI
    # =========================================================================
    async def _call_ha_service(self, service: str, entity_id: Optional[str], data: dict) -> None:
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
                print(f"[FatigueGuard] ✅ {service} → {entity_id or 'N/A'}")
        except Exception as e:
            print(f"[FatigueGuard] ❌ {service}: {e}")

    # =========================================================================
    # ANA DÖNGÜ
    # =========================================================================
    async def run_guard_loop(self) -> None:
        """
        Sürekli döngü: her 30 saniyede sürücü durumunu kontrol et.

        🧬 "TANRI KOMPLEKSİ":
        Sistem her 30 saniyede sürücüyü "gözler" — sessizce, fark edilmeden.
        Normal → hiçbir şey olmaz. Anomali → müdahale. Kritik → hayat kurtarır.
        """
        print("[FatigueGuard] Gözetmen döngüsü başlatıldı (30sn aralık)")

        while True:
            try:
                state = await self.gather_driver_state()
                await self.intervene_fatigue(state)
                await self.intervene_spine_stress(state)
            except Exception as e:
                print(f"[FatigueGuard] Döngü hatası: {e}")

            await asyncio.sleep(30)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.ha_client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Fatigue & Ergonomic Guard test."""
    guard = FatigueErgonomicGuard()

    # Omurga stres testi (2 saat sürüş)
    stress = guard.compute_spine_stress(120)
    print(f"2 saat sürüş → omurga stres: {stress:.0f}/100")

    await guard.close()


if __name__ == "__main__":
    asyncio.run(main())