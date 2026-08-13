# desktop_pet_kame — Donanım, Montaj ve Lokal İzolasyon Rehberi

> **Modül 30: Desktop Pet Kame**
> Jarvis'in masadaki fiziksel evcil hayvanı — 8-DOF dört bacaklı robot
> Kamera/mikrofonu YOK — tüm zeka Jarvis'ten (Modül 13 + 10) MQTT ile gelir

---

## 🐾 Kame Nedir?

Kame, BQ Innovation Lab (Javier Isabel) tarafından geliştirilen açık kaynak
3D basılabilir dört bacaklı robottur. 8 serbestlik derecesi (DOF) ile
her bacakta 2 servo — paralelgram mekanizması ile ayak her zaman zemine
dik kalır.

| Özellik | Detay |
|---------|-------|
| **Tasarım** | Kame by BQ — Thingiverse #1265766 |
| **Kaynak** | https://www.thingiverse.com/thing:1265766 |
| **Lisans** | CC BY-SA 3.0 |
| **DOF** | 8 (4 bacak × 2 servo) |
| **Mekanizma** | Paralelgram — ayak zemine dik |
| **Rulman** | F693ZZ (PLA parçalara tam oturur) |
| **İşlemci** | ESP8266 NodeMCU v3 |
| **Güç** | 2S LiPo (7.4V) — HV servo doğrudan |

---

## 📐 Mimari: "Beyinsiz Gövde" — Lokal İzolasyon

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD VPS (Beyin)                         │
│  Home Assistant + DeepSeek V4-Pro + MiniMax Speech 2.8 Turbo │
│  Modül 13: Tapo C200 Kamera (OpenCV — Kame konum takibi)     │
│  Modül 10: WLED INMP441 (BPM/ritim analizi)                  │
└──────────────────┬──────────────────────────────────────────┘
                   │ Tailscale VPN + MQTT
                   │
    ┌──────────────▼──────────────┐
    │   GL-MT3000 (Yerel Ağ)       │
    │   MQTT Broker: 1883          │
    └──────────────┬──────────────┘
                   │ Local LAN (WiFi)
                   │
    ┌──────────────▼──────────────┐
    │   ESP8266 NodeMCU (Kame)     │
    │   ⚠️ ÇİN BULUTU YOK!         │
    │   Sadece yerel MQTT dinler   │
    │   8 × SG90/MG90S servo       │
    └─────────────────────────────┘
```

**Kritik:** ESP8266 NodeMCU varsayılan olarak Blynk/Tuya çin bulutuna
bağlanmaya çalışır. Biz bunu DISABLE edip SADECE yerel MQTT broker'a
(GL-MT3000) bağlanacak şekilde izole ederiz.

---

## 📋 BOM (Bill of Materials)

### 1. Elektronik

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 1 | ESP8266 NodeMCU v3 (CH340) | 1 | ~120 | Ana işlemci — WiFi + MQTT |
| 2 | SG90 Micro Servo (1.8kg-cm) | 8 | ~25/adet | 4 bacak × 2 servo (hafif Kame) |
|   | — VEYA — MG90S Metal Dişli (2.2kg-cm) | 8 | ~35/adet | Daha dayanıklı (önerilen) |
| 3 | 2S LiPo Batarya 1000mAh (7.4V) | 1 | ~150 | HV servo doğrudan besler |
| 4 | TP4056 Şarj Modülü (koruma dahil) | 1 | ~15 | LiPo şarj koruması |
| 5 | 1000µF/16V Elektrolitik Kondansatör | 1 | ~10 | Servo güç dalgalanması |
| 6 | Qi Receiver Coil (kablosuz şarj) | 1 | ~60 | Otonom şarj pad'i |
| 7 | Slide Switch (aç/kapa) | 1 | ~5 | Güç anahtarı |

**Ara Toplam (SG90): ~560₺ / (MG90S): ~640₺**

### 2. 3D Baskı

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 8 | PLA Filament 500g | 1 | ~180 | Kame gövde parçaları |
| 9 | F693ZZ Rulman × 8 | 1 set | ~80 | Eklemlerde sürtünmeyi azalt |
| 10 | M2/M3 Vida ve Somun Seti | 1 | ~40 | Montaj |

**Ara Toplam: ~300₺**

### 3. Şarj İstasyonu (Eye of Sauron)

| # | Malzeme | Adet | Fiyat (₺) | Not |
|---|---------|------|-----------|-----|
| 11 | Qi Kablosuz Şarj Verici Pad | 1 | ~80 | Masaya sabit — Kame üstüne park |
| 12 | 5V/2A USB Adaptör (Qi pad güç) | 1 | ~80 | Qi pad güç kaynağı |

**Ara Toplam: ~160₺**

---

### 💰 TOPLAM MALİYET

| Kategori | SG90 | MG90S |
|----------|------|-------|
| Elektronik | ~560₺ | ~640₺ |
| 3D Baskı | ~300₺ | ~300₺ |
| Şarj İstasyonu | ~160₺ | ~160₺ |
| **TOPLAM** | **~1.020₺ (~$30)** | **~1.100₺ (~$33)** |

---

## 🔧 ESP8266 Pin Bağlantıları

### Servo Kanal Ataması

| Servo | ESP8266 Pin | Bacak | Eksen | Açı Aralığı |
|-------|-------------|-------|-------|-------------|
| 1 | D1 (GPIO5) | Sol Ön | Hip (kalça) | 45-135° |
| 2 | D2 (GPIO4) | Sol Ön | Knee (diz) | 30-150° |
| 3 | D3 (GPIO0) | Sağ Ön | Hip | 45-135° |
| 4 | D4 (GPIO2) | Sağ Ön | Knee | 30-150° |
| 5 | D5 (GPIO14) | Sol Arka | Hip | 45-135° |
| 6 | D6 (GPIO12) | Sol Arka | Knee | 30-150° |
| 7 | D7 (GPIO13) | Sağ Arka | Hip | 45-135° |
| 8 | D8 (GPIO15) | Sağ Arka | Knee | 30-150° |

### Güç Bağlantısı

```
  2S LiPo (7.4V) ──┬── Switch ──┬── ESP8266 Vin (5V pin'e bağla)
                   │             │
                   │             ├── Servo VCC (tüm 8 servo)
                   │             │
                   │             └── 1000µF Kondansatör (paralel)
                   │
                   └── TP4056 ── Qi Receiver Coil (şarj için)

  GND ── Ortak (ESP8266 + Servo + LiPo + TP4056)
```

⚠️ **Servoları ESP8266'dan BESLEME!** 8 servo peak ~8A — ESP8266'nın
3.3V pin'i SADECE ~12mA verebilir. LiPo'dan doğrudan besle.

---

## 🔒 Lokal İzolasyon — Çin Bulutu Devre Dışı

ESP8266 NodeMCU varsayılan firmware'leri (Blynk, Tuya, WeMo) çin
bulut sunucularına bağlanır. Biz bunu tamamen devre dışı bırakır:

### İzolasyon Adımları

1. **Arduino IDE ile özel firmware yükle** (`kame_esp8266_firmware.ino`)
2. **WiFi:** Sadece GL-MT3000 ağına bağlan (SSID: GL-MT3000)
3. **MQTT:** Sadece yerel broker (gl-mt3000.local:1883)
4. **Cloud bağlantısı YOK** — hiçbir dış sunucuya istek göndermez
5. **mDNS:** `kame.local` olarak yerel ağda keşfedilir

### MQTT Topic'leri (Kame Dinler)

| Topic | Yön | Payload | İşlev |
|-------|-----|---------|-------|
| `kame/command/move` | Cloud → Kame | `{"dir": "forward", "steps": 3}` | Yürü |
| `kame/command/dance` | Cloud → Kame | `{"bpm": 120, "beat": 1}` | Dans et |
| `kame/command/pose` | Cloud → Kame | `{"pose": "bow"}` | Poz ver |
| `kame/command/sit` | Cloud → Kame | `{}` | Çömel |
| `kame/command/stand` | Cloud → Kame | `{}` | Kalk |
| `kame/status/battery` | Kame → Cloud | `{"level": 85}` | Batarya % |
| `kame/status/position` | Kame → Cloud | `{"x": 0.3, "y": 0.5}` | Masada konum |
| `kame/status/alive` | Kame → Cloud | `{"heartbeat": 1}` | Canlı sinyali |

---

## 📐 Kame Hareket Repertuarı

| Hareket | Açıklama | Kullanım |
|---------|----------|----------|
| **walk** | 4 bacaklı yürüyüş (diagonal gait) | Eye of Sauron park |
| **dance** | Müzik ritmine senkron çömelme + ayak vurma | Audio-Reactive |
| **bow** | Baş eğme (ön bacaklar uzat, gövde alçalt) | Wingman karşılama |
| **sit** | Çömelme (tüm bacaklar bükülü) | Bekleme/uyku |
| **stand** | Dik durma | Hazır |
| **wave** | Tek ön bacak kaldırma | Selamlama |
| **tilt** | Gövde yana eğme | "Meraklı" ifade |

---

## 🔗 İlgili Dosyalar

- [`kame_esp8266_firmware.ino`](kame_esp8266_firmware.ino) — ESP8266 Arduino kodu
- [`audio_reactive_dance.yaml`](audio_reactive_dance.yaml) — WLED BPM → Kame dans
- [`eye_of_sauron_parking.py`](eye_of_sauron_parking.py) — OpenCV otonom park
- [`wingman_greeting_protocol.yaml`](wingman_greeting_protocol.yaml) — Misafir karşılama
- [`config.yaml`](config.yaml) — Modül konfigürasyonu