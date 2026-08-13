# embodied_jarvis_avatar — Donanım, Kinematik ve BOM Rehberi

> **Modül 29: Embodied Jarvis Avatar**
> Jarvis'in masadaki "fiziksel yüzü" — 5 eksenli robotik masa lambası
> Autonomous OS (açık kaynaklı fiziksel AI ajan işletim sistemi) tabanlı

---

## 🎯 Konsept: "Fiziksel Jarvis"

```
  ┌─────────────────────────────────────────────────────┐
  │              CLOUD VPS (Beyin)                       │
  │  Home Assistant + DeepSeek V4-Pro + MiniMax Speech  │
  │  OpenClaw Agentic Runtime                            │
  └──────────────────┬──────────────────────────────────┘
                     │ Tailscale VPN + MQTT
  ┌──────────────────▼──────────────────────────────────┐
  │           RASPBERRY PI 4 (Gövde)                     │
  │  Autonomous OS — sadece sensör/motor HAL             │
  │  Kamera + Mikrofon + Servolar + LED Halkası          │
  └──────────────────┬──────────────────────────────────┘
                     │ PCA9685 (I2C) + GPIO
  ┌──────────────────▼──────────────────────────────────┐
  │           FİZİKSEL GÖVDE (5-DOF)                     │
  │  Base → Shoulder → Elbow → Wrist → Head              │
  │  MG996R × 3 + SG90 × 2 + WS2812 LED Halkası         │
  └─────────────────────────────────────────────────────┘
```

**Mantık:** Beyin Cloud VPS'te (pahalı GPU, sınırsız token). Pi sadece
"sensör/motor gövdesi" olarak çalışır — görüntü alır, MQTT ile VPS'e
gönderir, VPS'ten gelen servo komutlarını uygular.

---

## 📐 3D Baskı Tasarımı — Açık Kaynak 5-DOF Robot Kol

### Önerilen Tasarım: BCN3D Moveo (5-DOF)

| Özellik | Detay |
|---------|-------|
| **Tasarım** | BCN3D Moveo — açık kaynak 5-DOF robot kol |
| **Kaynak** | https://github.com/BCN3D/Moveo |
| **Lisans** | CC BY-NC-SA 4.0 |
| **DOF** | 5 (Base + Shoulder + Elbow + Wrist Pitch + Wrist Roll) |
| **Dosyalar** | STL + STEP + SolidWorks montaj dosyaları |
| **Baskı Süresi** | ~15-20 saat (tüm parçalar) |
| **Filament** | PLA/PETG, ~150-200g |

### Alternatif: EEZYbotARM MK2 (4+1 DOF)

| Özellik | Detay |
|---------|-------|
| **Tasarım** | EEZYbotARM MK2 — daha basit masaüstü robot kol |
| **Kaynak** | https://www.thingiverse.com/thing:1451810 |
| **DOF** | 4+1 (4 eksen + gripper) |
| **Avantaj** | Daha az parça, daha hızlı baskı (~8 saat) |
| **Dezavantaj** | Daha kısa erişim (~20-30cm) |

### Lamba Adaptasyonu — "Kafa" Modülü

Robot kolun uç efektörü (gripper) yerine "kafa" modülü tasarlanmalı:

```
  ┌─────────────────────────────┐
  │         Kafa Modülü          │
  │  ┌───────────────────────┐  │
  │  │   WS2812 LED Halkası   │  │  ← 12 LED, 144mm çap
  │  │  ┌─────────────────┐  │  │
  │  │  │  Kamera Modülü   │  │  │  ← Raspberry Pi Camera V2
  │  │  │  (5MP, 1080p)    │  │  │
  │  │  └─────────────────┘  │  │
  │  │  ┌─────────────────┐  │  │
  │  │  │  INMP441 Mik.    │  │  │  ← I2S dijital mikrofon
  │  │  └─────────────────┘  │  │
  │  └───────────────────────┘  │
  └─────────────────────────────┘
```

**Kafa STL dosyası:** `head_module_v1.stl` (özel tasarım — Fusion 360 ile
robot kolun uç flanşına uyacak şekilde tasarlanmalı)

---

## 📋 BOM (Bill of Materials) — Eksiksiz Malzeme Listesi

### 1. Ana İşlemci ve Aksesuarlar

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 1 | Raspberry Pi 4 Model B 4GB | 1 | ~1.500 | Ana işlemci — Autonomous OS host |
| 2 | Raspberry Pi Camera V2 (5MP) | 1 | ~600 | Postür analizi + yüz tanıma |
| 3 | MicroSD 64GB A2 | 1 | ~250 | OS + Autonomous OS |
| 4 | 5V/3A USB-C Güç Adaptörü | 1 | ~150 | Pi güç kaynağı |
| 5 | Aktif Soğutma Fanı + Heatsink | 1 | ~80 | Pi termal yönetimi |

**Ara Toplam: ~2.580₺**

### 2. Servo Motorlar ve Sürücü

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 6 | MG996R Servo Motor (Metal Dişli, 11kg-cm) | 3 | ~150/adet | Base + Shoulder + Elbow (yüksek tork) |
| 7 | SG90 Micro Servo (1.8kg-cm) | 2 | ~25/adet | Wrist Pitch + Wrist Roll (hafif) |
| 8 | PCA9685 16-Kanal PWM Sürücü (I2C) | 1 | ~80 | Tüm servoları tek I2C hattından sürer |
| 9 | 6V/5A Harici Güç Kaynağı | 1 | ~200 | Servolar için (Pi'den AYRI!) |
| 10 | 1000µF/16V Elektrolitik Kondansatör | 1 | ~10 | Servo güç dalgalanmasını filtrele |

**Ara Toplam: ~810₺**

### ⚠️ KRİTİK: Servo Güç Kaynağı
MG996R servo stall akımı ~2.5A. 3 servo = ~7.5A peak.
Pi'nin 5V pin'i SADECE ~1.2A verebilir → SERVO'LARI Pİ'DEN BESLEME!
Ayrı 6V/5A güç kaynağı kullan, GND'leri ortakla.

### 3. Sensörler ve LED

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 11 | INMP441 I2S Dijital Mikrofon | 1 | ~80 | Sesli komut (MiniMax'a gönderilir) |
| 12 | WS2812B LED Halkası (12 LED, 144mm) | 1 | ~60 | Kafa modülü — ifade ışığı |
| 13 | MAX98357A I2S Amplifikatör | 1 | ~50 | Hoparlör sürücü (opsiyonel) |
| 14 | 4Ω 3W Mini Hoparlör | 1 | ~30 | Sesli yanıt (MiniMax'ten gelen) |

**Ara Toplam: ~220₺**

### 4. 3D Baskı Malzemeleri

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 15 | PLA Filament 1kg | 1 | ~300 | Gövde parçaları |
| 16 | PETG Filament 500g | 1 | ~250 | Yüksek stresli parçalar (base, shoulder) |
| 17 | M3 Vidalar ve Somun Seti | 1 | ~50 | Montaj |
| 18 | Rulman Seti (MR85ZZ × 4) | 1 | ~40 | Eklemlerde sürtünmeyi azalt |

**Ara Toplam: ~640₺**

### 5. Ağ ve Kablolama

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 19 | Tailscale VPN (ücretsiz) | - | 0 | Pi ↔ Cloud VPS güvenli tünel |
| 20 | Jumper Kablo Seti (Dupont) | 1 | ~50 | Servo + sensör bağlantıları |
| 21 | 22AWG Silikon Kablo | 1 | ~30 | Güç hatları |

**Ara Toplam: ~80₺**

---

### 💰 TOPLAM MALİYET

| Kategori | Tutar |
|----------|-------|
| İşlemci + Aksesuar | ~2.580₺ |
| Servo + Sürücü | ~810₺ |
| Sensör + LED | ~220₺ |
| 3D Baskı | ~640₺ |
| Ağ + Kablo | ~80₺ |
| **GENEL TOPLAM** | **~4.330₺ (~$130)** |

> **Karşılaştırma:** Autonomous Lamp hazır ürün = $999
> **DIY maliyet:** ~$130 → **%87 tasarruf**

---

## 🔧 Montaj ve Kablolama

### Pin Bağlantı Tablosu (Raspberry Pi 4)

| Bileşen | Pi Pin | İşlev | Not |
|---------|--------|-------|-----|
| PCA9685 SDA | GPIO2 (Pin 3) | I2C Data | Servo sürücü |
| PCA9685 SCL | GPIO3 (Pin 5) | I2C Clock | Servo sürücü |
| PCA9685 VCC | 3.3V (Pin 1) | Logic güç | Sadece logic |
| PCA9685 V+ | 6V PSU | Servo güç | HARİCİ güç! |
| PCA9685 GND | GND (Pin 6) | Ortak toprak | PSU GND ile ortak |
| INMP441 SD | GPIO20 (Pin 38) | I2S Data | Mikrofon |
| INMP441 WS | GPIO21 (Pin 40) | I2S Word Select | Mikrofon |
| INMP441 SCK | GPIO18 (Pin 12) | I2S Bit Clock | Mikrofon |
| INMP441 VDD | 3.3V | Güç | 3.3V! 5V VERME |
| Camera | CSI-2 Port | Kamera | Ribbon kablo |
| WS2812 DIN | GPIO10 (Pin 19) | SPI MOSI | LED halkası |
| WS2812 VCC | 5V (Pin 2) | Güç | 12 LED ~720mA |
| WS2812 GND | GND | Toprak | |
| MAX98357 DIN | GPIO22 (Pin 15) | I2S Data | Hoparlör |
| MAX98357 BCLK | GPIO18 | I2S BCLK | Mikrofonla ortak |
| MAX98357 LRC | GPIO21 | I2S LRC | Mikrofonla ortak |

### Servo Kanal Ataması (PCA9685)

| Kanal | Servo | Eksen | Açı Aralığı | Not |
|-------|-------|-------|-------------|-----|
| 0 | MG996R | Base (Y rotasyon) | 0-180° | Masa tabanı |
| 1 | MG996R | Shoulder (Omuz) | 30-150° | Kol yukarı/aşağı |
| 2 | MG996R | Elbow (Dirsek) | 0-135° | Kol büküm |
| 3 | SG90 | Wrist Pitch | 0-180° | Kafa yukarı/aşağı |
| 4 | SG90 | Wrist Roll | 0-180° | Kafa sağa/sola |

---

## 📐 Kinematik — 5-DOF İleri Kinematik

```
  Base (θ₁) → Shoulder (θ₂) → Elbow (θ₃) → Wrist Pitch (θ₄) → Wrist Roll (θ₅)

  Link uzunlukları (BCN3D Moveo adaptasyonu):
    L₁ (base height) = 120mm
    L₂ (shoulder-elbow) = 150mm
    L₃ (elbow-wrist) = 120mm
    L₄ (wrist-head) = 80mm

  İleri kinematik (TCP = Tool Center Point = kafa merkezi):
    x = cos(θ₁) × [L₂×cos(θ₂) + L₃×cos(θ₂+θ₃) + L₄×cos(θ₂+θ₃+θ₄)]
    y = sin(θ₁) × [L₂×cos(θ₂) + L₃×cos(θ₂+θ₃) + L₄×cos(θ₂+θ₃+θ₄)]
    z = L₁ + L₂×sin(θ₂) + L₃×sin(θ₂+θ₃) + L₄×sin(θ₂+θ₃+θ₄)
```

**Postür Kalkanı için:** Lambanın "kullanıcıya uzanması" hareketi
`motion.aim(x, y, z)` skill'i ile yapılır — Autonomous OS HAL `motion`
capability'si bu hesabı otomatik yapar (inverse kinematics).

---

## 🔗 İlgili Dosyalar

- [`autonomous_os_setup.md`](autonomous_os_setup.md) — Autonomous OS kurulum rehberi
- [`embodied_lamp_driver.py`](embodied_lamp_driver.py) — MG996R + PCA9685 servo sürücü
- [`posture_shield_automation.yaml`](posture_shield_automation.yaml) — Postür Kalkanı HA otomasyonu
- [`DEVICE.md`](DEVICE.md) — Autonomous OS cihaz tanımı
- [`SOUL.md`](SOUL.md) — Jarvis lamp karakteri
- [`SAFETY.md`](SAFETY.md) — Güvenlik sınırları