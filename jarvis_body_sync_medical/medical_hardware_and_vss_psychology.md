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

### Işık Tetikleyicileri

| Tetikleyici | Etki | Çözüm |
|---|---|---|
| **Düşük PWM frekansı (<1kHz)** | LED titreşimi → VSS statik artışı | WLED PWM ≥ 2kHz (donanımsal) |
| **Sert mavi ışık (450nm)** | Fotofobi → göz ağrısı → VSS alevlenme | Kehribar/yeşil filtre (≤500nm kes) |
| **Anlık parlaklık değişimi** | Flaş/strobe → palinopsia tetikleme | Transition ≥ 3 saniye (3000ms) |
| **Yüksek kontrast** | Görsel stres → statik artışı | Düşük kontrast, koyu gri/kehribar |
| **Beyaz arka plan (#FFFFFF)** | Maksimum fotofobi | Koyu gri (#1A1A2E) + kehribar yazı |

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