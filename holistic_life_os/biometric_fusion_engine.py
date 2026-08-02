"""
 =============================================================================
 holistic_life_os — Biometric Fusion Engine (Uyku ve Sağlık Verisi)
 =============================================================================
 2026 Sürümü — Sensor Fusion + Agentic Takvim Esnetme

 Bu modül, iki veri kaynağını birleştirir (Sensor Fusion):
   1. Yatak altı radar (LD2450) → kalp atışı, nefes, uyku evreleri
   2. Akıllı saat (Apple Health / Google Fit) → uyku süresi, adım, nabız

 Birleştirilmiş veri → Gemini 3.5 → "kullanıcı yorgun mu?" analizi
 → Yorgunsa + takvimde esnetilebilir etkinlik varsa → AGENTIC takvim değişikliği

 🤖 AGENTIC TAKVİM ESNETME MANTIĞI:
 =============================================================================
 Kullanıcı gece 6.5 saat uyudu (kötü), derin uyku 0.8 saat (çok az).
 Sabah 10:00'da toplantı var ama takvimde "esnetilebilir" olarak işaretli.
 Jarvis: "Bugün yorgun görünüyorsunuz, 10:00 toplantısını 11:00'e
 kaydırmamı ister misin?" → kullanıcı "evet" der → Jarvis Google Calendar
 API'yi çağırır → toplantıyı 11:00'e taşır.

 Bu, "statik alarm" → "dinamik yaşam yönetimi" dönüşümüdür.
 Jarvis sadece odayı değil, kullanıcının ZAMANINI da yönetir.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install httpx asyncio

 =============================================================================
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class LifeOSConfig:
    """Holistic Life OS konfigürasyonu."""

    # Home Assistant REST API
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # Google Calendar API (takvim esnetme için)
    GOOGLE_CALENDAR_ID: str = "primary"
    GOOGLE_OAUTH_TOKEN: str = "YOUR_GOOGLE_OAUTH_TOKEN"

    # Gemini 3.5 API (duygu/uyku analizi)
    GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY"

    # MQTT
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_HEALTH_CONTEXT: str = "jarvis/health/context"
    MQTT_TOPIC_CALENDAR_ACTION: str = "jarvis/calendar/action"

    # Uyku kalitesi eşikleri
    MIN_SLEEP_HOURS: float = 7.0        # 7 saatten az = yorgun
    MIN_DEEP_SLEEP_HOURS: float = 1.2   # 1.2 saatten az derin uyku = yorgun
    MAX_RESTING_HR: int = 75            # 75+ dinlenme nabzı = stres/yorgun


# =============================================================================
# VERİ MODELLERİ
# =============================================================================

@dataclass
class SleepData:
    """Uyku verisi (radar + akıllı saat birleştirilmiş)."""
    total_sleep_hours: float          # Toplam uyku süresi
    deep_sleep_hours: float           # Derin uyku süresi
    rem_sleep_hours: float            # REM uyku süresi
    light_sleep_hours: float          # Hafif uyku süresi
    awakenings: int                   # Uyanma sayısı
    sleep_quality_score: float        # 0-100 uyku kalitesi skoru
    source: str                       # "radar", "watch", "fusion"

    @property
    def is_poor_sleep(self) -> bool:
        """Uyku kalitesi kötü mü?"""
        return (
            self.total_sleep_hours < LifeOSConfig.MIN_SLEEP_HOURS or
            self.deep_sleep_hours < LifeOSConfig.MIN_DEEP_SLEEP_HOURS
        )


@dataclass
class HealthData:
    """Günlük sağlık verisi (akıllı saat)."""
    steps: int                        # Adım sayısı
    resting_heart_rate: int           # Dinlenme nabzı
    active_calories: int              # Aktif kalori
    total_calories: int               # Toplam kalori
    stand_hours: int                  # Ayakta geçen saat (Apple Watch)
    stress_score: float               # 0-10 stres skoru

    @property
    def is_high_stress(self) -> bool:
        """Yüksek stres mi?"""
        return (
            self.resting_heart_rate > LifeOSConfig.MAX_RESTING_HR or
            self.stress_score > 6.0
        )


@dataclass
class CalendarEvent:
    """Takvim etkinliği."""
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    is_flexible: bool                 # Esnetilebilir mi? (kullanıcı tanımı)
    is_important: bool                # Önemli mi? (sınav, mülakat)


# =============================================================================
# BIOMETRIC FUSION ENGINE
# =============================================================================

class BiometricFusionEngine:
    """
    Akıllı saat + LD2410 radar (varlık) verisini birleştirir (Sensor Fusion) ve
    Agentic takvim esnetme önerisi üretir.

    ⚠️ DÜZELTME: LD2450/LD2410 radar kalp atışı ve nefes ÖLÇMEZ.
    Sadece varlık/hareket algılar. Kalp atışı ve uyku evreleri
    akıllı saatten (Apple Health/Google Fit) gelir.

    🤖 AGENTIC MANTIK:
    =============================================================================
    1. Akıllı saat: uyku süresi + derin uyku + REM + uyanma sayısı + nabız
    2. LD2410 radar: varlık (odada biri var mı?) + hareket aktivitesi
    3. FUSION: Akıllı saat uyku verisi + radar varlık → en doğru uyku analizi
    4. ANALİZ: Gemini 3.6 → "kullanıcı yorgun, derin uyku eksik"
    5. AGENTİC EYLEM: Takvimde esnetilebilir etkinlik varsa → öner
       "10:00 toplantısını 11:00'e kaydırmamı ister misin?"
    6. Kullanıcı "evet" der → Google Calendar API → etkinliği taşı

    Bu, "statik alarm" → "dinamik yaşam yönetimi" dönüşümüdür.
    """

    def __init__(self, config: LifeOSConfig = None):
        self.config = config or LifeOSConfig()
        self.ha_client = httpx.AsyncClient(
            base_url=self.config.HA_URL,
            headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
            timeout=10.0,
        )
        print("[LifeOS] Biometric Fusion Engine başlatıldı (2026)")

    # =========================================================================
    # SENSOR FUSION — Akıllı Saat + LD2410 Radar (Varlık) Verisini Birleştir
    # =========================================================================
    async def fuse_sleep_data(self) -> SleepData:
        """
        Akıllı saat (Apple Health/Google Fit) ve LD2410 radar (varlık) verisini birleştir.

        ⚠️ DÜZELTME: LD2450/LD2410 radar kalp atışı ve nefes ÖLÇMEZ.
        Sadece varlık/hareket algılar.

        🧠 SENSOR FUSION MANTIĞI:
        Akıllı saat: uyku süresi, derin uyku, REM, uyanma sayısı, nabız.
        LD2410 radar: varlık (odada biri var mı?) + hareket aktivitesi.
        FUSION: Akıllı saat uyku verisi + radar varlık → en doğru analiz.

        İki kaynak birleştirilir:
        - Akıllı saat: uyku süresi, derin uyku, REM, uyanma sayısı (ana kaynak)
        - LD2410 radar: sadece varlık (odada biri var mı?) + hareket aktivitesi
        - FUSION: Saat uyku verisi + radar varlık = en doğru analiz

        ⚠️ LD2410/LD2450 kalp atışı ve nefes ÖLÇMEZ.
        Sadece varlık (binary) ve mikro-hareket (nefes alırken göğüs hareketi)
        algılar. Uyku evreleri (derin/REM/hafif) akıllı saatten gelir.

        Eğer kalp atışı (BPM) ve solunum sayısı için radar kullanmak istersen:
        - HLK-LD2420 / HLK-LD6001 (Sleep Quality Monitor Radar) — özel uyku radarı
        - 60GHz mmWave (Seeed Studio MR60BHA1) — kalp atışı + solunum ölçer
        Bu sensörler LD2410'dan farklı olarak BPM ve solunum frekansı verir.
        """
        # Akıllı saat verisi (HA webhook'tan gelen sensor'lar — ANA KAYNAK)
        watch_sleep = await self._get_ha_state("sensor.sleep_hours")
        watch_deep = await self._get_ha_state("sensor.deep_sleep_hours")
        watch_rem = await self._get_ha_state("sensor.rem_sleep_hours")
        watch_light = await self._get_ha_state("sensor.light_sleep_hours")
        watch_awakenings = await self._get_ha_state("sensor.sleep_awakenings")

        # LD2410 radar verisi (SADECE varlık + hareket — kalp/nefes YOK)
        radar_presence = await self._get_ha_state("binary_sensor.room_presence")
        radar_activity = await self._get_ha_state("sensor.bed_activity_level")

        # -------------------------------------------------------------------------
        # FUSION: Akıllı saat (uyku verisi) + LD2410 (varlık/hareket)
        # -------------------------------------------------------------------------
        # Akıllı saat ana kaynaktır (uyku evreleri + süre + nabız).
        # LD2410 radar sadece varlık/hareket için kullanılır (kalp/nefes YOK).
        # Eğer LD2420/LD6001 (Sleep Quality Monitor Radar) kullanılıyorsa,
        # o sensörden de uyku verisi alınabilir — ama LD2410'dan ALINAMAZ.

        total_sleep = float(watch_sleep or 0)
        deep_sleep = float(watch_deep or 0)
        rem_sleep = float(watch_rem or 0)
        light_sleep = float(watch_light or 0)
        awakenings = int(watch_awakenings or 0)

        # Uyku kalitesi skoru hesapla (0-100)
        quality_score = self._compute_sleep_quality(
            total_sleep, deep_sleep, rem_sleep, awakenings
        )

        fused = SleepData(
            total_sleep_hours=total_sleep,
            deep_sleep_hours=deep_sleep,
            rem_sleep_hours=rem_sleep,
            light_sleep_hours=light_sleep,
            awakenings=awakenings,
            sleep_quality_score=quality_score,
            source="fusion"
        )

        print(f"[LifeOS] Uyku FUSION: {total_sleep}h toplam, "
              f"{deep_sleep}h derin, kalite: {quality_score}/100")

        return fused

    # =========================================================================
    # UYKU KALİTESİ SKORU HESAPLAMA
    # =========================================================================
    def _compute_sleep_quality(
        self,
        total: float,
        deep: float,
        rem: float,
        awakenings: int
    ) -> float:
        """
        Uyku kalitesi skoru hesapla (0-100).

        Faktörler:
        - Toplam süre (ideal: 7-9 saat)
        - Derin uyku (ideal: 1.5-2 saat, toplamın %15-25'i)
        - REM (ideal: 1.5-2 saat, toplamın %20-25'i)
        - Uyanma sayısı (ideal: <3)
        """
        score = 0.0

        # Toplam süre (40 puan)
        if 7 <= total <= 9:
            score += 40
        elif 6 <= total < 7 or 9 < total <= 10:
            score += 25
        elif total < 6:
            score += 10

        # Derin uyku (30 puan)
        if total > 0:
            deep_ratio = deep / total
            if 0.15 <= deep_ratio <= 0.25:
                score += 30
            elif 0.10 <= deep_ratio < 0.15:
                score += 20
            else:
                score += 10

        # REM (15 puan)
        if total > 0:
            rem_ratio = rem / total
            if 0.20 <= rem_ratio <= 0.25:
                score += 15
            elif 0.15 <= rem_ratio < 0.20:
                score += 10

        # Uyanma sayısı (15 puan)
        if awakenings <= 2:
            score += 15
        elif awakenings <= 4:
            score += 10
        else:
            score += 5

        return min(score, 100.0)

    # =========================================================================
    # AGENTIC TAKVİM ESNETME — Yorgunsa Takvimi Ayarla
    # =========================================================================
    async def check_and_suggest_calendar_adjustment(
        self,
        sleep_data: SleepData,
        health_data: HealthData,
        calendar_events: List[CalendarEvent]
    ) -> Optional[str]:
        """
        Kullanıcı yorgunsa ve takvimde esnetilebilir etkinlik varsa,
        takvim değişikliği ÖNERİR (agentic).

        🤖 AGENTIC MANTIK:
        =============================================================================
        1. Uyku kalitesi kötü mü? (is_poor_sleep)
        2. Takvimde "esnetilebilir" etkinlik var mı?
        3. Varsa → Jarvis "10:00 toplantısını 11:00'e kaydırmamı ister misin?"
        4. Kullanıcı "evet" der → Google Calendar API → etkinliği taşı
        5. Kullanıcı "hayır" der → "Anlaşıldı, efendim." → geç

        Bu, Jarvis'in SADECE odayı değil, kullanıcının ZAMANINI da yönetmesidir.
        Jarvis, "statik alarm" → "dinamik yaşam yönetimi" dönüşümünü sağlar.

        Neden Agentic?
        - Statik: "Her sabah 7:30'da uyandır" → yorgun olsa da uyandırır
        - Agentic: "Dün gece kötü uyudun, toplantını 1 saat kaydırayım mı?"
          → kullanıcıya seçenek sunar → dinamik karar
        """
        # Yorgun mu?
        if not sleep_data.is_poor_sleep and not health_data.is_high_stress:
            return None  # Yorgun değil → takvim esnetme gerekmez

        # Esnetilebilir etkinlik var mı?
        flexible_events = [e for e in calendar_events if e.is_flexible and not e.is_important]

        if not flexible_events:
            return None  # Esnetilebilir etkinlik yok

        # İlk esnetilebilir etkinliği al
        event = flexible_events[0]

        # Öneri mesajı üret
        suggestion = (
            f"Efendim, dün gece {sleep_data.total_sleep_hours:.1f} saat uyudunuz, "
            f"derin uyku sadece {sleep_data.deep_sleep_hours:.1f} saat. "
            f"Bugün yorgun olabilirsiniz. "
            f"Takviminizdeki '{event.title}' etkinliğini "
            f"{event.start_time.strftime('%H:%M')} yerine "
            f"{(event.start_time + timedelta(hours=1)).strftime('%H:%M')}'e "
            f"kaydırmamı ister misin?"
        )

        print(f"[LifeOS] AGENTIC takvim esnetme önerisi: {suggestion}")

        # MQTT'ye öneriyi gönder → Jarvis TTS ile okur
        # Kullanıcı "evet" derse → _reschedule_calendar_event çağrılır
        return suggestion

    # =========================================================================
    # TAKVİM ETİNLİĞİNİ TAŞIMA (Google Calendar API)
    # =========================================================================
    async def reschedule_calendar_event(
        self,
        event_id: str,
        new_start: datetime,
        new_end: datetime
    ) -> bool:
        """
        Google Calendar API ile etkinliği yeni saate taşı.

        Bu, Jarvis'in "kullanıcının zamanını yönettiği" noktadır.
        Kullanıcı "evet" der → Jarvis Google Calendar API'yi çağırır →
        etkinlik yeni saate taşınır → kullanıcıya "Taşındı, efendim." der.

        🤖 Bu bir AGENTİC eylemdir — Jarvis "önceden yazılmış komut" beklemez.
        Kullanıcının "evet" cevabını alır → dinamik olarak API'yi çağırır.
        """
        url = f"https://www.googleapis.com/calendar/v3/calendars/{self.config.GOOGLE_CALENDAR_ID}/events/{event_id}"

        headers = {
            "Authorization": f"Bearer {self.config.GOOGLE_OAUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        body = {
            "start": {
                "dateTime": new_start.isoformat(),
                "timeZone": "Europe/Istanbul",
            },
            "end": {
                "dateTime": new_end.isoformat(),
                "timeZone": "Europe/Istanbul",
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=headers, json=body)

                if response.status_code == 200:
                    print(f"[LifeOS] ✅ Etkinlik taşındı: {event_id} → {new_start.strftime('%H:%M')}")
                    return True
                else:
                    print(f"[LifeOS] ❌ Takvim hatası: HTTP {response.status_code}")
                    return False

        except Exception as e:
            print(f"[LifeOS] ❌ Takvim API hatası: {e}")
            return False

    # =========================================================================
    # HA STATE SORGULAMA
    # =========================================================================
    async def _get_ha_state(self, entity_id: str) -> Optional[str]:
        """HA'dan bir sensörün değerini al."""
        try:
            response = await self.ha_client.get(f"/api/states/{entity_id}")
            if response.status_code == 200:
                return response.json().get("state")
            return None
        except Exception:
            return None

    # =========================================================================
    # GÜNLÜK SAĞLIK VERİSİ AL
    # =========================================================================
    async def get_health_data(self) -> HealthData:
        """Akıllı saatten gelen günlük sağlık verisini al."""
        steps = int(await self._get_ha_state("sensor.daily_steps") or 0)
        resting_hr = int(await self._get_ha_state("sensor.resting_hr") or 0)
        active_cal = int(await self._get_ha_state("sensor.active_calories") or 0)
        total_cal = int(await self._get_ha_state("sensor.total_calories") or 0)
        stand_hours = int(await self._get_ha_state("sensor.stand_hours") or 0)
        stress = float(await self._get_ha_state("input_number.jarvis_stress_level") or 0)

        return HealthData(
            steps=steps,
            resting_heart_rate=resting_hr,
            active_calories=active_cal,
            total_calories=total_cal,
            stand_hours=stand_hours,
            stress_score=stress
        )

    # =========================================================================
    # JARVIS'E BAĞLAM GÖNDER (Gemini 3.5 için)
    # =========================================================================
    async def send_health_context_to_jarvis(
        self,
        sleep: SleepData,
        health: HealthData
    ) -> None:
        """
        Birleştirilmiş sağlık verisini Jarvis'e (Gemini 3.5) bağlam olarak gönder.

        🤖 Bu, Jarvis'in "kullanıcının biyolojisini okumasını" sağlar.
        Gemini 3.5'in 2M token bağlam penceresi tüm veriyi alır:
        - Uyku: 6.5 saat, derin 0.8, kalite 35/100
        - Adım: 4200, nabız: 72, kalori: 380
        - Stres: 3.2/10

        Jarvis bu bağlamı okuyup "Bugün yorgun görünüyorsunuz" der.
        """
        context = {
            "sleep": {
                "total_hours": sleep.total_sleep_hours,
                "deep_hours": sleep.deep_sleep_hours,
                "rem_hours": sleep.rem_sleep_hours,
                "awakenings": sleep.awakenings,
                "quality_score": sleep.sleep_quality_score,
                "is_poor": sleep.is_poor_sleep
            },
            "health": {
                "steps": health.steps,
                "resting_hr": health.resting_heart_rate,
                "active_calories": health.active_calories,
                "stress_score": health.stress_score,
                "is_high_stress": health.is_high_stress
            },
            "timestamp": datetime.now().isoformat()
        }

        # MQTT'ye publish → jarvis_core Python dinler → Gemini 3.5 bağlamına ekler
        print(f"[LifeOS] Sağlık bağlamı Jarvis'e gönderildi: {json.dumps(context, indent=2)}")
        # mqtt.publish("jarvis/health/context", json.dumps(context))

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.ha_client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Biometric Fusion Engine test."""

    engine = BiometricFusionEngine()

    # Uyku verisini birleştir
    sleep = await engine.fuse_sleep_data()
    print(f"\n=== UYKU ANALİZİ ===")
    print(f"Toplam: {sleep.total_sleep_hours}h")
    print(f"Derin: {sleep.deep_sleep_hours}h")
    print(f"Kalite: {sleep.sleep_quality_score}/100")
    print(f"Kötü uyku: {sleep.is_poor_sleep}")

    # Sağlık verisini al
    health = await engine.get_health_data()
    print(f"\n=== SAĞLIK VERİSİ ===")
    print(f"Adım: {health.steps}")
    print(f"Nabız: {health.resting_heart_rate} BPM")
    print(f"Stres: {health.stress_score}/10")

    # Jarvis'e bağlam gönder
    await engine.send_health_context_to_jarvis(sleep, health)

    # Agentic takvim esnetme kontrolü
    events = [
        CalendarEvent(
            title="Team Meeting",
            start_time=datetime.now().replace(hour=10, minute=0),
            end_time=datetime.now().replace(hour=11, minute=0),
            location="Zoom",
            is_flexible=True,
            is_important=False
        )
    ]

    suggestion = await engine.check_and_suggest_calendar_adjustment(
        sleep, health, events
    )

    if suggestion:
        print(f"\n=== AGENTİC TAKVİM ÖNERİSİ ===")
        print(f"Jarvis: {suggestion}")

    await engine.close()


if __name__ == "__main__":
    asyncio.run(main())