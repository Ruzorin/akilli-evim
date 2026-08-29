# 🛡️ Modül 32: Yurt İklim ve Solunum Kalkanı — Donanım ve Kurulum

> **"Kıbrıs'ın rutubeti ve klimanın boğaz kurutmasına karşı yerel Zero-Trust iklim ağı."**

Kıbrıs yurt odalarında iki temel sorun vardır:
1. **Yüksek nem (%65-80):** Rutubet, küf, nefes darlığı, uyku kalitesi düşüşü
2. **Klima boğaz kurutması:** Split klima gece çalışınca havayı kurutur → boğaz tahrişi → sabah kuru öksürük

Bu modül, her iki sorunu da otonom olarak çözen yerel bir iklim kalkanıdır.

---

## 📦 Donanım Listesi

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Nem Alma Cihazı | Hisense D16CW (1.6L/gün) | 1 | ~$120 | Kompresörlü, Auto-Restart özellikli, Shelly prizle kontrol |
| 2 | Akıllı Priz | Shelly Plug S | 1 | ~$15 | Hisense'i otonom tetikler + güç tüketim izleme |
| 3 | Sensör | BME280 (Sıcaklık + Nem + Basınç) | 1 | ~$5 | I2C, ESP32'ye bağlı, oda nemi ölçer |
| 4 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | BME280 okur, MQTT yayınlar |
| 5 | Hava Temizleyici (DIY) | HEPA Filtre (H13) + 12V PC Fanı | 1 set | ~$25 | DIY kutu içinde, toz/küf/polen filtreler |
| 6 | Güç Kaynağı | 12V 2A Adaptör | 1 | ~$6 | PC fanını besler |
| 7 | 3D Baskı / Kutu | PLA Filament 200g veya MDF kutu | 1 | ~$4 | HEPA + fan montajı |
| 8 | Jumper Kablo | Dupont Dişi-Dişi | 4 | ~$1 | BME280 → ESP32 I2C |

**Modül 32 Toplam:** ~**$181**

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                  YURT ODA İKLİM KALKANI                      │
│                                                              │
│  ┌──────────────┐    I2C    ┌──────────────┐                │
│  │   BME280     │◄─────────►│   ESP32      │                │
│  │  (Nem/Isı)   │   SDA/SCL │  (ESPHome)   │                │
│  └──────────────┘           └──────┬───────┘                │
│                                    │ MQTT                    │
│                                    ▼                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Home Assistant (VPS — Tailscale)           │   │
│  │                                                      │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  GÜNDÜZ OTOMASYONU                              │  │   │
│  │  │  Nem > %55 → Klima KAPAT (Broadlink)            │  │   │
│  │  │           → Shelly ON → Hisense çalışır         │  │   │
│  │  │  Nem < %45 → Shelly OFF → Hisense durur         │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  GECE OTOMASYONU (Uyku)                         │  │   │
│  │  │  Hisense KAPAT (sessiz uyku)                    │  │   │
│  │  │  Klima → 26°C (Broadlink)                       │  │   │
│  │  │  Swing → TARA (hava akımı tavana)               │  │   │
│  │  │  → Boğaz kurutması önlenir                      │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐           ┌──────────────────────┐       │
│  │  Hisense     │◄──────────│  Shelly Plug S       │       │
│  │  D16CW       │  220V     │  (Akıllı Priz)       │       │
│  │  (Nem Alıcı) │           └──────────────────────┘       │
│  └──────────────┘                                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DIY Hava Temizleyici                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │ 12V Fan  │→ │ HEPA H13 │→ │ Temiz Hava Çıkış │   │   │
│  │  │ (PC Fan) │  │  Filtre  │  │                  │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💧 Hisense D16CW Nem Alma Cihazı

### Özellikler

| Özellik | Değer |
|---|---|
| Nem alma kapasitesi | 1.6L / gün (16°C, %60RH) |
| Tip | Kompresörlü (termoelektrik değil) |
| Tank kapasitesi | ~2L (dolu sensörü var) |
| Güç | ~230W (kompressör aktif) |
| Ses | ~38dB (gece modu) |
| Auto-Restart | **EVET** — güç kesintisinde otomatik devam |
| Boyut | ~34×21×40 cm (yurt odası için ideal) |

### Neden 1.6L (D16CW) ve 4.2L Değil?

| | Hisense D16CW (1.6L) | Hisense D42CW (4.2L) |
|---|---|---|
| **Fiyat** | ~$120 | ~$250 |
| **Boyut** | 34×21×40 cm | 36×25×64 cm |
| **Ses** | ~38dB | ~48dB |
| **Güç** | ~230W | ~550W |
| **Yurt odası (15-20m²)** | Yeterli (1.6L/gün) | Overkill |
| **Tank dolma sıklığı** | ~1.5 günde bir | ~3 günde bir |

> **Mühendislik kararı:** Yurt odası 15-20m². Günde 1.6L nem alma bu alan için yeterli. 4.2L model 2× pahalı, 2× büyük, 2× gürültülü, 2× güç tüketiyor. Boşa enerji harcamak değil, doğru kapasiteyi seçmek.

### Shelly Plug S ile Kontrol

```
Hisense D16CW → Shelly Plug S prizine takılır
Shelly → WiFi → HA → otonom tetiklenir

Hisense Auto-Restart özelliği:
  1. Hisense'i manuel aç, "Continuous" (sürekli) mod ayarla
  2. Shelly prizi KAPAT → Hisense güç kesilir → durur
  3. Shelly prizi AÇ → Hisense güç alır → Auto-Restart → otomatik çalışır
  4. Hiçbir fiziksel butona basmaya gerek yok

Shelly güç izleme:
  Hisense kompressör aktif: ~230W
  Hisense bekleme (tank dolu/fan): ~5W
  → HA'da "Hisense kompressör çalışıyor" sensörü türetilebilir
```

---

## 🌡️ BME280 + ESP32 Nem Sensörü

### ESPHome Kablolama

```
BME280 → ESP32
  VCC  → 3.3V (Pin 1)
  GND  → GND  (Pin 2)
  SDA  → GPIO 21 (I2C SDA)
  SCL  → GPIO 22 (I2C SCL)
```

### Montaj Pozisyonu

```
BME280 sensörü odanın ORTASINDA, ~1.5m yükseklikte:
  - Duvara yakın DEĞİL (duvar nemi yanıltıcı)
  - Klima üfleme yönünde DEĞİL (klima nemi yanıltıcı)
  - Hisense'e yakın DEĞİL (nem alıcı çevresi kuru)
  - Yatak seviyesinde (~1.5m) — uyku kalitesi için doğru ölçüm

Önerilen: Kitaplık orta raf, kablo sleeve ile gizli
```

---

## 🌬️ DIY Hava Temizleyici (HEPA + Fan)

### Neden Xiaomi Mi Air Purifier Değil, DIY?

| | DIY (HEPA + 12V Fan) | Xiaomi Mi Air Purifier 4 Lite |
|---|---|---|
| **Fiyat** | ~$25 | ~$130 |
| **Filtre değişim** | ~$8 (HEPA H13) | ~$30 (Xiaomi orijinal) |
| **Akıllı kontrol** | Shelly/ESP32 (HA) | Mi Home (Çin bulutu) |
| **Boyut** | ~15×15×20 cm | 24×24×52 cm |
| **Ses** | ~30dB (12V fan düşük hız) | ~35dB |
| **Yurt odası (15-20m²)** | Yeterli (CADR ~80) | Overkill (CADR 360) |
| **Gizlenebilirlik** | Evet (kutuya gizli) | Hayır (büyük, beyaz kule) |

> **Mühendislik kararı:** Yurt odası 15-20m². CADR 80 m³/h bu alan için yeterli. Xiaomi'nin CADR 360'ı overkill. Ayrıca Xiaomi Çin bulutuna bağlı — Zero-Trust ihlali. DIY HEPA+Fan hem 5× ucuz, hem HA'ya yerel entegre, hem de kutu içinde gizlenebilir.

### DIY Hava Temizleyici Montajı

```
Malzemeler:
  - HEPA H13 filtre (Ø15cm × 5cm) — ~$12
  - 12V PC fanı (120mm) — ~$8
  - 12V 2A adaptör — ~$6
  - MDF kutu veya 3D baskı kasa — ~$4

Montaj:
  ┌─────────────────────┐
  │   Temiz Hava Çıkış  │  ← Fan üfler
  │  ┌───────────────┐  │
  │  │   12V Fan     │  │
  │  │  (120mm PC)   │  │
  │  └───────┬───────┘  │
  │          │          │
  │  ┌───────┴───────┐  │
  │  │  HEPA H13     │  │  ← Filtre
  │  │  Filtre       │  │
  │  └───────┬───────┘  │
  │          │          │
  │   Kirli Hava Giriş │  ← Fan emer
  └─────────────────────┘

  Fan: Kirli havayı emer → HEPA'dan geçirir → temiz havayı üfler
  Akış: Aşağıdan yukarıya (ısı yükselir, doğal konveksiyon)

Kontrol:
  - 12V fan → Shelly Plug S (veya ESP32 PWM)
  - HA otomasyon: Toz sensörü (opsiyonel PMS5003) veya zamanlayıcı
  - Gece modu: Fan hızını %40'a düşür (sessiz)
  - Gündüz modu: Fan %80 (etkili filtreleme)
```

### Opsiyonel: PMS5003 Toz Sensörü

```
PMS5003 → ESP32 (UART)
  - PM1.0, PM2.5, PM10 ölçer
  - HA'da toz seviyesi sensörü
  - Toz > 35 μg/m³ → DIY hava temizleyici AÇ
  - Toz < 15 μg/m³ → DIY hava temizleyici KAPAT
  - Maliyet: ~$12 (opsiyonel)
```

---

## 🔒 Zero-Trust Güvenlik

| Kural | Açıklama |
|---|---|
| **Hisense yerel** | Hiçbir bulut bağlantısı yok — sadece Shelly prizle aç/kapa |
| **BME280 yerel** | ESP32 → MQTT → HA, veri buluta çıkmaz |
| **DIY hava temizleyici yerel** | Shelly/ESP32 ile kontrol, Çin bulutu yok |
| **Broadlink yerel** | Klima kontrolü Broadlink RM4 Mini (Modül 8) ile, yerel IR |
| **Veri gizliliği** | Nem/sıcaklık verisi sadece HA'da, buluta gönderilmez |

---

*Bu dosya, Kıbrıs yurt odası için iklim ve solunum kalkanının donanım kurulumunu detaylandır. Hisense D16CW + Shelly + BME280 + DIY HEPA kombinasyonu, $181 ile hem nem hem boğaz kurutması sorununu çözer.*
