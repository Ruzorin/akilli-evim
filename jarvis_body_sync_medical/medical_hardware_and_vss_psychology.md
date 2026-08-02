# jarvis_body_sync_medical — Medikal Donanım ve VSS Psikolojisi

> **Modül 26: Jarvis Body-Sync Medical (Medikal Kalkan ve Kişisel Yaşam Destek Ünitesi)**
> Kullanıcının nörolojik (Visual Snow Syndrome) ve ortopedik (Skolyoz, postür) ihtiyaçlarını Home Assistant ekosistemi üzerinden otonom olarak yöneten medikal destek modülü.

---

## 👁️ Visual Snow Syndrome (VSS) ve Işık Tetikleyicileri

### VSS Nedir?

Visual Snow Syndrome, görsel alanda sürekli "karıncalanma" (statik kar/TV karıncası) görme nörolojik bir durumdur. Semptomlar:
- Görsel karıncalanma (statik)
- Fotofobi (ışık hassasiyeti)
- Palinopsia (görüntü kalıntıları)
- Gece körlüğü benzeri semptomlar

### Nörolojik Temel: Thalamocortical Dysrhythmia

VSS'nin nörolojik kökeni **Thalamocortical Dysrhythmia** (TCD) olarak bilinir. Bu teoriye göre:
- Beynin talamus ve korteks arasındaki iletişim frekansları bozulur
- Normalde alpha bandında (8-12 Hz) çalışan görsel korteks, theta bandına (4-8 Hz) kayar
- Bu frekans kayması → görsel "karıncalanma" (statik) üretir
- **Işık stresi** → TCD'yi alevlendirir → statik karıncalanma artar
- **Düşük stres + doğru ışık** → TCD baskılanır → semptomlar azalır

> **Klinik bağlam:** Jarvis'in AI katmanı (Gemini 3.6 Pro), kullanıcının akıllı saat HRV (Kalp Atış Varyabilitesi) verisinden stres seviyesini analiz eder. HRV düşüşü → otonom sinir sistemi stres altında → VSS krizi yaklaşabilir → AI **proaktif olarak** FL-41 aydınlatma modunu tetikler. "Krizi beklemek yerine, krizi önler."

### Pattern Glare (Desen Parlaması)

Pattern Glare, tekrarlayan desenlerin (çizgiler, kafesler, yüksek kontrastlı geometrik şekiller) görsel sistemde aşırı uyarım yaratmasıdır. VSS hastalarında:
- Yüksek kontrastlı desenler → görsel karıncalanma artışı
- Düz beyaz yüzeyler (tavan, duvar) → "boş alan karıncalanması" (empty field static)
- **Çözüm:** Düz yüzeyleri maskelemek için düşük kontrastlı, yavaş hareket eden görseller (nebula projeksiyonu) kullanılır

> **Pattern Glare kırma:** Modül 3'teki (Space Projection) tavan projeksiyonu, düz beyaz tavanı "çok yavaş dönen, koyu mor/kırmızı düşük kontrastlı nebula" ile maskeleyerek Pattern Glare etkisini kırar. "Düz yüzey = karıncalanma; hareketli düşük kontrast = sakin."

### FL-41 Rose Tint (Gül Rengi) Spektrumu

FL-41, nöroloji ve oftalmoloji literatüründe VSS ve fotofobi için en etkili ışık filtresidir:

| Özellik | Detay |
|---|---|
| **Filtre aralığı** | 480-520 nm (mavi-yeşil bandı) kesim |
| **Renk** | Gül rengi / pembe-msı kehribar |
| **HEX** | #E6A8D7 → #FFB6C1 (FL-41 Rose Tint) |
| **Etki** | Mavi-yeşil ışığı filtreler → fotofobi azalır → VSS statik baskılanır |
| **Klinik kanıt** | FL-41 gözlükler VSS hastalarında semptomları %30-50 azaltır (klinik çalışmalar) |
| **WLED uygulaması** | RGB: [230, 168, 215] → FL-41 spektrumu taklit edilir |

> **FL-41 vs standart kehribar:** Standart kehribar (#BF8000) sıcak ama mavi-yeşil bandı tam kesmez. FL-41 Rose Tint (#E6A8D7) spesifik olarak 480-520 nm bandını filtreler → VSS için klinik olarak daha etkilidir.

### Işık Tetikleyicileri (Güncellenmiş)

| Tetikleyici | Etki | Çözüm |
|---|---|---|
| **Düşük PWM frekansı (<1kHz)** | LED titreşimi → VSS statik artışı | WLED PWM ≥ 2kHz (donanımsal) — **KRİTİK** |
| **Sert mavi ışık (450nm)** | Fotofobi → göz ağrısı → VSS alevlenme | FL-41 Rose Tint filtre (480-520nm kesim) |
| **Anlık parlaklık değişimi** | Flaş/strobe → palinopsia tetikleme | Transition ≥ 3000ms (ZORUNLU) |
| **Yüksek kontrast** | Pattern Glare → statik artışı | Düşük kontrast, FL-41 Rose Tint |
| **Beyaz arka plan (#FFFFFF)** | Maksimum fotofobi + Pattern Glare | Koyu lacivert (#0A0A0F) + FL-41 Rose Tint yazı |
| **Düz beyaz yüzeyler (tavan)** | Empty field static → karıncalanma | Nebula projeksiyonu ile maskeleme (Modül 3) |
| **Tekrarlayan desenler** | Pattern Glare → görsel stres | Düzgün, organik, düşük kontrastlı görseller |

### WLED VSS Optimizasyonu

```
  ❌ STANDART WLED (VSS tetikleyici)        ✅ VSS OPTIMIZE WLED
  ┌──────────────────────────────┐          ┌──────────────────────────────┐
  │  PWM: 500Hz (titreşim var)    │          │  PWM: 2kHz+ (titreşim yok)    │
  │  Renk: Tüm spektrum (mavi)    │          │  Renk: Kehribar/yeşil only   │
  │  Transition: 0-500ms (ani)   │          │  Transition: 3000ms (yavaş) │
  │  Efekt: Strobe/Flash          │          │  Efekt: Solid/Breathe only    │
  │  Parlaklık: 0-255 (ani)       │          │  Parlaklık: 0-150 (kademeli) │
  └──────────────────────────────┘          └──────────────────────────────┘
```

### VSS İçin WLED Ayarları

| Parametre | Standart | VSS Optimized |
|---|---|---|
| **PWM Frekans** | 500Hz (varsayılan) | 2kHz+ (donanımsal) |
| **Renk paleti** | Tüm RGB | Kehribar (#BF8000) + Yeşil (#2E8B57) |
| **Mavi ışık** | Açık | KAPALI (≤450nm kesim filtresi) |
| **Transition** | 0-500ms | 3000ms (minimum) |
| **Efektler** | Strobe, Flash, Rainbow | Solid, Breathe (yavaş nefes) |
| **Maks parlaklık** | 255 | 150 (%58) |
| **Kontrast** | Yüksek | Düşük (koyu arka plan) |

> **VSS Kuralı:** Odada ASLA ani ışık değişimi olmaz. Tüm geçişler ≥3 saniye. Mavi ışık yasak. Sadece kehribar/yeşil spektrum. "Calm Technology" prensibi medikal seviyeye yükseltilmiştir.

---

## 🩺 Bluetooth Tansiyon Aleti → Home Assistant

### Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Bluetooth Tansiyon | Omron HEM-7156T (BLE) | 1 | ~$60 | BLE → HA entegrasyonu |
| 2 | (Alternatif) | Withings BPM Connect (WiFi) | 1 | ~$100 | WiFi → HA webhook |
| 3 | (Yazılım) | HA BLE tansiyon entegrasyonu | — | $0 | HACS custom component |

### Omron BLE → HA Entegrasyonu

```
1. Omron HEM-7156T'yi telefona bağla (Omron Connect app)
2. HA HACS → "Omron BLE" custom component kur
3. Omron Connect → ölçüm yap → BLE → HA
4. HA sensörler:
   - sensor.blood_pressure_systolic → Sistolik (mmHg)
   - sensor.blood_pressure_diastolic → Diastolik (mmHg)
   - sensor.blood_pressure_pulse → Nabız (BPM)
   - sensor.blood_pressure_timestamp → Ölçüm zamanı
5. Veriler LOKAL saklanır (HA SQLite → .gitignore)
6. Tansiyon > 130/85 → "Yüksek Tansiyon Protokolü" otomasyon tetiklenir
```

### Veri Akışı

```
  Omron BLE Tansiyon Aleti
       │ Bluetooth
       ▼
  HA (VPS) → sensor.blood_pressure_systolic/diastolic
       │
       ├── Normal (<120/80) → sessiz (kayıt only)
       ├── Yüksek (>130/85) → "Yüksek Tansiyon Protokolü"
       │   ├── Barista mode KAPAT (kahve = tansiyon ↑)
       │   ├── Difüzör → Ylang-Ylang (tansiyon düşürücü)
       │   ├── Klima → 20°C (serin = tansiyon ↓)
       │   └── Jarvis → "Tansiyonunuz yüksek, kahveyi kestim"
       └── Kritik (>160/100) → mobil critical bildirim + "Doktor kontrolü"
```

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | BLE Tansiyon | Omron HEM-7156T | 1 | ~$60 | Bluetooth → HA |
| 2 | (Opsiyonel) | USB kamera (postür analizi) | 1 | ~$25 | Çalışma masası → MediaPipe Pose |
| 3 | (Yazılım) | MediaPipe Pose Estimation | — | $0 | pip install mediapipe opencv-python |

> **Toplam ekstra maliyet: ~$60-85** (tansiyon aleti + opsiyonel kamera)

---

## ✅ Kurulum Kontrol Listesi

- [ ] Omron BLE tansiyon aleti HA'a entegre edildi
- [ ] sensor.blood_pressure_systolic/diastolic HA'ta görünüyor
- [ ] WLED PWM frekansı 2kHz+ (donanımsal ayar)
- [ ] WLED renk paleti kehribar/yeşil only (mavi KAPALI)
- [ ] WLED transition minimum 3000ms
- [ ] WLED efektler Solid/Breathe only (Strobe/Flash YASAK)
- [ ] MagicMirror custom.css VSS optimize (koyu gri, kehribar yazı)
- [ ] `anti_vss_lighting_protocol.yaml` HA'a yüklendi
- [ ] `posture_and_spinal_guard.py` Pi 4'te çalışıyor (MediaPipe Pose)
- [ ] `hypertension_and_recovery_orchestrator.yaml` HA'a yüklendi
- [ ] Test: Tansiyon >130/85 → barista KAPAT + difüzör Ylang-Ylang + Jarvis uyarı
- [ ] Test: Boyun 15° öne → "Postürünüzü düzeltin" sesli uyarı
- [ ] Test: WLED transition 3sn → ani ışık değişimi YOK