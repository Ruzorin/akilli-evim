"""
 =============================================================================
 car_omniscience_copilot — Predictive Maintenance OBD2 (Mekanik Kehanet)
 =============================================================================
 2026 Sürümü — OBD2 verilerinden anomali tespiti ve arıza kehaneti

 Bu modül, OBD2 portundan gelen anlık verileri (MAF sensörü, silindir
 ateşleme gecikmeleri, yağ basıncı, şanzıman sıcaklığı) analiz eder.
 Anomalileri henüz arıza lambası yanmadan tespit edip kullanıcıya sesli
 rapor verir ve bakım takvimine işler.

 🔮 "KEHANET" MANTIĞI:
 =============================================================================
 Normal OBD2 okuyucular: "Arıza lambası yandı → kod oku → tamirciye git."
 Bu sistem: "Arıza lambası henüz yanmadı → ama yağ basıncı trendi düşüyor
 → 500 km içinde yağ bakımı gerekecek → şimdi söyle."

 Bu, "reaktif" → "proaktif kehanet" dönüşümüdür.
 Jarvis, aracın beynini "okur" ve geleceği "görür".

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio numpy

 =============================================================================
"""

import asyncio
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
from collections import deque

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class PredictiveMaintenanceConfig:
    """OBD2 kehanet konfigürasyonu."""

    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # OBD2 veri okuma aralığı (saniye)
    OBD2_POLL_INTERVAL: int = 10  # 10 saniyede bir OBD2 verisi oku

    # Anomali tespiti parametreleri
    TREND_WINDOW_SIZE: int = 30  # Son 30 örneği trend analizi için tut
    ANOMALY_THRESHOLD: float = 2.0  # 2 standart sapma → anomali

    # Kehanet parametreleri
    OIL_PRESSURE_MIN: float = 1.5  # bar — altında → uyarı
    OIL_PRESSURE_CRITICAL: float = 1.0  # bar — altında → kritik
    TRANS_TEMP_MAX: float = 95.0  # °C — üstünde → uyarı
    TRANS_TEMP_CRITICAL: float = 110.0  # °C — üstünde → kritik
    MAF_DEVIATION_PCT: float = 15.0  # %15 sapma → anomali
    MISFIRE_THRESHOLD: int = 5  # 5+ ateşleme hatası → uyarı


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

class MaintenanceLevel(Enum):
    """Bakım/kehanet seviyesi."""
    NORMAL = "normal"
    WATCH = "watch"        # İzlenmeli (trend bozuk ama kritik değil)
    WARNING = "warning"    # Uyarı (bakım yaklaşıyor)
    CRITICAL = "critical"  # Kritik (bakım acil)


@dataclass
class OBD2Snapshot:
    """OBD2 anlık veri örneği."""
    timestamp: float
    rpm: int                    # Motor devri
    speed: int                  # Hız (km/h)
    maf: float                  # Mass Air Flow (g/s)
    oil_pressure: float         # Yağ basıncı (bar)
    trans_temp: float           # Şanzıman sıcaklığı (°C)
    coolant_temp: float         # Soğutma suyu sıcaklığı (°C)
    misfire_count: int          # Ateşleme hatası sayısı
    fuel_trim: float            # Yakıt trim (%) — karışım oranı
    battery_voltage: float      # Akü voltajı (V)


@dataclass
class Prediction:
    """Kehanet sonucu."""
    component: str              # Hangi parça (yağ, şanzıman, MAF, vb.)
    level: MaintenanceLevel     # Seviye
    message: str                # İnsan dilinde mesaj
    km_estimate: int            # Tahmini kalan km (0 = acil)


# =============================================================================
# PREDICTIVE MAINTENANCE ENGINE
# =============================================================================

class PredictiveMaintenanceOBD2:
    """
    OBD2 verilerinden anomali tespiti ve arıza kehaneti.

    🔮 "KEHANET" MANTIĞI — AGENTIC:
    =============================================================================
    1. OBD2'den 10 saniyede bir veri örneği al
    2. Son 30 örneği trend analizi (standart sapma)
    3. Anomali tespiti: değer normal aralıkta ama trend bozuk → "izlenmeli"
    4. Eşik aşımı: değer kritik eşik altında/üstünde → "uyarı/kehanet"
    5. Jarvis sesli rapor: "Yağ basıncı düşüyor, 500 km içinde bakım"
    6. Bakım takvimine işle (HA → input_datetime → takvim)

    Bu, "reaktif" → "proaktif" dönüşümüdür.
    Jarvis, aracın beynini "okur" ve geleceği "görür".
    """

    def __init__(self, config: PredictiveMaintenanceConfig = None):
        self.config = config or PredictiveMaintenanceConfig()
        self.ha_client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
            timeout=5.0,
        )

        # Trend analizi için veri penceresi (son 30 örnek)
        self._oil_pressure_history: deque = deque(maxlen=config.TREND_WINDOW_SIZE)
        self._trans_temp_history: deque = deque(maxlen=config.TREND_WINDOW_SIZE)
        self._maf_history: deque = deque(maxlen=config.TREND_WINDOW_SIZE)

        # Son kehanet zamanı (cooldown için)
        self._last_prediction_time: float = 0
        self._prediction_cooldown: float = 600  # 10 dk cooldown

        print("[OBD2Oracle] Mekanik Kehanet Motoru başlatıldı (2026)")

    # =========================================================================
    # OBD2 VERİSİ OKU (HA sensörlerinden)
    # =========================================================================
    async def read_obd2_snapshot(self) -> Optional[OBD2Snapshot]:
        """
        HA'dan OBD2 sensörlerini oku → OBD2Snapshot oluştur.

        Veri kaynakları (Android Torque/Car Scanner → Webhook → HA):
        - sensor.car_rpm → Motor devri
        - sensor.car_speed → Hız
        - sensor.car_maf → Mass Air Flow
        - sensor.car_oil_pressure → Yağ basıncı
        - sensor.car_trans_temp → Şanzıman sıcaklığı
        - sensor.car_coolant_temp → Soğutma suyu
        - sensor.car_misfire → Ateşleme hatası
        - sensor.car_fuel_trim → Yakıt trim
        - sensor.car_battery → Akü voltajı
        """
        async def get_state(entity: str, default: float = 0.0) -> float:
            try:
                resp = await self.ha_client.get(f"/api/states/{entity}")
                if resp.status_code == 200:
                    return float(resp.json().get("state", default))
            except Exception:
                pass
            return default

        snapshot = OBD2Snapshot(
            timestamp=time.time(),
            rpm=int(await get_state("sensor.car_rpm")),
            speed=int(await get_state("sensor.car_speed")),
            maf=await get_state("sensor.car_maf"),
            oil_pressure=await get_state("sensor.car_oil_pressure", 3.0),
            trans_temp=await get_state("sensor.car_trans_temp", 80.0),
            coolant_temp=await get_state("sensor.car_coolant_temp", 90.0),
            misfire_count=int(await get_state("sensor.car_misfire")),
            fuel_trim=await get_state("sensor.car_fuel_trim", 0.0),
            battery_voltage=await get_state("sensor.car_battery", 12.5),
        )

        # Trend penceresine ekle
        self._oil_pressure_history.append(snapshot.oil_pressure)
        self._trans_temp_history.append(snapshot.trans_temp)
        self._maf_history.append(snapshot.maf)

        return snapshot

    # =========================================================================
    # ANOMALİ TESPİTİ — Trend Analizi
    # =========================================================================
    def detect_trend_anomaly(self, history: deque, name: str) -> Optional[str]:
        """
        Son N örneğin trendini analiz et → anomali tespit et.

        📊 MANTIK:
        - Standart sapma hesapla
        - Son değer, ortalama ± 2 standart sapma dışında → anomali
        - Trend: son 5 örnek sürekli düşüyor/yükseliyor → trend bozuk

        Bu, "arıza lambası yanmadan" trend bozukluğunu yakalar.
        """
        if len(history) < 10:
            return None

        values = list(history)
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return None

        last_value = values[-1]
        z_score = (last_value - mean) / std_dev

        if abs(z_score) > self.config.ANOMALY_THRESHOLD:
            direction = "yükseliyor" if z_score > 0 else "düşüyor"
            return f"{name} anomali: {last_value:.1f} (ortalama {mean:.1f}, {direction})"

        return None

    # =========================================================================
    # KEHANET — OBD2 Verisinden Gelecek Tahmini
    # =========================================================================
    async def predict_issues(self, snapshot: OBD2Snapshot) -> List[Prediction]:
        """
        OBD2 verisinden arıza kehanetinde bulun.

        🔮 "KEHANET" MANTIĞI:
        Jarvis, aracın beynini "okur" ve geleceği "görür":
        - Yağ basıncı trendi düşüyor → "500 km içinde yağ bakımı"
        - Şanzıman sıcaklığı yükseliyor → "şanzıman yağı kontrol"
        - MAF sapması → "hava filtresi temizliği"
        - Ateşleme hatası → "bujiler kontrol"
        - Yakıt trim sapması → "oksijen sensörü kontrol"

        Bu kehanetler, arıza lambası yanmadan ÖNCE yapılır.
        """
        predictions = []

        # -------------------------------------------------------------------------
        # 1. YAĞ BASINCI KEHANETİ
        # -------------------------------------------------------------------------
        if snapshot.oil_pressure < self.config.OIL_PRESSURE_CRITICAL:
            predictions.append(Prediction(
                component="Yağ Basıncı",
                level=MaintenanceLevel.CRITICAL,
                message=f"Yağ basıncı kritik: {snapshot.oil_pressure:.1f} bar. Acil bakım gerekli.",
                km_estimate=0
            ))
        elif snapshot.oil_pressure < self.config.OIL_PRESSURE_MIN:
            predictions.append(Prediction(
                component="Yağ Basıncı",
                level=MaintenanceLevel.WARNING,
                message=f"Yağ basıncı düşük: {snapshot.oil_pressure:.1f} bar. 500 km içinde yağ bakımı önerilir.",
                km_estimate=500
            ))
        else:
            # Trend analizi — yağ basıncı düşüyor mu?
            trend = self.detect_trend_anomaly(self._oil_pressure_history, "Yağ basıncı")
            if trend and "düşüyor" in trend:
                predictions.append(Prediction(
                    component="Yağ Basıncı",
                    level=MaintenanceLevel.WATCH,
                    message="Yağ basıncı trendi düşüyor. Yakında bakım gerekebilir.",
                    km_estimate=1000
                ))

        # -------------------------------------------------------------------------
        # 2. ŞANZIMAN SICAKLIĞI KEHANETİ
        # -------------------------------------------------------------------------
        if snapshot.trans_temp > self.config.TRANS_TEMP_CRITICAL:
            predictions.append(Prediction(
                component="Şanzıman",
                level=MaintenanceLevel.CRITICAL,
                message=f"Şanzıman sıcaklığı kritik: {snapshot.trans_temp:.0f}°C. Durun ve soğumaya izin verin.",
                km_estimate=0
            ))
        elif snapshot.trans_temp > self.config.TRANS_TEMP_MAX:
            predictions.append(Prediction(
                component="Şanzıman",
                level=MaintenanceLevel.WARNING,
                message=f"Şanzıman sıcaklığı yüksek: {snapshot.trans_temp:.0f}°C. Şanzıman yağı kontrolü önerilir.",
                km_estimate=1000
            ))

        # -------------------------------------------------------------------------
        # 3. MAF (MASS AIR FLOW) KEHANETİ
        # -------------------------------------------------------------------------
        maf_trend = self.detect_trend_anomaly(self._maf_history, "MAF")
        if maf_trend:
            predictions.append(Prediction(
                component="Hava Filtresi",
                level=MaintenanceLevel.WATCH,
                message="MAF sensöründe sapma tespit edildi. Hava filtresi temizliği önerilir.",
                km_estimate=2000
            ))

        # -------------------------------------------------------------------------
        # 4. ATEŞLEME HATASI (MISFIRE) KEHANETİ
        # -------------------------------------------------------------------------
        if snapshot.misfire_count >= self.config.MISFIRE_THRESHOLD:
            predictions.append(Prediction(
                component="Bujiler",
                level=MaintenanceLevel.WARNING,
                message=f"Ateşleme hatası: {snapshot.misfire_count} kez. Bujiler kontrol edilmeli.",
                km_estimate=500
            ))

        # -------------------------------------------------------------------------
        # 5. YAKIT TRIM SAPMASI
        # -------------------------------------------------------------------------
        if abs(snapshot.fuel_trim) > 15.0:
            predictions.append(Prediction(
                component="Oksijen Sensörü",
                level=MaintenanceLevel.WATCH,
                message=f"Yakıt trim sapması: {snapshot.fuel_trim:.1f}%. Oksijen sensörü kontrolü önerilir.",
                km_estimate=2000
            ))

        # -------------------------------------------------------------------------
        # 6. AKÜ VOLTAJI
        # -------------------------------------------------------------------------
        if snapshot.battery_voltage < 11.5:
            predictions.append(Prediction(
                component="Akü",
                level=MaintenanceLevel.WARNING,
                message=f"Akü voltajı düşük: {snapshot.battery_voltage:.1f}V. Akü değişimi önerilir.",
                km_estimate=500
            ))

        return predictions

    # =========================================================================
    # KEHANET RAPORU → JARVIS SESli + Bakım Takvimi
    # =========================================================================
    async def report_predictions(self, predictions: List[Prediction]) -> None:
        """
        Kehanet sonuçlarını Jarvis'e sesli raporla ve bakım takvimine işle.

        🔮 AGENTIC MANTIK:
        Jarvis, kehaneti "görür" ve "söyler":
        - NORMAL → sessiz (kayıt only)
        - WATCH → sessiz (kayıt only, trend izleniyor)
        - WARNING → Jarvis sesli rapor + bakım takvimine işle
        - CRITICAL → Jarvis sesli acil uyarı + mobil bildirim

        Bakım takvimi: HA → input_datetime → Google Calendar → "500 km içinde yağ bakımı"
        """
        current_time = time.time()

        # Cooldown kontrolü
        if current_time - self._last_prediction_time < self._prediction_cooldown:
            return

        warning_or_critical = [p for p in predictions if p.level in (MaintenanceLevel.WARNING, MaintenanceLevel.CRITICAL)]

        if not warning_or_critical:
            return  # Sessiz — normal/watch seviyesi

        print(f"[OBD2Oracle] 🔮 {len(warning_or_critical)} kehanet tespit edildi")

        for pred in warning_or_critical:
            print(f"[OBD2Oracle] {pred.component}: {pred.level.value} → {pred.message}")

            # Jarvis sesli rapor
            await self._call_ha_service(
                "tts.speak",
                "tts.jarvis_voice",
                {"message": pred.message}
            )

            # Bakım takvimine işle (HA → input_datetime)
            if pred.km_estimate > 0:
                await self._call_ha_service(
                    "input_datetime.set_datetime",
                    f"input_datetime.maintenance_{pred.component.lower().replace(' ', '_')}",
                    {"datetime": f"2026-08-15 10:00:00"}  # Tahmini bakım tarihi
                )

            # Kritik ise mobil bildirim
            if pred.level == MaintenanceLevel.CRITICAL:
                await self._call_ha_service(
                    "notify.mobile_app",
                    None,
                    {
                        "title": f"🚨 {pred.component} Kritik",
                        "message": pred.message,
                        "data": {"push": {"interruption_level": "critical"}}
                    }
                )

        self._last_prediction_time = current_time

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
                print(f"[OBD2Oracle] ✅ {service} → {entity_id or 'N/A'}")
        except Exception as e:
            print(f"[OBD2Oracle] ❌ {service}: {e}")

    # =========================================================================
    # ANA DÖNGÜ
    # =========================================================================
    async def run_oracle_loop(self) -> None:
        """
        Sürekli döngü: 10 saniyede bir OBD2 oku → kehanet → rapor.

        🔮 "TANRI KOMPLEKSİ" TİTİZLİĞİ:
        Sistem aracın beynini her 10 saniyede "okur" — sessizce.
        Normal → sessiz. Trend bozuk → izle. Eşik aşımı → kehanet → uyarı.
        Sürücü, arıza lambası yanmadan önce haberdar olur.
        """
        print("[OBD2Oracle] Kehanet döngüsü başlatıldı (10sn aralık)")

        while True:
            try:
                snapshot = await self.read_obd2_snapshot()
                if snapshot:
                    predictions = await self.predict_issues(snapshot)
                    await self.report_predictions(predictions)
            except Exception as e:
                print(f"[OBD2Oracle] Döngü hatası: {e}")

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
    """Predictive Maintenance OBD2 test."""
    oracle = PredictiveMaintenanceOBD2()

    # Test: OBD2 oku
    snapshot = await oracle.read_obd2_snapshot()
    if snapshot:
        print(f"RPM: {snapshot.rpm} | Hız: {snapshot.speed} | "
              f"Yağ: {snapshot.oil_pressure} bar | Şanz: {snapshot.trans_temp}°C")

        # Test: Kehanet
        predictions = await oracle.predict_issues(snapshot)
        for p in predictions:
            print(f"🔮 {p.component}: {p.level.value} → {p.message}")

    await oracle.close()


if __name__ == "__main__":
    asyncio.run(main())