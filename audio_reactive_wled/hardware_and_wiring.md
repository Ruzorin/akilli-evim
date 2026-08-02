# audio_reactive_wled — Donanım ve Kablolama Rehberi

> **Modül 10: Audio Reactive WLED**
> Odayı basit bir RGB "oyuncu odasından" çıkarıp, premium bir lounge alanına dönüştürmek. ESP32 ve INMP441 dijital mikrofon ile müziğin bas ritimlerine duyarlı, zarif ve nefes alan aydınlatma.

---

## 🧠 Neden ESP8266 Değil, ESP32?

Bu modülde **ESP8266 kullanılamaz**. Bunun teknik ve pratik nedenleri vardır:

### 1. FFT (Hızlı Fourier Dönüşüm) İşlem Gücü

Sese duyarlı aydınlatma, mikrofondan gelen ham ses sinyalini **frekans bantlarına** ayırmayı gerektirir. Bu işlem FFT (Fast Fourier Transform) algoritması ile yapılır.

| Özellik | ESP8266 (Tensilica L106) | ESP32 (Tensilica LX6 Dual-Core) |
|---|---|---|
| Çekirdek | 1 çekirdek @ 80MHz | 2 çekirdek @ 240MHz |
| RAM | ~50KB usable | 520KB SRAM |
| FPU (Kayan Nokta Birimi) | ❌ Yok (yazılım emülasyonu) | ✅ Var (donanımsal) |
| FFT Performansı | Çok yavaş, ses gecikmeli | Akıcı, gerçek zamanlı |

> **Kritik:** FFT, yoğun kayan nokta (float) hesabı gerektirir. ESP8266'da FPU olmadığı için her float işlemi yazılım ile emüle edilir → saniyede sadece birkaç FFT frame'i hesaplanabilir. Ses ve ışık arasındaki gecikme 200-500ms'ye çıkar → ışık müziğe ayak uyduramaz, "gecikmeli yanıp sönme" hissi yaratır. ESP32'de donanımsal FPU ile saniyede 60+ FFT frame'i hesaplanır → ışık müzikle **anında** senkronizedir.

### 2. I2S Dijital Mikrofon Desteği

INMP441, **I2S (Inter-IC Sound)** protokolü ile çalışan dijital bir mikrofondur. I2S, ses verisini dijital olarak (analog değil) iletir — bu da çok daha temiz, gürültüsüz ses sinyali demektir.

| Özellik | ESP8266 | ESP32 |
|---|---|---|
| I2S Donanım | ❌ Yok | ✅ Donanımsal I2S peripheral |
| Analog mikrofon (MAX9814 vb.) | ✅ ADC ile (ama gürültülü) | ✅ ADC ile (ama gürültülü) |
| Dijital mikrofon (INMP441) | ❌ Desteklenmiyor | ✅ Tam destek |

> ESP8266'da I2S donanımı olmadığı için INMP441 kullanılamaz. Analog mikrofon (MAX9814) kullanılabilir ama ADC gürültüsü nedeniyle bas frekansları temiz algılanamaz. ESP32 + INMP441 kombinasyonu, **stüdyo kalitesinde** ses algılama sağlar.

### 3. Sound Reactive WLED Firmware

[Sound Reactive WLED](https://github.com/atuline/WLED) projesi, ESP32 için optimize edilmiştir. ESP8266 desteği ya hiç yok ya da sınırlıdır. Tüm gelişmiş ses efektleri (Gravimeter, Freqwave, DJ Light) ESP32'de çalışır.

---

## 🎤 INMP441 Dijital Mikrofon → ESP32 Pin Şeması

INMP441, 24-bit I2S dijital mikrofondur. ESP32'nin I2S peripheral'ına 4 kablo ile bağlanır.

### Pin Bağlantı Tablosu

| INMP441 Pin | ESP32 Pin | İşlev | Açıklama |
|---|---|---|---|
| **VDD** | **3.3V** | Güç | ⚠️ 3.3V! 5V VERME — mikrofon yanar |
| **GND** | **GND** | Toprak | Ortak referans |
| **SD (Serial Data)** | **GPIO 32** | I2S Data In | Mikrofon → ESP32 ses verisi |
| **WS (Word Select / LRCLK)** | **GPIO 15** | I2S Word Select | Kanal seçim sinyali (L/R) |
| **SCK (Serial Clock)** | **GPIO 14** | I2S Bit Clock | Veri saat sinyali |
| **L/R** | **GND** | Kanal Seçimi | GND = Sol kanal aktif |

### Bağlantı Diyagramı

```
  ESP32 DevKit V1              INMP441 Modülü
  ┌──────────────┐             ┌──────────────┐
  │              │             │              │
  │  3.3V        ├────────────►│  VDD         │  (Güç — 3.3V!)
  │              │             │              │
  │  GND         ├────────────►│  GND         │  (Toprak)
  │              │             │              │
  │  GPIO 32     ├◄────────────┤  SD          │  (I2S Data — mikrofon→ESP32)
  │              │             │              │
  │  GPIO 15     ├────────────►│  WS          │  (I2S Word Select)
  │              │             │              │
  │  GPIO 14     ├────────────►│  SCK         │  (I2S Bit Clock)
  │              │             │              │
  │  GND         ├────────────►│  L/R         │  (Sol kanal = GND)
  │              │             │              │
  └──────────────┘             └──────────────┘
```

### ⚠️ Önemli Uyarılar

- **L/R Pini:** INMP441'nin L/R pini GND'ye bağlanırsa **sol kanal**, 3.3V'a bağlanırsa **sağ kanal** aktif olur. Biz sol kanal kullanıyoruz (GND).
- **Kablo Uzunluğu:** I2S sinyalleri yüksek frekanslıdır. Kablo 15cm'den uzun olursa sinyal bozulur. Mikrofonu ESP32'ye mümkün olduğunca yakın tutun.
- **Güç Filtreleme:** VDD hattına 100nF kondansat paralel bağlayın. Bu, güç hattı gürültüsünü filtreler ve ses kalitesini artırır.

---

## 💡 LED Şerit Bağlantısı (WS2812B)

| WS2812B Pin | ESP32 Pin | İşlev |
|---|---|---|
| **5V / VCC** | Harici 5V güç kaynağı | ⚠️ ESP32'nin 3.3V pin'i yetersiz! Harici güç şart |
| **GND** | GND (ortak) | Toprak — ESP32 ve güç kaynağı ortak GND |
| **DIN (Data In)** | **GPIO 2** | LED veri hattı |
| **DOUT** | — | Bir sonraki LED şeride bağlanır (zincirleme) |

> **Güç Notu:** 60 LED'lik bir WS2812B şerit tam parlaklıkta ~3.6A çeker. ESP32'nin onboard regülatörü sadece ~500mA verebilir. **Harici 5V/4A güç kaynağı kullanın.** Veri hattına 330Ω direnç seri bağlayın (geri besleme koruması).

---

## 🎨 Difüzör Profil: Neden Şart?

### Sorun: Çıplak LED'ler

WS2812B LED'ler, **noktasal ışık kaynaklarıdır**. Her LED ayrı ayrı görülür — bu, "oyuncu odası" veya "pavyon" hissi yaratır. Çıplak LED'ler:

- **Gözü yorar:** Noktasal ışık retina'da lokal aşırı uyarım yaratır
- **Premium hissi bozar:** Lüks otellerde LED'ler asla çıplak görünmez; her zaman bir difüzör arkasındadır
- **Renk karışımını bozar:** Bitişik LED'ler arasındaki renk geçişi keskindir; pürüzsüz gradyan istenmez

### Çözüm: Silikon / Alüminyum Difüzör Profil

| Profil Tipi | Malzeme | Etki | Fiyat |
|---|---|---|---|
| **Silikon difüzör** | Opak silikon tüp | LED'leri yumuşak bir çizgiye dönüştürür | ~$2/metre |
| **Alüminyum + opak akrilik** | Alüminyum kanal + mat akrilik kapak | En premium görünüm; ışık duvar yüzeyine homojen yansır | ~$8/metre |
| **Mat akrilik tüp** | Mat akrilik silindir | LED'leri tamamen gizler; sadece ışık görünür | ~$5/metre |

### Psikolojik Etki

```
  ÇIPLAK LED (Oyuncu Odası)          DİFÜZÖRLÜ LED (Premium Lounge)
  ┌──────────────────────┐           ┌──────────────────────┐
  │  ●  ●  ●  ●  ●  ●  ● │           │  ░░░░░░░░░░░░░░░░░░░ │
  │  ●  ●  ●  ●  ●  ●  ● │           │  ░░░░░░░░░░░░░░░░░░░ │
  │  ●  ●  ●  ●  ●  ●  ● │           │  ░░░░░░░░░░░░░░░░░░░ │
  └──────────────────────┘           └──────────────────────┘
  Noktasal, keskin, ucuz             Homojen, yumuşak, premium
  Dikkat dağıtıcı                    Sakinleştirici
  "Gamer" hissi                      "Lounge/otel" hissi
```

> **Öneri:** Alüminyum kanal + mat akrilik kapak. Alüminyum, LED'leri soğutur (ömür uzar) ve mat akrilik, ışığı mükemmel homojenize eder. Misafir LED'leri değil, sadece ışığı görür.

### Montaj Konumu

- **Tavan pervazı:** LED şerit tavan ile duvar birleşimine, difüzör profil içinde gizlenir. Işık duvara yansır → "dolaylı aydınlatma" (indirect lighting) — lüks otellerin standardı.
- **Yatak başı arkası:** LED'ler yatak başı panelinin arkasına gizlenir. Işık duvara yansır → yumuşak, sıcak ambiyans.
- **Asla doğrudan göz hizasında:** Çıplak LED'ler göz hizasında olmamalı; difüzör olsa bile. Işık her zaman bir yüzeye yansımalı.

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | Dual-core, FPU, I2S desteği |
| 2 | Dijital Mikrofon | INMP441 I2S | 1 | 24-bit, düşük gürültü |
| 3 | LED Şerit | WS2812B (60 LED/m) | 2-5m | Oda boyutuna göre |
| 4 | Güç Kaynağı | 5V 4A | 1 | LED şerit için harici güç |
| 5 | Difüzör Profil | Alüminyum + mat akrilik | LED şerit boyu | Premium görünüm için şart |
| 6 | Kondansatör | 100nF | 1 | INMP441 VDD filtresi |
| 7 | Direnç | 330Ω | 1 | WS2812B veri hattı koruması |
| 8 | Jumper Wire | Dişi-Dişi | 6 | INMP441 → ESP32 bağlantısı |

---

## ✅ Kurulum Kontrol Listesi

- [ ] ESP32'ye Sound Reactive WLED firmware yüklendi (https://install.wled.me/ → Audio Reactive sürüm)
- [ ] INMP441 mikrofon bağlandı (VDD→3.3V, GND→GND, SD→GPIO32, WS→GPIO15, SCK→GPIO14, L/R→GND)
- [ ] VDD hattına 100nF kondansatör eklendi
- [ ] WS2812B LED şerit bağlandı (5V→harici güç, GND→ortak, DIN→GPIO2, 330Ω direnç)
- [ ] LED şerit alüminyum + mat akrilik difüzör profile yerleştirildi
- [ ] Difüzör profil tavan pervazına veya yatak başı arkasına monte edildi
- [ ] WLED web arayüzüne erişildi (http://wled-ambient.local)
- [ ] WLED → User Settings → Audio → I2S mikrofon yapılandırıldı (pins doğrulandı)
- [ ] Ses reaktif efektler test edildi (Gravimeter, Freqwave)
- [ ] WLED HA entegrasyonu yapıldı (light.wled_ambient entity_id)
- [ ] `wled_api_presets.json` preset'leri WLED'e yüklendi
- [ ] `audio_wled_automation.yaml` HA'a yüklendi