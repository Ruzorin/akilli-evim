# call_routing_and_ceo_mode — Bluetooth Proxy ve Ses Köprüsü

> **Modül 19: Gelişmiş Çağrı Yönlendirme ve CEO Modu**
> Telefon çaldığında odanın atmosferini bir yönetim merkezine çevirmek; akıllı hoparlörler ve Bluetooth Proxy mikrofonu (ESP32-S3) üzerinden eller serbest (hands-free) görüşmeler yapmak.

---

## 📞 ESP32-S3 Bluetooth Proxy + HFP (Hands-Free Profile)

### Mimari

```
  Telefon (çağrı)                        Oda (Yönetim Merkezi)
  ┌──────────────┐                      ┌──────────────────┐
  │  Gelen arama  │                      │  Hoparlör (Echo)  │
  │  (ringing)    │                      │  Karşı taraf sesi │
  └──────┬───────┘                      └────────▲─────────┘
         │                                     │ I2S DAC
         │ Bluetooth HFP                       │
         ▼                                     │
  ┌──────────────┐    ┌──────────────┐  ┌─────┴───────┐
  │  ESP32-S3    │    │  HFP Ses      │  │  INMP441    │
  │  (BT Proxy)  │───►│  Gateway      │─►│  Mikrofon   │
  │              │    │  (A2DP+HFP)   │  │  Senin sesin│
  └──────────────┘    └──────────────┘  └─────────────┘
```

### HFP (Hands-Free Profile) Nedir?

| Profil | Kullanım | Ses Kalitesi |
|---|---|---|
| **A2DP** | Müzik streaming (stereo, yüksek kalite) | Yüksek |
| **HFP** | Telefon çağrısı (mono, iki yönlü) | Orta (8kHz) |
| **HFP Wideband** | Telefon çağrısı (geniş bant, 16kHz) | İyi |

> ESP32-S3, hem A2DP (müzik) hem HFP (çağrı) destekler. Çağrı geldiğinde A2DP'den HFP'ye otomatik geçer.

### ESPHome Bluetooth Proxy + HFP Yapılandırması

```yaml
# ESP32-S3 ESPHome konfigürasyonu (Modül 1 ses hub'ına ek)

# Bluetooth Proxy — telefon BT bağlantısını alır
bluetooth_proxy:
  active: true
  # HFP (Hands-Free Profile) desteği
  services:
    - service_uuid: "111E"  # HFP UUID

# I2S Mikrofon (INMP441) — senin sesin → çağrıya
i2s_audio:
  - id: mic_i2s
    i2s_lrclk: GPIO 5    # WS
    i2s_bclk: GPIO 6     # SCK
    i2s_data: GPIO 4     # SD (mikrofon → ESP32)

# I2S DAC (hoparlör) — karşı taraf sesi → oda
i2s_audio:
  - id: spk_i2s
    i2s_lrclk: GPIO 41   # WS (ESP32-S3)
    i2s_bclk: GPIO 42    # SCK
    i2s_data: GPIO 40    # SD (ESP32 → hoparlör)

# Bluetooth HFP ses köprüsü
# Telefon → BT → ESP32-S3 → I2S DAC → hoparlör
# Mikrofon → I2S → ESP32-S3 → BT → telefon → çağrı
```

### Gecikmesiz ve Cızırtısız Ses Akışı

| Sorun | Çözüm |
|---|---|
| **Gecikme** | I2S DMA buffer küçük tut (256 samples = ~16ms). BT HFP buffer minimize |
| **Cızırtı** | I2S clock jitter → 100nF kondansatör VDD'ye. GND ortak. Kısa kablo |
| **Yankı** | AEC (Acoustic Echo Cancellation) — ESP32-S3'de yazılımsal AEC. Hoparlör sesi mikrofona geri gelmesin |
| **Kesilme** | BT sinyal gücü yüksek tut. ESP32-S3 anteni serbest bırakma. WiFi + BT aynı anten → öncelik BT'ye |

> **Gecikme hedefi:** <50ms (telefon → oda). İnsan kulağı 50ms altını "anında" algılar. 100ms+ → "gecikmeli" hissi → konuşma zorlaşır.

---

## 🎯 "CEO Modu" — Yönetim Merkezi Atmosferi

### Çağrı Sırasında Oda

```
  Normal mod → CEO modu (çağrı geldiğinde):

  ┌─────────────────────────────────────────────┐
  │                  ODA (CEO MODU)               │
  │                                             │
  │  WLED: Sakin beyaz/mavi "nefes" (profesyonel) │
  │  Müzik: Duraklatıldı (Auto-Ducking)           │
  │  Klima: Fan quiet (ses yapmasın)              │
  │  Difüzör: Kapat (koku dikkat dağıtmasın)     │
  │  Projeksiyon: Kapat (görsel dikkat dağıtma)   │
  │                                             │
  │  📞 Çağrı → BT Proxy → Hoparlör (karşı taraf) │
  │  🎤 INMP441 → BT Proxy → Telefon (senin sesin)│
  │                                             │
  │  "Oda bir yönetim merkezine dönüştü"          │
  └─────────────────────────────────────────────┘
```

### UX (Kullanıcı Deneyimi) — CEO Hissi

| Faktör | CEO Deneyimi |
|---|---|
| **Işık** | Sakin beyaz/mavi → "profesyonel, odaklı" hissi |
| **Ses** | Müzik durur → "çağrı önemli" mesajı |
| **Koku** | Difüzör kapanır → "iş modu" (koku = dinlenme, iş değil) |
| **Klima** | Fan quiet → "sessiz oda" (çağrıda hava sesi olmaz) |
| **Mikrofon** | INMP441 → "odanın her yerinden konuş" (bağırmadan) |
| **Hoparlör** | Spatial Audio → "karşı taraf odada" (stereo değil, oda dolusu) |

> **"CEO deneyimi":** Kullanıcı odaya girer, telefon çalar, oda otomatik "yönetim merkezine" dönüşür. Işıklar sakinleşir, müzik durur, koku kapanır. Kullanıcı odanın ortasında durur ve normal ses tonuyla konuşur — oda onu duyar, karşı tarafı odaya verir. "Telefon kulakta" değil, "oda bir konferans salonu" hissi.

---

## 📋 Gerekli Ek Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Donanım) | ESP32-S3 (Modül 1 ile paylaşımlı) | — | $0 | BT Proxy + HFP + I2S |
| 2 | (Donanım) | INMP441 (Modül 1 ile paylaşımlı) | — | $0 | Mikrofon |
| 3 | (Donanım) | I2S DAC (MAX98357A) | 1 | ~$3 | Hoparlör sürücü (çağrı sesi) |
| 4 | (Yazılım) | HA Companion App | — | $0 | phone_call_state sensörü |

> **Toplam ekstra maliyet: ~$3** (I2S DAC — diğer her şey Modül 1 ile paylaşımlı)

---

## ✅ Kurulum Kontrol Listesi

- [ ] ESP32-S3'e Bluetooth Proxy + HFP eklendi (ESPHome)
- [ ] INMP441 mikrofon I2S üzerinden çalışıyor
- [ ] I2S DAC (MAX98357A) hoparlöre bağlandı
- [ ] BT HFP ses köprüsü test edildi (telefon → oda, oda → telefon)
- [ ] Gecikme <50ms (test: telefonla odayı ara, gecikme ölç)
- [ ] Cızırtı yok (100nF kondansatör, ortak GND, kısa kablo)
- [ ] AEC aktif (yankı yok — hoparlör sesi mikrofona geri gelmez)
- [ ] HA Companion App → phone_call_state sensörü çalışıyor
- [ ] `ceo_call_routing_automation.yaml` HA'a yüklendi
- [ ] `hands_free_interraction_script.yaml` HA'a yüklendi
- [ ] Test: Çağrı gel → müzik dur + WLED beyaz/mavi + klima quiet
- [ ] Test: VIP arıyor → Jarvis "Önemli arama, [Ad] arıyor"
- [ ] Test: Çağrı cevapla → BT Proxy → ses odaya → normal sesle konuş
- [ ] Test: Çağrı bit → müzik fade-in devam + ışıklar normale