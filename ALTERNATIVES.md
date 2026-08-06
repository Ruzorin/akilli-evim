# 🔄 ALTERNATIVES.md — Ekipman Alternatifleri ve Karşılaştırma Rehberi

> Bu dosya, projedeki her ekipman için önerilen model + alternatifler + neden bu modeli önerdiğimizi listeler. "Neden bu değil şu?" sorusunun cevabı burada.

---

## 🧠 Yapay Zeka ve Ses (Maliyet Devrimi — Ağustos 2026)

### Sesten-Sese (Speech-to-Speech) API

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | MiniMax Speech 2.8 Turbo | MiniMax Realtime API (DeepSeek V4-Pro) | MiniMax Voice Cloning + MiniMax Sesten-Sese (STT/TTS ayrı) |
| **Fiyat** | ~$10/ay | ~$50-100/ay | ~$15/ay (STT + TTS ayrı) |
| **Neden önerilen?** | Sesten-sese TEK katman (<300ms), Voice Cloning dahil (ekstra $0), duygu kontrol, WebSocket streaming. En düşük maliyet + en düşük gecikme | İyi ama ASTRONOMİK fatura. STT/TTS ara katmanları var (2-3sn gecikme). Voice Cloning yok | STT + TTS ayrı → 3 ara katman → 2-3sn gecikme. Voice Cloning var ama ekstra $5/ay. MiniMax'ten pahalı ve yavaş |

### Ağır Zeka (Kod, Analiz, Özet)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | DeepSeek V4-Pro | DeepSeek V4-Pro | Claude 3.5 Sonnet |
| **Fiyat** | ~$1-2/ay | ~$10-15/ay | ~$10/ay |
| **Neden önerilen?** | Çok ucuz (~$0.01/istek), kod yazma ve özet için yeterli. MiniMax ses token maliyetine girmeden düşünme işini ucuz beyne devret | İyi ama pahalı. Kod/özet için gereksiz güç → gereksiz maliyet | İyi ama DeepSeek'ten pahalı. Kod yazmada DeepSeek daha iyi |

### Görüntü Analizi (Vision)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Qwen-VL Max | Qwen-VL Max | Gemini 1.5 Pro Vision |
| **Fiyat** | ~$2/ay | ~$10/ay | ~$8/ay |
| **Neden önerilen?** | Ucuz (~$0.02/görüntü), Çince/İngilizce görsel analizi güçlü, mutfak/stil analizi için yeterli | İyi ama pahalı. Vision token maliyeti yüksek | İyi ama Qwen-VL'den pahalı. Bazı görüntü tiplerinde zayıf |

---

## 🌐 Genel Altyapı

### Yönlendirici

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | GL-MT3000 (Beryl AX) | GL-AXT1800 (Slate AX) | Raspberry Pi 4 + OpenWrt |
| **Fiyat** | ~$80 | ~$130 | ~$55 |
| **Neden önerilen?** | WiFi 6, Tailscale yerleşik, küçük boyut, USB port (Zigbee dongle), düşük güç tüketimi. Yurt odası için ideal boyut | Daha güçlü CPU ama yurt odası için fazla. Daha pahalı | Esnek ama Tailscale kurulumu manuel, WiFi 6 yok, daha büyük |

### VPS

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | DigitalOcean / Hetzner | AWS EC2 | Kendi sunucun (evde) |
| **Fiyat** | ~$10/ay | ~$15-25/ay | Elektrik + internet |
| **Neden önerilen?** | Ucuz, sabit IP, Docker desteği, kolay kurulum. Hetzner Avrupa'da daha ucuz | Daha pahalı, karmaşık faturalandırma. Yurt odası için gereksiz güç | İnternet kesilirse HA çöker. Kıb-Tek kesintileri sık. VPS daha güvenilir |

### Zigbee Koordinatör

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | CC2652R USB dongle | ConBee II | Sonoff ZBDongle-E |
| **Fiyat** | ~$25 | ~$30 | ~$20 |
| **Neden önerilen?** | Zigbee2MQTT ile en uyumlu, açık kaynak firmware, güçlü sinyal, çoklu cihaz desteği | İyi ama kendi yazılımı (deCONZ) kullanır, Zigbee2MQTT ile uyumu sınırlı | Ucuz ama bazı cihazlarla uyumsuzluk yaşanabilir |

### Akıllı Priz (Güç Ölçümlü)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Shelly Plug S | Tapo TP-Link P110 | Sonoff S31 |
| **Fiyat** | ~$15 | ~$15 | ~$12 |
| **Neden önerilen?** | Doğrudan MQTT yayınlar (HA entegrasyon gerekmez), 0.1W hassasiyet, yerel kontrol, hızlı yanıt. Barista modu güç ölçümü için kritik | İyi ama HA bulut entegrasyonu gerekir, yerel değil. Bulut gecikmesi olabilir | Ucuz ama Tasmota firmware gerekir, kutudan çıkmış haliyle yerel değil |

### Akım Korumalı Priz (Surge Protector)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | APC SurgeArrest | Brennenstuhl | Tunçmatik |
| **Fiyat** | ~$25-40 | ~$30 | ~$35 |
| **Neden önerilen?** | Dünya standardı, garanti, LED koruma göstergesi, Kıb-Tek dalgalanmaları için yeterli joule rating | Avrupa standardı, iyi ama Türkiye/Kıbrıs'ta bulunabilirlik düşük | Türkiye/Kıbrıs uyumlu, yerel priz tipi, bulunabilirlik iyi |

---

## 🧠 Modül 1: jarvis_core

### Mikrodenetleyici (Audio Hub)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | ESP32-S3 DevKit | ESP32 DevKit V1 | Raspberry Pi Zero 2 W |
| **Fiyat** | ~$8 | ~$5 | ~$15 |
| **Neden önerilen?** | I2S + Bluetooth Proxy + WiFi aynı anda. HFP (Hands-Free) desteği. 240MHz dual-core. Çağrı yönlendirme için Bluetooth Proxy gerekiyor → S3 şart | I2S var ama Bluetooth Proxy + HFP desteği zayıf. Çağrı yönlendirme için yetersiz | Güçlü ama I2S mikrofon için GPIO yetersiz, Bluetooth Proxy karmaşık, fazla güç tüketir |

### Dijital Mikrofon

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | INMP441 I2S | MAX9814 (analog) | USB Mikrofon |
| **Fiyat** | ~$5 | ~$3 | ~$10 |
| **Neden önerilen?** | Dijital I2S → gürültüsüz, ESP32 ile doğrudan bağlantı, STT için temiz ses. Analog mikrofonlarda ADC gürültüsü var | Ucuz ama analog → ADC gürültüsü, bas frekansları zayıf. STT için yetersiz | Kolay ama I2S değil, USB üzerinden → ESP32 ile uyumsuz, Pi gerekir |

### IP Kamera (Yüz Tanıma)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | TP-Link Tapo C200 | Reolink E1 Pro | USB Web Kamera |
| **Fiyat** | ~$25 | ~$45 | ~$25 |
| **Neden önerilen?** | RTSP desteği, ucuz, WiFi, 720p yeterli (yüz tanıma için). HA ve OpenCV ile uyumlu | Daha iyi çözünürlük ama pahalı, yurt odası için fazla | Ucuz ama WiFi değil (USB), kablo gerekir, RTSP yok |

### Python Sunucu

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Raspberry Pi 4 (4GB) | Raspberry Pi 5 (8GB) | Mini PC (Intel NUC) |
| **Fiyat** | ~$55 | ~$100 | ~$150 |
| **Neden önerilen?** | ChromaDB + face_recognition + multi_model_orchestrator için yeterli RAM. Düşük güç. Sessiz. Yurt odası için ideal | Daha güçlü ama gereksiz — 4GB yeterli. Daha pahalı, daha sıcak | Güçlü ama pahalı, büyük, fan sesi var. Yurt odası için fazla |

---

## 🔘 Modül 2: hidden_triggers

### Zigbee Mini Buton

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Sonoff ZBMINI / Tuya | IKEA TRÅDFRI | Aqara Mini Switch |
| **Fiyat** | ~$10 | ~$8 | ~$15 |
| **Neden önerilen?** | Çok küçük (40mm), CR2032 pil, 1-2 yıl ömrü, Zigbee2MQTT ile tam uyum. Tek/çift/uzun basma desteği | Ucuz ama daha büyük, bazı modeller tek tık sadece. Jest çeşitliliği az | İyi ama daha pahalı, Apple HomeKit odaklı, Zigbee2MQTT ile bazı sorunlar |

### Kapasitif Dokunmatik Sensör

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | TTP223 | MPR121 | Capacitive Soil Sensor (modifiye) |
| **Fiyat** | ~$2 | ~$8 | ~$5 |
| **Neden önerilen?** | Ucuz, ahşaptan algılama (5-10mm), tek pin, ESPHome ile tam uyum. "DIY sihir" için ideal | 12 kanal ama ahşap algılama zayıf, karmaşık, fazla pahalı bu iş için | Toprak nem sensörü — ahşap için tasarlanmamış, güvenilmez |

---

## 🌌 Modül 3: space_projection

### Galaksi Projeksiyon

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Tuya Galaxy Projector | BlissLights Sky Lite | DIY: Pi + Projektör |
| **Fiyat** | ~$30 | ~$60 | ~$100+ |
| **Neden önerilen?** | Tuya/SmartLife uyumlu → LocalTuya ile HA kontrol. Nebula + lazer (lazer kapatılabilir). Ucuz. WiFi | Daha kaliteli ama Tuya değil, HA entegrasyonu zor, IR kumanda sadece | Tam kontrol ama pahalı, karmaşık, fazla güç tüketir |

---

## 🪞 Modül 4 & 20: Magic Mirror

### Two-Way Mirror

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Two-way mirror akrilik | Two-way mirror cam | Görüntülü ayna filmi (DIY) |
| **Fiyat** | ~$40 | ~$80-120 | ~$20 |
| **Neden önerilen?** | Hafif, kolay kesim, ucuz, LCD arkasına kolay monte. Akrilik → kırılmaz, yurt odası için güvenli | Daha kaliteli yansıma ama ağır, kırılabilir, pahalı. Kesim zor | Ucuz ama kalite düşük, hava kabarcıkları, uygulanması zor |

### Mikro Bilgisayar (MagicMirror²)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Raspberry Pi Zero 2 W | Raspberry Pi 4 | ESP32 (WLED tabanlı) |
| **Fiyat** | ~$15 | ~$55 | ~$5 |
| **Neden önerilen?** | MagicMirror² için yeterli, çok küçük (ayna arkasına gizler), WiFi, düşük güç. Sessiz | Daha güçlü ama gereksiz — MagicMirror² Pi Zero'da yeterince hızlı. Daha sıcak, daha büyük | MagicMirror² çalışmaz — ESP32'de browser yok. Sadece WLED için |

### USB Kamera (Modül 20)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Logitech C270 | Logitech C920 | Generic 720p USB cam |
| **Fiyat** | ~$25 | ~$60 | ~$10 |
| **Neden önerilen?** | 720p yeterli (stil analizi + görüntülü arama), ucuz, küçük, aynaya gizlenir. Linux uyumlu | 1080p ama pahalı, büyük, aynaya gizlemek zor. Gereksiz yüksek çözünürlük | Ucuz ama Linux uyumu sorunlu, driver eksik, kalite düşük |

---

## 🔊 Modül 5: Spatial Audio

### Akıllı Hoparlör

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Echo Dot 5. Gen (×2) | Nest Mini 2. Gen (×2) | Sonos One (×2) |
| **Fiyat** | ~$50/çift | ~$60/çift | ~$400/çift |
| **Neden önerilen?** | Ucuz, stereo pair desteği, Alexa Media Player (HACS) ile HA tam kontrol, Spotify Connect. "Cocoon Effect" için yeterli | İyi ama Google Home stereo pair bazı bölgelerde yok, HA entegrasyonu daha sınırlı | En iyi ses kalitesi ama çok pahalı. Yurt odası için gereksiz. Overkill |

---

## 🛏️ Modül 6: Underbed Lighting

### mmWave Radar

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | HLK-LD2410B | HLK-LD2450 | PIR (HC-SR501) |
| **Fiyat** | ~$5 | ~$8 | ~$2 |
| **Neden önerilen?** | Varlık + mikro-hareket algılama, Gate bazlı mesafe, ESPHome tam uyum, ucuz. Yatak altı için ideal — hareketsizken kapanmaz | Çoklu hedef takibi + X/Y koordinatları ama Gate bazlı mesafe filtresi daha karmaşık. Kalp/nefes ÖLÇMEZ (sadece varlık/hareket) | Ucuz ama hareketsizken kapanır, yatakta dönmeyi algılar, gece ışık yanıp söner. PIR bu iş için YANLIŞ |

### LED Şerit

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | COB LED (12V sıcak beyaz) | WS2812B (adreslenebilir) | LED şerit (sabit beyaz) |
| **Fiyat** | ~$10/m | ~$5/m | ~$3/m |
| **Neden önerilen?** | Pürüzsüz sürekli ışık çizgisi → "Floating Bed" illüzyonu. Noktasal LED yok. Premium his. Sıcak beyaz gece için ideal | Noktasal LED → "disco" hissi. Difüzör gerekir. COB daha iyi bu iş için. Adreslenebilir ama gereksiz — tek renk yeterli | Ucuz ama noktasal, premium değil, "oyuncu odası" hissi |

---

## 🌅 Modül 7: Morning After

### Perde Motoru

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | SwitchBot Curtain | Tuya Perde Motoru | Aqara Curtain Driver |
| **Fiyat** | ~$90 | ~$35 | ~$70 |
| **Neden önerilen?** | Kornişe vidalama yok, kolay takım, sessiz (~40dB), HA entegrasyonu, U-rail + rod uyumlu | Ucuz ama kurulum daha teknik, bazı perde tipleriyle uyumsuz, kalite değişken | İyi ama pahalı, sadece belirli ray tipleri, Zigbee ama Aqara ekosistemi |

---

## 📡 Modül 8: Invisible Remote

### IR Blaster

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Broadlink RM4 Mini | ESP32 + IR LED (DIY) | Tuya IR Blaster |
| **Fiyat** | ~$20 | ~$6 | ~$15 |
| **Neden önerilen?** | Hazır ürün, 360° IR, HA entegrasyonu, SmartIR ile klima kod veritabanı. Kurulum kolay | Ucuz ama lehim gerekir, ESPHome IR kodu yaz, 360° değil (tek yön). Daha teknik | Ucuz ama LocalTuya gerekir, bazı modellerde IR kod öğrenme sınırlı |

---

## 🌿 Modül 9: Smart Diffuser

### Akıllı Difüzör

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Tuya WiFi Difüzör | "Dumb" Difüzör + Akıllı Priz | Aromatherapy Diffuser (Zigbee) |
| **Fiyat** | ~$25 | ~$15 + ~$15 priz | ~$40 |
| **Neden önerilen?** | LocalTuya ile tam kontrol (aç/kapa, buhar hızı, RGB kapatma, zamanlayıcı). WiFi → bulut gecikmesi yok. RGB kapatılabilir → WLED ile çakışmaz | Ucuz ama buhar hızı ayarı yok, RGB kapatılamaz (fiziksel bant gerekir). Sadece aç/kapa | İyi ama pahalı, Zigbee range sınırlı, marka uyumluluğu sorunlu |

### Esans Yağları

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Monin / Plant Therapy | Doğal uçucu yağ (organik) | Ucuz sentetik esans |
| **Fiyat** | ~$15 | ~$25 | ~$5 |
| **Neden önerilen?** | Profesyonel kalite, barista/cafe standardı, tutarlı koku profili. Misafir "otel lobisi" hisseder | En saf ama pahalı, bazıları difüzörde tortu bırakır, kalite değişken | Ucuz ama sentetik → baş ağrısı, kimyasal koku, "premium" hissi bozar |

---

## 💡 Modül 10: Audio Reactive WLED

### Mikrodenetleyici

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | ESP32 DevKit V1 | ESP8266 | Raspberry Pi Pico |
| **Fiyat** | ~$5 | ~$3 | ~$4 |
| **Neden önerilen?** | FFT için donanımsal FPU (float), I2S mikrofon desteği, dual-core 240MHz. Sound Reactive WLED ESP32 gerektirir. ESP8266'da FFT yazılım emülasyonu → 200-500ms gecikme | Ucuz ama FPU yok → FFT çok yavaş, I2S yok → dijital mikrofon kullanılamaz. Bu modül için YANLIŞ | İyi ama WLED firmware yok, I2S desteği sınırlı, topluluk desteği az |

### Dijital Mikrofon (WLED için)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | INMP441 I2S | MAX9814 (analog) | I2S Mic (SPH0645) |
| **Fiyat** | ~$5 | ~$3 | ~$8 |
| **Neden önerilen?** | I2S dijital → gürültüsüz, ESP32 ile doğrudan, Sound Reactive WLED ile tam uyum. Bas frekansları temiz algılanır | Ucuz ama analog → ADC gürültüsü, bas frekansları zayıf. FFT için kötü sinyal | Daha iyi ama pahalı, pin uyumu farklı, bazı WLED sürümlerinde sorun |

### LED Şerit

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | WS2812B (60 LED/m) | SK6812 (RGBW) | COB LED |
| **Fiyat** | ~$5/m | ~$7/m | ~$10/m |
| **Neden önerilen?** | En yaygın, WLED tam uyum, ucuz, adreslenebilir. Sese duyarlı efektler için ideal. 60 LED/m → akıcı efektler | RGBW (beyaz kanal) ama daha pahalı, WLED'de bazı efektler farklı. Beyaz renk için daha iyi ama bu modülde renkli efektler kullanıyoruz | Pürüzsüz ama adreslenebilir değil → sese duyarlı efektler YAPILAMAZ. Sabit renk sadece |

### Difüzör Profil

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Alüminyum + mat akrilik | Silikon difüzör tüp | Difüzör YOK (çıplak LED) |
| **Fiyat** | ~$8/m | ~$2/m | $0 |
| **Neden önerilen?** | En premium görünüm — LED'ler tamamen gizli, ışık homojen, alüminyum soğutma. "Lüks otel" hissi. Misafir LED'leri değil ışığı görür | Ucuz, iyi difüzyon ama alüminyum yok → soğutma yok (ömür kısalır), görünüm daha az premium | Bedava ama "oyuncu odası" hissi → noktasal LED'ler görünür → premium bozulur |

---

## ☕ Modül 11: Barista Mode

### Kahve Makinesi

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Fiziksel anahtarlı + Akıllı Priz | Dijital anahtarlı + Fingerbot | Tam akıllı kahve makinesi |
| **Fiyat** | ~$15 (priz) | ~$15 + ~$15 (Fingerbot) | ~$200+ |
| **Neden önerilen?** | En basit ve güvenilir. Güç anahtarı ON → priz aç → ısınma başlar. Kapsül makinesi (Nespresso) için ideal | Dijital anahtarlı makineler için (Sage, Breville) → Fingerbot düğmeye basar. Ama montaj hassas | Pahalı, gereksiz. Akıllı priz + dumb makine = aynı iş, çok daha ucuz |

---

## ❤️‍🔥 Modül 12: Intimacy Sync

### İvmeölçer

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | MPU6050 (6-DoF) | MPU9250 (9-DoF) | ADXL345 |
| **Fiyat** | ~$3 | ~$5 | ~$3 |
| **Neden önerilen?** | 3 eksen ivme + 3 eksen jiroskop → yatak ritmi için yeterli. I2C, ESP32 ile kolay. Ucuz. 6-DoF bu iş için yeterli — 9-DoF fazla | 9-DoF (manyetik + ivme + jiroskop) ama manyetik sensör yatak altında gereksiz, pusula gerekmez. Daha pahalı, fazla | Ucuz ama sadece ivme (3-DoF), jiroskop yok → dönme algılama zayıf. Ritim için yeterli ama MPU6050 daha iyi |

---

## 🧑‍🍳 Modül 13: Vision Chef

### IP Kamera (Mutfak)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | TP-Link Tapo C200 | Reolink E1 Zoom | USB Kamera + Uzatma |
| **Fiyat** | ~$25 | ~$50 | ~$15 |
| **Neden önerilen?** | RTSP, WiFi, ucuz, 720p yeterli (tezgah analizi). Mutfak dolabı altına gizli. HA + OpenCV uyumlu | Daha iyi zoom ama pahalı, gereksiz — tezgah sabit mesafe. Overkill | Ucuz ama USB → kablo uzunluğu sınırlı (5m max), WiFi değil, dolap altından zor |

---

## 🧬 Modül 16: Life OS

### Kalp Atışı / Nefes Sensörü

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Akıllı Saat (Apple Watch / Wear OS) | HLK-LD6002 (60GHz Vital Signs Radar) | Seeed Studio MR60BHA2 (60GHz) |
| **Fiyat** | ~$200 (mevcut) | ~$25-40 | ~$50-70 |
| **Neden önerilen?** | Kullanıcının zaten sahip olduğu saat → ekstra maliyet $0. Apple Health / Google Fit → HA webhook → nabız, uyku, adım. En güvenilir ve en kolay kalp atışı kaynağı | 60GHz — temassız kalp atışı (BPM) + solunum ölçer. Yatak başucuna monte, 1.5m mesafe, göğüs hizası. ESPHome topluluğunda hazır YAML var. Uyku takibi için ideal | En hassas 60GHz vital signs radar ama pahalı, nadir bulunur, ESPHome desteği sınırlı. LD6002 daha ucuz ve yeterli |

> ⚠️ **KRİTİK SENSÖR UYARISI:**
> - **LD2410 / LD2450:** Sadece varlık/hareket algılar. Kalp atışı ve nefes ÖLÇMEZ. "Heartbeat Detection" ibaresi pazarlama yanıltmacasıdır.
> - **LD2420:** 24GHz — sadece varlık/hareket. Kalp atışı ÖLÇMEZ.
> - **LD6001:** 60GHz — çoklu kişi takibi + konum (X/Y). Kalp atışı ÖLÇMEZ.
> - **LD6002:** 60GHz — temassız kalp atışı (BPM) + solunum ölçer. ✅ BU sensör kalp atışı ölçer.
> - **MR60BHA2:** 60GHz — temassız kalp atışı + solunum. ✅ Alternatif.
> - **Akıllı saat:** En güvenilir ve en kolay kalp atışı kaynağı. Ekstra donanım gerekmez.
>
> Eğer temassız radar tabanlı kalp atışı ölçümü istiyorsanız: **HLK-LD6002** kullanın (yatak başucuna monte, 1m mesafe, göğüs hizası).
> Çift kişilik yatakta: sağ ve sol başucuna iki ayrı LD6002 yerleştirin, Gate/mesafe ayarını daraltın.

---

## 🎬 Modül 17: Hyperion

### HDMI Grabber

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | UCV007 / MS2109 | Ezcap 284 | Generic USB 2.0 grabber |
| **Fiyat** | ~$10 | ~$20 | ~$5 |
| **Neden önerilen?** | Düşük gecikme (<50ms), Hyperion ile uyumlu, ucuz, 1080p@30fps. En iyi fiyat/performans | Daha iyi kalite ama pahalı, Hyperion ile bazı sorunlar, fazla | Ucuz ama yüksek gecikme (200ms+), görüntü bozuk, Hyperion için YANLIŞ |

---

## 📱 Modül 18: SuperApp

### HA Custom Cards

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Mushroom + Bubble Card | HA varsayılan kartlar | Hui-Flow + Tile Card |
| **Fiyat** | $0 (HACS) | $0 | $0 (HACS) |
| **Neden önerilen?** | Mushroom: yuvarlak, minimalist, Apple tarzı. Bubble: swipeable, pop-up. İkisi birlikte = Tesla/Apple UI. "Kontrol paneli" değil "yaşam alanı" | Kare, düz, kalabalık → "endüstriyel kontrol paneli" hissi. Premium değil | İyi ama daha az topluluk desteği, bazı özellikler eksik, Bubble kadar esnek değil |

---

## 📞 Modül 19: CEO Call Mode

### I2S DAC (Hoparlör Sürücü)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | MAX98357A | PCM5102 | LM386 (analog) |
| **Fiyat** | ~$3 | ~$5 | ~$2 |
| **Neden önerilen?** | I2S → analog, 3W amplifiyer, ESP32 ile doğrudan, ucuz. Çağrı sesi için yeterli. Hoparlör sürücü entegre | Daha iyi ses kalitesi ama pahalı, fazla pin, çağrı için gereksiz (8kHz ses) | Ucuz ama analog → I2S değil, DAC gerekir, gürültü, çağrı için kötü |

---

## 🪞 Modül 20: Mirror Comm

### USB Hub

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Mini 4-port USB hub | Pi Zero USB HAT | Bluetooth dongle (kamera yerine) |
| **Fiyat** | ~$5 | ~$10 | ~$5 |
| **Neden önerilen?** | Ucuz, küçük, Pi Zero'nun tek portuna kamera + mikrofon. Ayna arkasına gizlenir. Basit | Daha düzenli ama pahalı, ayna arkasında yer kaplar | Kamera BT değil → dongle işe yaramaz. USB kamera + hub şart |

---

## 🚗 Modül 21: Car Knight Rider Core

### Android Multimedya Ekranı

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | 9-10" Universal Android Head Unit | Araç markası orijinal ekran (Android Auto) | Tablet + dashboard mount |
| **Fiyat** | ~$150-250 | ~$500+ (araç markası) | ~$100 (tablet) |
| **Neden önerilen?** | Universal fit (2005+), Android 10+, Play Store, HA Companion App, Tailscale, ucuz. Araç içine gizli monte | Orijinal ama pahalı, markaya özel, HA kurulumu sınırlı, Android Auto değil tam Android | Ucuz ama dashboard mount sabit değil, kablo karmaşası, profesyonel değil |

### OBD2 Adaptör

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | ELM327 Bluetooth | ELM327 Wi-Fi | ESP32 + CAN Bus shield |
| **Fiyat** | ~$15-25 | ~$20 | ~$20 |
| **Neden önerilen?** | Ucuz, yaygın, Torque/Car Scanner uyumlu, Bluetooth → Android. Temel OBD2 okuma için yeterli | Daha hızlı veri (10 Hz) ama Wi-Fi → Bluetooth'tan daha çok güç tüketir, bazı araçlarda karışıklık | En gelişmiş (CAN Bus direkt) ama teknik, lehim gerekir, fazla karmaşık bu iş için |

---

## 🔮 Modül 22: Car Omniscience Copilot

### IR Kamera (Sürücü Yüzü / PERCLOS)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | FLIR One Pro (USB-C) | Seek Thermal Compact | Web kamera + OpenCV (göz kırpma) |
| **Fiyat** | ~$200 | ~$180 | ~$25 |
| **Neden önerilen?** | Termal → gece görüş (sürüş çoğu zaman gece), PERCLOS için ideal, Android USB-C, profesyonel | İyi ama FLIR'dan daha az çözünürlük, bazı Android'lerde uyumsuzluk | Ucuz ama gece görüş yok → karanlıkta göz kırpma algılanamaz. Sürüş için YANLIŞ |

---

## 🌑 Modül 23: Car Stealth & Seduction

### Araç İçi WLED

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | WS2812B + ESP32 (ayak/kapı) | COB LED (sabit renk) | Araç içi LED şerit (12V analog) |
| **Fiyat** | ~$5 (1m) | ~$10 (1m) | ~$3 (1m) |
| **Neden önerilen?** | Adreslenebilir → efekt (Breathe, Strobe), MQTT → HA kontrol, renk değişimi (kırmızı/amber/mavi). Seduction + Blackout için şart | Pürüzsüz ama sabit renk → efekt yok, Strobe yapılamaz, HA kontrol yok | Ucuz ama tek renk, efekt yok, HA entegrasyonu yok |

---

## 🚀 Modül 24: Car Edge-AI Vision

### Edge-AI Bilgisayar

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Nvidia Jetson Nano 4GB | Raspberry Pi 5 (8GB) | Coral USB Accelerator |
| **Fiyat** | ~$150 | ~$100 | ~$70 |
| **Neden önerilen?** | 128 CUDA core + TensorRT → YOLO FP16 30 FPS. GPU + CUDA şart (ADAS için). JetPack SDK hazır. Araç içi güç tüketimi düşük | CPU güçlü ama GPU yok → YOLO CPU'da 5 FPS → sürüş için yetersiz. TensorRT yok | Ucuz ama sadece inference accelerator (TPU) → tam bilgisayar değil, kamera/ekran yönetimi için ayrı sistem gerekir |

### Kamera (ADAS)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Sony IMX219 CSI-2 (8MP) | USB Web Kamera (Logitech C920) | Raspberry Pi Camera V2 |
| **Fiyat** | ~$25 | ~$60 | ~$25 |
| **Neden önerilen?** | CSI-2 → Jetson Nano'ya doğrudan, düşük gecikme, 70° FOV, dikiz aynası arkasına gizli. Araç içi için ideal | 1080p ama USB → gecikme daha yüksek, CSI-2'den yavaş, araç içi kablo uzun | IMX219 ile aynı sensör ama Raspberry Pi için → Jetson'da bazı pin uyumsuzlukları |

---

---

## 🛡️ Modül 25: Car Sentry Mode Security

### PIR Hareket Sensörü

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | HC-SR501 mini | AM312 (daha küçük) | mmWave LD2410 (araç içi) |
| **Fiyat** | ~$2 | ~$3 | ~$5 |
| **Neden önerilen?** | Ucuz, 12V uyumlu, düşük güç (~0.05W), ayarlanabilir hassasiyet, Jetson GPIO'ya doğrudan. Araç içi için ideal | Daha küçük ama menzil kısa (3m), hassasiyet ayarı yok | En iyi (varlık + mikro-hareket) ama pahalı, Deep Sleep'te daha çok güç çeker, bu iş için overkill |

### Akıllı Röle (Akü Koruması)

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | 12V→5V DC-DC + voltaj sensörü | Basit 12V→5V adaptör (voltaj sensörsüz) | ESP32 + voltaj divider (ADC) |
| **Fiyat** | ~$10 | ~$5 | ~$8 |
| **Neden önerilen?** | Voltaj sensör → akü <11.5V'de otomatik keser. Aküyü bitirmez. Araç için KRİTİK | Ucuz ama akü koruması yok → akü bitebilir → araç çalışmaz | İyi ama fazla karmaşık, ESP32 ayrı güç ister, bu iş için overkill |

### Anlık Bildirim Kanalı

| | Önerilen | Alternatif 1 | Alternatif 2 |
|---|---|---|---|
| **Model** | Telegram Bot API | WhatsApp Business API | HA Companion App push |
| **Fiyat** | $0 | $0 (Meta Developer) | $0 |
| **Neden önerilen?** | Ücretsiz, BotFather → 30sn'de bot oluştur, fotoğraf + metin, anlık push, API limiti yüksek | İyi ama Meta Developer hesabı + onaylı numara gerekir, kurulum karmaşık, bazı ülkelerde kısıtlı | Kolay ama sadece HA Companion App → Telegram kadar hızlı değil, fotoğraf kalitesi sınırlı |

---

*Bu dosya, her ekipman için "neden bu?" sorusunu yanıtlar. Yeni alternatifler bulundukça güncellenir.*