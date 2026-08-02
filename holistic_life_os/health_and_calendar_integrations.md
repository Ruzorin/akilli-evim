# holistic_life_os — Sağlık, Takvim ve Biyometrik Entegrasyonlar

> **Modül 16: Holistic Life OS (Yaşam İşletim Sistemi)**
> Kullanıcının akıllı saati, takvimi ve yatak altı radarı ile entegre çalışarak; kan değerleri, kalori, uyku ve günlük rutinleri takip eden proaktif bir yaşam koçu.
>
> ⚠️ **ÖNEMLİ SENSÖR DÜZELTMESİ:**
> LD2450/LD2410 mmWave radar **kalp atışı ve nefes ölçmez**. Sadece varlık/hareket algılar.
> Kalp atışı (BPM), nefes ve uyku evreleri **akıllı saatten** (Apple Health/Google Fit) gelir.
> Radar (LD2410) sadece "odada biri var mı?" ve "aktivite seviyesi" için kullanılır.
>
> **Sensör Doğruluk Tablosu:**
> - LD2410 / LD2450: Varlık/hareket only. Kalp/nefes ÖLÇMEZ.
> - LD2420: 24GHz — varlık/hareket only. Kalp/nefes ÖLÇMEZ.
> - LD6001: 60GHz — çoklu kişi takibi + konum. Kalp/nefes ÖLÇMEZ.
> - **LD6002: 60GHz — temassız kalp atışı (BPM) + solunum ölçer. ✅ BU sensör kalp atışı ölçer.**
> - MR60BHA2: 60GHz — temassız kalp atışı + solunum. ✅ Alternatif.
>
> Eğer radar tabanlı kalp atışı ölçümü istenirse: **HLK-LD6002** (60GHz Vital Signs Radar)
> yatak başucuna monte edilir (1m mesafe, göğüs hizası). ESPHome topluluğunda hazır YAML mevcuttur.

---

## 📅 Takvim Entegrasyonu (CalDAV / Google Calendar)

### Yöntem 1: CalDAV (Evrensel — iCloud, Nextcloud, vb.)

```
1. HA → Settings → Devices → Add → CalDAV
2. CalDAV sunucu bilgilerini gir:
   - iCloud: https://caldav.icloud.com
   - Nextcloud: https://your-nextcloud.com/remote.php/dav
   - Google: https://www.google.com/calendar/dav/your@gmail.com/events
3. Kullanıcı adı ve şifre (app-specific password gerekir)
4. HA, takvim etkinliklerini sensor olarak oluşturur:
   - calendar.personal → sonraki etkinlik
   - sensor.calendar_personal_event_1 → etkinlik adı, saati, konumu
5. Test: sensor.calendar_personal_event_1.state → "Team Meeting"
```

### Yöntem 2: Google Calendar (Resmi HA Entegrasyonu)

```
1. Google Cloud Console → proje oluştur
2. Google Calendar API etkinleştir
3. OAuth 2.0 credentials oluştur (Client ID + Secret)
4. HA → Settings → Devices → Add → Google Calendar
5. Google hesabınla yetkilendir
6. calendar.personal ve calendar.work entity'leri oluşur
7. Her takvim için sonraki 5 etkinlik sensor olarak gelir
```

### Takvim Verisinin Jarvis'e Aktarımı

```
Takvim → HA sensor → MQTT → jarvis_core Python
  sensor.calendar_personal_event_1 → "Team Meeting 10:00-11:00"
  → MQTT: jarvis/context/calendar → {"event": "Team Meeting", "start": "10:00", "end": "11:00"}
  → Gemini 3.5 bağlamına eklenir → Jarvis "10:00'da toplantınız var" bilir
```

---

## ⌚ Akıllı Saat Entegrasyonu (Apple Health / Google Fit)

### Mimari: Akıllı Saat → Webhook → HA → Jarvis

```
Apple Watch / Wear OS
    ↓ (Apple Health / Google Fit API)
iOS Shortcuts / Android Automation
    ↓ (HTTP POST webhook)
Home Assistant Webhook
    ↓ (sensor olarak)
Jarvis Core 3.0 (Gemini 3.5 bağlam)
```

### Apple Health → HA Webhook

```
1. iPhone'da "Shortcuts" app'ini aç
2. Yeni shortcut oluştur: "Health to HA"
3. Aşağıdaki verileri al:
   - Son gece uyku süresi (Sleep Analysis)
   - Günün adım sayısı (Step Count)
   - Dinlenme nabzı (Resting Heart Rate)
   - Aktif kalori (Active Energy)
4. HTTP POST ile HA webhook'a gönder:
   URL: http://HA_URL/api/webhook/health_data
   Body: {
     "sleep_hours": 6.5,
     "sleep_quality": "poor",
     "deep_sleep_hours": 0.8,
     "steps": 4200,
     "resting_hr": 72,
     "active_calories": 380
   }
5. Otomasyon: Her sabah 07:00'de otomatik çalış
6. HA'da sensor'lar oluştur:
   - sensor.sleep_hours → 6.5
   - sensor.sleep_quality → poor
   - sensor.deep_sleep_hours → 0.8
   - sensor.daily_steps → 4200
   - sensor.resting_hr → 72
   - sensor.active_calories → 380
```

### Google Fit → HA Webhook

```
1. Google Fit API'yi etkinleştir (Google Cloud Console)
2. OAuth 2.0 ile erişim al
3. Python script (Raspberry Pi 4'te cron ile çalışır):
   - Her sabah 07:00'de Google Fit API'den veri çek
   - Uyku, adım, nabız, kalori verilerini al
   - HA webhook'a POST gönder
4. HA'da aynı sensor'lar oluşur
```

### Veri Akışı

```
Akıllı Saat → Health API → Webhook → HA Sensor → MQTT → Jarvis
  ↓                                    ↓
  Uyku: 6.5 saat (kötü)          Gemini 3.5 bağlam:
  Derin uyku: 0.8 saat           "Kullanıcı dün gece 6.5 saat uyudu,
  Adım: 4200                      derin uyku sadece 0.8 saat.
  Nabız: 72 BPM                  Bugün yorgun olabilir."
  Kalori: 380
```

---

## 🩸 Kan Tahlili PDF Analizi (Gemini 3.5)

### Mantık

```
Kullanıcı kan tahlili PDF'ini yükler
  ↓
HA webhook → PDF → Python (PyPDF2) → metin çıkar
  ↓
Metin → Gemini 3.5 (2M token bağlam) → analiz
  ↓
Jarvis: "Demir değeriniz düşük (32 μg/dL, referans 50-170).
         B12 seviyesi normal ama alt sınırda.
         D vitamini eksik (18 ng/mL, referans 30-100).
         Öneri: D vitamini takviyesi, demir açısından zengin besinler."
```

### Kurulum

```
1. HA → File Upload (HA Companion App veya web arayüzü)
2. PDF → /config/uploads/blood_test.pdf
3. Python script (Raspberry Pi 4):
   - PyPDF2 ile PDF'ten metin çıkar
   - Metni Gemini 3.5'e gönder (system prompt: "Kan tahlili analiz et")
   - Gemini 3.5: değerleri referans aralıklarıyla karşılaştır
   - Sonucu MQTT'ye publish: jarvis/health/blood_analysis
4. HA, MQTT'yi dinler → Jarvis TTS ile sonucu okur
5. Sonuç ChromaDB'ye kaydedilir (geçmiş takip için)
```

### Gemini 3.5 Analiz Prompt'u

```
Sen bir tıbbi analiz asistanısın (doktor değilsin).
Aşağıdaki kan tahlili sonuçlarını analiz et:
1. Her değeri referans aralığıyla karşılaştır
2. Düşük/yüksek değerleri işaretle
3. Basit, anlaşılır dille özetle
4. Beslenme/takviye önerileri ver (doktor tavsiyesi değil)
5. Kullanıcının hedeflerini bil → sağlık gereksinimleri

Format:
- Düşük/Yüksek değerler: ⚠️
- Normal değerler: ✅
- Öneriler: 💡
```

### Güvenlik

```
🚨 Kan tahlili verileri son derece hassastır:
- PDF LOKAL işlenir (Raspberry Pi 4'te)
- Metin Gemini 3.5'e gönderilir ama SAKLANMAZ (API'de tutulmaz)
- Sonuç ChromaDB'ye LOKAL kaydedilir
- Hiçbir sağlık verisi buluta kalıcı olarak gönderilmez
- Jarvis "doktor" değildir — tavsiyeler bilgilendirme amaçlıdır
```

---

## 📋 Gerekli Ek Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Saat | Apple Watch SE / Wear OS | 1 | ~$200 | Kullanıcının mevcut saati |
| 2 | (Opsiyonel) | Google Fit API erişimi | — | $0 | Wear OS saati varsa |
| 3 | (Yazılım) | PyPDF2 (PDF analiz) | — | $0 | pip install pypdf2 |
| 4 | (Yazılım) | Google Calendar API | — | $0 | Ücretsiz |

> **Not:** Bu modül EKSTRA DONANIM GEREKTİRMEZ — mevcut akıllı saat + HA altyapısı yeterli. Sadece yazılım entegrasyonu yapılır.

---

## ✅ Kurulum Kontrol Listesi

- [ ] CalDAV veya Google Calendar HA'a entegre edildi
- [ ] Akıllı saat → HA webhook → sensor'lar oluşturuldu
- [ ] Uyku, adım, nabız, kalori verileri HA'a geliyor
- [ ] Kan tahlili PDF analizi Python script'i kuruldu
- [ ] Gemini 3.5 API anahtarı ayarlandı
- [ ] biometric_fusion_engine.py Raspberry Pi 4'te çalışıyor
- [ ] routine_and_medical_tracker.yaml HA'a yüklendi
- [ ] life_coach_prompt_extension.md Jarvis system prompt'a eklendi
- [ ] Test: Kötü uyku → Jarvis "Bugün yorgun görünüyorsunuz" + takvim esnetme önerisi
- [ ] Test: Gece 02:00 + ışıklar açık + sabah sınav → Jarvis "Uyku moduna geçiyorum"
- [ ] Test: "Bu yemeği kalori takibime ekle" → Vision API + kalori bilgisi