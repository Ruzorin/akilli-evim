# 📋 EQUIPMENT.md — Akıllı Yurt Odası Teçhizat Listesi

> Bu dosya, projenin tüm 14 modülü için gereken donanım, sensör, kablo ve materyallerin eksiksiz listesidir. Modüllere göre sıralanmıştır.

---

## 🌐 Genel Altyapı

| # | Bileşen | Model / Tip | Adet | Modül | Fiyat (≈) | Not |
|---|---|---|---|---|---|---|
| 1 | VPS | DigitalOcean / Hetzner (2 vCPU, 4GB RAM) | 1 | Tümü | ~$10/ay | Home Assistant Docker + Tailscale |
| 2 | Yönlendirici | GL-MT3000 (Beryl AX) | 1 | Tümü | ~$80 | WiFi 6 + Tailscale client + MQTT broker |
| 3 | Tailscale VPN | Tailscale (ücretsiz plan) | — | Tümü | $0 | VPS ↔ GL-MT3000 şifreli tünel |
| 4 | Home Assistant | HA Core (Docker) | 1 | Tümü | $0 | VPS üzerinde Docker |
| 5 | Zigbee2MQTT | Z-Stack dongle (CC2652R) | 1 | Tümü | ~$25 | Zigbee koordinatör |
| 6 | Akıllı Priz (Güç Ölçümlü) | Shelly Plug S | 3-4 | 8, 11, 13 | ~$15/adet | Klima, kahve, ocak güç izleme |
| 7 | **Akım Korumalı Priz (Surge Protector)** | APC / Brennenstuhl / Tunçmatik | 2 | Tümü | ~$25-40/adet | Kıb-Tek şebeke dalgalanmalarına karşı GL-MT3000, Pi 4, Pi Zero ve LCD monitörü korur. Tüm emeğin tek bir şimşek çakmasıyla çöp olmasını engeller |
| 8 | **UPS (Kesintisiz Güç Kaynağı)** | APC Back-UPS 600VA (opsiyonel) | 1 | Tümü | ~$50-70 | Şebeke kesintisinde GL-MT3000 + Pi 4'ü 10-15 dk çalıştırır (HA çökmesini engeller) |

---

## 🧠 Modül 1: jarvis_core (Sistemin Beyni)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32-S3 DevKit | 1 | ~$8 | Audio hub (mikrofon + hoparlör yönetimi) |
| 2 | Dijital Mikrofon | INMP441 I2S | 1 | ~$5 | Komodin içinde gizli, 24-bit |
| 3 | IP Kamera (Yüz Tanıma) | TP-Link Tapo C200 | 1 | ~$25 | RTSP, oturma alanı için |
| 4 | Akıllı Hoparlör | Echo Dot 5. Gen (veya Nest Mini) | 2 | ~$50/çift | Stereo pair (spatial audio) |
| 5 | OpenAI API | **GPT-5.6-Realtime** + GPT-5.6 Vision | — | ~$15/ay | Doğal dil işleme + görüntü analizi (2026) |
| 6 | OpenAI Realtime API | **GPT-5.6-Realtime** (WebRTC) | — | ~$0.08/dk | Sıfır gecikme sesli konuşma (2026) |
| 7 | Anthropic API | **Claude 5 Opus** + **Claude 5 Mythos** + **Claude 5 Fable** | — | ~$12/ay | Felsefe, yaratıcı rol yapma, dil eğitimi (2026) |
| 8 | Google AI API | **Gemini 3.6 Pro** (2M+ token bağlam) | — | ~$8/ay | Biyometrik analiz, devasa bağlam (2026) |
| 9 | ElevenLabs TTS | Voice Design 2026 API | — | ~$5/ay | Karizmatik ses ("Adam" voice, duygusal tonlama) |
| 10 | Whisper STT | OpenAI Whisper 2026 | — | ~$0.004/dk | Ses → metin |
| 11 | LangGraph 2026 | Agentic Framework | — | $0 | Açık kaynak agent graph (pip install langgraph) |
| 9 | Python Sunucu | Raspberry Pi 4 (4GB) | 1 | ~$55 | jarvis_core Python + ChromaDB çalıştırır |
| 10 | Kondansatör | 100nF | 1 | ~$0.1 | INMP441 VDD filtresi |

---

## 🔘 Modül 2: hidden_triggers (Gizli Tetikleyiciler)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Zigbee Mini Buton | Sonoff ZBMINI / Tuya | 2 | ~$10/adet | Yatak başı + masa altı |
| 2 | Kapasitif Sensör | TTP223 | 1 | ~$2 | Ahşap masa altına yapıştır |
| 3 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | TTP223'ü okur |
| 4 | Bakır Folyo | 5cm × 5cm | 1 | ~$1 | Kalın ahşap için alan genişletme |
| 5 | NFC Etiket | NTAG215 | 1 | ~$0.30 | Bardak altlığı altına |
| 6 | Çift Taraflı Bant | 3M VHB | 1 rulo | ~$5 | Gizleme için |
| 7 | CR2032 Pil | Buton pili | 2 | ~$1/adet | Zigbee butonlar için |

---

## 🌌 Modül 3: space_projection (Derin Uzay Projeksiyonu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Galaksi Projeksiyon | Tuya Galaxy Projector | 1 | ~$30 | Nebula + lazer (lazer kapatılacak) |
| 2 | Broadlink RM4 Mini (alternatif) | IR blaster | 1 | ~$20 | Tuya yerine IR kumandalı cihazlar için |

---

## 🪞 Modül 4: magic_mirror (Akıllı Ayna)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Two-way Mirror Akrilik | Şeffaf ayna filmli akrilik | 1 | ~$40 | Ayna boyutu |
| 2 | LCD Panel | Çerçevesiz monitör (stripped) | 1 | ~$100 | Akrilik ile aynı boyut |
| 3 | Mikro Bilgisayar | Raspberry Pi Zero 2 W | 1 | ~$15 | MagicMirror² çalıştırır |
| 4 | Akıllı Priz | Shelly Plug s | 1 | ~$15 | LCD gücünü keser/açar |
| 5 | Siyah Bant | Işık sızdırmazlık bandı | 1 rulo | ~$5 | Kenar ışık sızıntısı |
| 6 | MicroSD | 16GB Class 10 | 1 | ~$5 | Raspberry Pi OS Lite |
| 7 | HDMI Adaptör | Mini HDMI → HDMI | 1 | ~$3 | Pi Zero → LCD |
| 8 | Güç Adaptörü | 5V 2.5A USB-C | 1 | ~$5 | Raspberry Pi |
| 9 | PIR Sensör (opsiyonel) | HC-SR501 mini | 1 | ~$2 | Ayna yakınında hareket algılama |

---

## 🔊 Modül 5: spatial_audio (Konumsal Ses)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Hoparlör | Echo Dot 5. Gen (veya Nest Mini) | 2 | ~$50/çift | Stereo pair, çapraz köşelerde |
| 2 | Spotify Premium | Spotify abonelik | — | ~$10/ay | Çalma listeleri için |

> Not: Hoparlörler Modül 1 (jarvis_core) ile paylaşımlıdır.

---

## 🛏️ Modül 6: underbed_lighting (Yatak Altı Aydınlatma)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | LD2410 + COB LED sürücü |
| 2 | Radar Sensör | HLK-LD2410B | 1 | ~$5 | 24GHz mmWave, mesafe algılama |
| 3 | COB LED Şerit | 12V sıcak beyaz (2700K) | 2-3m | ~$10/m | Pürüzsüz ışık (Floating Bed) |
| 4 | MOSFET Modülü | IRLZ44N | 1 | ~$2 | ESP32 PWM → COB LED sürme |
| 5 | Güç Kaynağı | 12V 2A | 1 | ~$8 | COB LED için |
| 6 | Silikon Difüzör Tüp | LED şerit boyu | 1 | ~$2/m | LED çiplerini gizle |
| 7 | Jumper Wire | Dişi-Dişi | 4 | ~$2 | LD2410 → ESP32 |

---

## 🌅 Modül 7: morning_after (Ertesi Sabah)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Perde Motoru | SwitchBot Curtain | 1 | ~$90 | Kornişe takılır, sessiz |
| 2 | Tuya Perde Motoru (alternatif) | Rod motor | 1 | ~$35 | Daha ucuz alternatif |

> Not: WLED sistemi (Modül 10) ve barista_mode (Modül 11) ile entegre çalışır.

---

## 📡 Modül 8: invisible_remote (Görünmez Kumanda)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | IR Blaster | Broadlink RM4 Mini | 1 | ~$20 | 360° IR, TV + klima kontrolü |
| 2 | Akıllı Priz (Klima) | Shelly Plug s | 1 | ~$15 | Klima güç izleme (geri besleme) |
| 3 | ESP32 (alternatif) | DevKit V1 | 1 | ~$5 | Broadlink yerine IR LED ile |
| 4 | IR LED | 940nm, 5mm, yüksek güç | 1 | ~$1 | ESP32 alternatifi için |
| 5 | IR Alıcı (öğrenme) | VS1838B | 1 | ~$1 | IR kod öğrenme (opsiyonel) |
| 6 | 220Ω Direnç | — | 1 | ~$0.1 | IR LED koruması |

---

## 🌿 Modül 9: smart_diffuser (Akıllı Difüzör)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Difüzör | Tuya/SmartLife uyumlu | 1 | ~$25 | WiFi, LocalTuya ile kontrol |
| 2 | Esans Yağı — Sandalağacı | Monin / Plant Therapy | 1 | ~$15 | Topraklayıcı, sakinleştirici |
| 3 | Esans Yağı — Amber | Monin / Nemat | 1 | ~$15 | Lüks, güven hissi |
| 4 | Esans Yağı — Ylang-Ylang | Plant Therapy / Monin | 1 | ~$15 | Afrodizyak, duygusal açılım |
| 5 | Cam Şişe (karışım) | 10ml pipetli | 3-4 | ~$2/adet | Mod bazlı karışımlar için |

> Alternatif: "Dumb" difüzör + akıllı priz (Shelly Plug s ~$15)

---

## 💡 Modül 10: audio_reactive_wled (Sese Duyarlı WLED)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | FFT + I2S (ESP8266 yetersiz) |
| 2 | Dijital Mikrofon | INMP441 I2S | 1 | ~$5 | 24-bit, düşük gürültü |
| 3 | LED Şerit | WS2812B (60 LED/m) | 2-5m | ~$5/m | Oda boyutuna göre |
| 4 | Güç Kaynağı | 5V 4A | 1 | ~$10 | LED şerit için harici güç |
| 5 | Difüzör Profil | Alüminyum + mat akrilik | LED boyu | ~$8/m | Premium görünüm için şart |
| 6 | Kondansatör | 100nF | 1 | ~$0.1 | INMP441 VDD filtresi |
| 7 | Direnç | 330Ω | 1 | ~$0.1 | WS2812B veri hattı koruması |
| 8 | Jumper Wire | Dişi-Dişi | 6 | ~$2 | INMP441 → ESP32 |

---

## ☕ Modül 11: barista_mode (Kahve Otomasyonu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Priz (Güç Ölçümlü) | Shelly Plug s | 1 | ~$15 | Kahve makinesi güç izleme |
| 2 | NFC Etiket | NTAG215 | 1 | ~$0.30 | Masanın altına gizli |
| 3 | Fingerbot (opsiyonel) | SwitchBot Fingerbot | 1 | ~$15 | Dijital anahtarlı makineler için |
| 4 | Çift Cidarlı Fincan | Porselen (IKEA FÄRGRIK / Villeroy & Boch) | 2-4 | ~$5-20/adet | Premium sunum |
| 5 | Vanilya Şurubu | Monin Vanilla | 1 | ~$10 | Tatlı, kremamsı |
| 6 | Karamel Şurubu | Monin Caramel | 1 | ~$10 | Zengin tat |
| 7 | Tarçın | Toz tarçın | 1 | ~$3 | Fincan üstüne serpme |
| 8 | Kahve (Kapsül) | Nespresso Original (Arpeggio, Ristretto) | 1 kutu | ~$15 | Hızlı, tutarlı |
| 9 | Kahve (Çekirdek) | Illy Classico | 1 paket | ~$15 | Premium (öğütücü gerekir) |
| 10 | Sunum Tepsisi | Bambu / Ceviz ahşap | 1 | ~$15 | Premium sunum |

---

## ❤️‍🔥 Modül 12: intimacy_sync_mode (Duyusal Senkron)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | MPU6050 + ritim algılama |
| 2 | İvmeölçer / Jiroskop | MPU6050 (6-DoF) | 1 | ~$3 | Yatak iskeletine gizli |
| 3 | Jumper Wire | Dişi-Dişi | 4 | ~$2 | MPU6050 → ESP32 (I2C) |
| 4 | Köpük Şerit | 1-2mm | 1 | ~$2 | Sensör izolasyonu (yüksek frekans filtre) |
| 5 | Çift Taraflı Bant | 3M VHB | 1 | ~$3 | Sensör montajı |

> Not: WLED (Modül 10), Spatial Audio (Modül 5), Invisible Remote (Modül 8) ve Smart Diffuser (Modül 9) ile entegre çalışır.

---

## 🧑‍🍳 Modül 13: vision_chef_assistant (Mutfak Şefi)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | IP Kamera | TP-Link Tapo C200 | 1 | ~$25 | RTSP, 720p, mutfak dolabı altı |
| 2 | USB Güç Adaptörü | 5V 1A | 1 | ~$3 | Kamera beslemesi |
| 3 | Çift Taraflı Bant | 3M VHB | 1 | ~$3 | Dolap altı montaj |
| 4 | Akıllı Priz (Ocak) | Shelly Plug s | 1 | ~$15 | Ocak güç izleme (güvenlik) |
| 5 | Zigbee Buton (Mutfak) | Sonoff ZBMINI / Tuya | 1 | ~$10 | Mutfak tezgahı yanında |

> Not: OpenAI GPT-4o-mini Vision API (Modül 1 ile paylaşımlı).

---

## 📚 Modül 15: immersive_language_tutor (Dil Eğitmeni)

> **Ekstra donanım GEREKMEZ!** Bu modül tamamen yazılım tabanlıdır.
> Mevcut Jarvis Core (Modül 1), WLED (Modül 10), Spatial Audio (Modül 5),
> Magic Mirror (Modül 4) ve klima (Modül 8) altyapısını kullanır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | NFC Etiket (Study Book) | NTAG215 | 1 | ~$0.30 | Masadaki NFC okuyucuya "Study Book" etiketi |
| 2 | Odaklanma Esansı (opsiyonel) | Biberiye / Limon esansı | 1 | ~$10 | Difüzör için odaklanma kokusu (veya difüzörü kapat) |
| 3 | vocabulary.json | Kelime listesi (100+ çift) | 1 | $0 | Magic Mirror için JSON dosya (elle hazırlanır) |

> **Toplam ekstra maliyet: ~$0-10** (NFC etiket + opsiyonel esans)

---

## 🧬 Modül 16: holistic_life_os (Yaşam İşletim Sistemi)

> **Ekstra donanım GEREKMEZ!** Bu modül tamamen yazılım tabanlıdır.
> Mevcut akıllı saat (Apple Watch/Wear OS), yatak radarı (LD2410, Modül 6 — varlık/hareket),
> kamera (Modül 13) ve HA altyapısını kullanır.
>
> ⚠️ **ÖNEMLİ:** LD2410/LD2450 radar kalp atışı ve nefes ÖLÇMEZ.
> Kalp atışı, nefes ve uyku evreleri akıllı saatten (Apple Health/Google Fit) gelir.
> Radar sadece varlık/hareket için kullanılır.
> Eğer radar tabanlı kalp atışı ölçümü istenirse: HLK-LD2420/LD6001 (Sleep Radar, ~$15-25) gerekir.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Saat | Apple Watch SE / Wear OS | 1 | ~$200 | Kullanıcının mevcut saati — kalp atışı, nefes, uyku evreleri (ANA KAYNAK) |
| 2 | (Yazılım) | CalDAV / Google Calendar API | — | $0 | Takvim entegrasyonu |
| 3 | (Yazılım) | PyPDF2 (PDF analiz) | — | $0 | pip install pypdf2 |
| 4 | (Yazılım) | Google Fit API / Apple Health | — | $0 | Sağlık verisi erişimi (nabız, uyku, adım) |
| 5 | (Opsiyonel) | Google OAuth token | — | $0 | Takvim esnetme (Calendar API) |
| 6 | (Opsiyonel) | HLK-LD6002 (60GHz Vital Signs Radar) | 1 | ~$25-40 | Temassız kalp atışı (BPM) + solunum ölçer. Yatak başucuna monte. ⚠️ LD2420 ve LD6001 kalp/nefes ÖLÇMEZ — sadece varlık/konum. LD6002 bu iş için özel üretilmiştir |

> **Toplam ekstra maliyet: ~$0** (mevcut akıllı saat + yazılım)
> (Opsiyonel sleep radar eklersen: +$15-25)

---

## 🎬 Modül 17: hyperion_media_sync (Ekran Senkronizasyonu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Hyperion Sunucu | Raspberry Pi 4 (2GB) | 1 | ~$45 | Hyperion.ng çalıştırır (Modül 1 Pi 4'ten ayrı veya aynı) |
| 2 | HDMI Grabber | UCV007 / MS2109 USB | 1 | ~$10 | HDMI → USB, düşük gecikme (<50ms) |
| 3 | HDMI Splitter | 1x2 HDMI splitter | 1 | ~$10 | Kaynak → TV + grabber |
| 4 | HDMI Kablo | 1.5m | 2 | ~$3/adet | Kaynak → splitter → TV/grabber |

> **Not:** WLED sistemi (Modül 10) zaten kurulu. Bu modül Hyperion yazılımı + HDMI grabber ekler.
> **Toplam ekstra maliyet: ~$71** (Pi 4 + grabber + splitter + kablolar)

---

## 📱 Modül 18: life_os_superapp (PWA SuperApp)

> **Ekstra donanım GEREKMEZ!** Mevcut HA PWA + HACS custom cards + ESP32-S3 (Modül 1) kullanır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | Mushroom Cards (HACS) | — | $0 | Modern yuvarlak kartlar |
| 2 | (Yazılım) | Bubble Card (HACS) | — | $0 | Swipeable sekmeler, pop-up |
| 3 | (Yazılım) | HA Companion App | — | $0 | PWA + çağrı sensörü (phone_state) |
| 4 | (Donanım) | ESP32-S3 Bluetooth Proxy | — | $0 | Modül 1 ile paylaşımlı |

> **Toplam ekstra maliyet: ~$0** — tüm altyapı mevcut, sadece yazılım.

---

## 📞 Modül 19: call_routing_and_ceo_mode (CEO Çağrı Modu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | I2S DAC | MAX98357A | 1 | ~$3 | Hoparlör sürücü (çağrı sesi → oda) |
| 2 | (Donanım) | ESP32-S3 (Modül 1 ile paylaşımlı) | — | $0 | BT Proxy + HFP + I2S |
| 3 | (Donanım) | INMP441 (Modül 1 ile paylaşımlı) | — | $0 | Mikrofon (senin sesin) |
| 4 | (Yazılım) | HA Companion App | — | $0 | phone_call_state sensörü |

> **Toplam ekstra maliyet: ~$3** (I2S DAC — diğer her şey Modül 1 ile paylaşımlı)

---

## 🪞 Modül 20: magic_mirror_comm_and_grooming (Ayna İletişim + Stil Koçu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | USB Web Kamera | Logitech C270 (720p mini) | 1 | ~$25 | Ayna çerçevesine gizli |
| 2 | USB Mikrofon | Mini USB mic | 1 | ~$10 | Ayna arkasında gizli |
| 3 | Hoparlör | Mini 3W speaker | 1 | ~$5 | Ayna arkasında (TTS + arama) |
| 4 | USB Hub | Mini 4-port USB hub | 1 | ~$5 | Pi Zero'nun tek portuna hub |
| 5 | (Donanım) | Pi Zero 2 W (Modül 4 ile paylaşımlı) | — | $0 | MagicMirror² çalıştırır |
| 6 | (Yazılım) | aiortc (WebRTC) | — | $0 | pip install aiortc |

> **Toplam ekstra maliyet: ~$45** (kamera + mikrofon + hoparlör + hub)

---

## 🚗 Modül 21: car_knight_rider_core (Araç Beyni + Giant's Throne)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Android Multimedya | 9-10" Head Unit (2GB RAM, Android 10+) | 1 | ~$150-250 | 2005+ araçlar, universal fit |
| 2 | OBD2 Adaptör | ELM327 Bluetooth/Wi-Fi | 1 | ~$15-25 | Direksiyon altı OBD2 portu |
| 3 | (Opsiyonel) | ESP32 + CAN Bus shield | 1 | ~$20 | Gelişmiş OBD2 (CAN Bus direkt) |
| 4 | (Yazılım) | Torque Pro / Car Scanner | 1 | ~$5 | OBD2 okuma app'i |
| 5 | (Yazılım) | Tailscale (Android) | — | $0 | VPN tüneli → VPS |

> **Toplam ekstra maliyet: ~$170-275** (Android ekran + OBD2 adaptör)

---

## 🔮 Modül 22: car_omniscience_copilot (Gözetmen + OBD2 Kehanet)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | IR Kamera | FLIR One / Seek Thermal (USB-C) | 1 | ~$200 | Sürücü yüzü → PERCLOS (gece görüş) |
| 2 | OBD2 Wi-Fi | ELM327 Wi-Fi (Bluetooth yerine) | 1 | ~$20 | Daha hızlı veri akışı (10 Hz) |
| 3 | Akıllı Saat | Apple Watch / Wear OS (mevcut) | — | $0 | Nabız, HRV, stres (Modül 16 ile paylaşımlı) |
| 4 | GPS | Android dahili GPS | — | $0 | Hız, konum |
| 5 | İvmeölçer | Android dahili / MPU6050 | — | $0 | G-kuvveti, ivme |

> **Toplam ekstra maliyet: ~$220** (IR kamera + OBD2 Wi-Fi adaptörü)

---

## 🌑 Modül 23: car_stealth_and_seduction (Blackout + Seduction + Sci-Fi)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | HA Companion App (Android) | — | $0 | Direksiyon tuşu → HA |
| 2 | (Opsiyonel) | Zigbee mini buton (araç içi gizli) | 1 | ~$10 | Direksiyon altına gizli |
| 3 | (Opsiyonel) | Araç içi WLED şerit (ayak/kapı) | 1m | ~$5 | ESP32 + WS2812B |
| 4 | (Opsiyonel) | Araç içi USB difüzör | 1 | ~$20 | Imza koku için |

> **Toplam ekstra maliyet: ~$0-35** (mevcut altyapı + opsiyonel WLED/difüzör)

---

## 🚀 Modül 24: car_edge_ai_vision (Jetson Nano Edge-AI + ADAS)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Edge-AI Bilgisayar | Nvidia Jetson Nano 4GB Dev Kit | 1 | ~$150 | 128 CUDA core, GPU |
| 2 | Kamera | Sony IMX219 CSI-2 (8MP) | 1 | ~$25 | Ön cam → dikiz aynası arkası |
| 3 | MicroSD | 64GB UHS-I U3 (A2) | 1 | ~$15 | JetPack imajı için |
| 4 | Güç | 5V 4A USB-C adaptör | 1 | ~$10 | Jetson Nano beslemesi |
| 5 | (Opsiyonel) | 5/7" IPS dokunmatik LCD | 1 | ~$35-50 | HMI ekranı |
| 6 | (Opsiyonel) | USB Wi-Fi dongle | 1 | ~$10 | Tailscale için |

> **Toplam ekstra maliyet: ~$200-250** (Jetson + kamera + SD + güç + opsiyonel LCD)

---

## 🛡️ Modül 25: car_sentry_mode_security (Sentry Mode + Güvenlik)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | PIR Sensör | HC-SR501 mini (12V uyumlu) | 1 | ~$2 | Araç içi, düşük güç (~0.05W) |
| 2 | Şok Sensör | MPU6050 (Modül 12 ile paylaşımlı) | — | $0 | Darbe/sarsıntı algılama |
| 3 | Akıllı Röle | 12V→5V DC-DC + voltaj sensörü | 1 | ~$10 | Akü koruma (<11.5V → kapat) |
| 4 | (Opsiyonel) | Arka kamera (USB webcam) | 1 | ~$15 | Ön + arka kayıt |
| 5 | (Yazılım) | Telegram Bot API | — | $0 | BotFather → token → anlık bildirim |
| 6 | (Donanım) | Jetson Nano (Modül 24 ile paylaşımlı) | — | $0 | Deep Sleep + kamera uyandırma |

> **Toplam ekstra maliyet: ~$12-27** (PIR + röle + opsiyonel arka kamera)

---

##  Toplam Maliyet Özeti

| Kategori | Adet | Toplam Fiyat (≈) |
|---|---|---|
| **Genel Altyapı** (VPS, yönlendirici, Zigbee dongle) | — | ~$120 + $10/ay |
| **Mikrodenetleyiciler** (ESP32 × 5, Pi Zero, Pi 4) | 7 | ~$95 |
| **Sensörler** (LD2410, MPU6050, TTP223, INMP441 × 2) | 6 | ~$25 |
| **Hoparlörler** (Echo Dot × 2) | 2 | ~$50 |
| **Kameralar** (Tapo C200 × 2) | 2 | ~$50 |
| **Akıllı Prizler** (Shelly × 4) | 4 | ~$60 |
| **LED & Aydınlatma** (WLED, COB, projeksiyon) | — | ~$80 |
| **Perde & Difüzör & Broadlink** | 3 | ~$135 |
| **Magic Mirror** (akrilik + LCD + Pi Zero) | — | ~$180 |
| **Esans Yağları** | 3 | ~$45 |
| **Kahve & Sunum** | — | ~$60 |
| **Kablo & Direnç & Kondansatör** | — | ~$20 |
| **API Abonelikleri** (OpenAI, ElevenLabs, Spotify) | — | ~$25/ay |
| **TOPLAM (Tek Seferlik)** | — | **~$920** |
| **TOPLAM (Aylık)** | — | **~$35/ay** |

> **Not:** Fiyatlar yaklaşık değerlerdir. Bazı bileşenler modüller arasında paylaşımlıdır (hoparlörler, API'ler, akıllı prizler). Gerçek maliyet, mevcut donanıma ve seçilen markalara göre değişir.

---

## 🛒 Satın Alma Öncelik Sırası

### Faz 1 (Temel — Jarvis Core + Gizli Tetikleyiciler)
1. ESP32-S3 + INMP441 (ses hub)
2. Echo Dot × 2 (stereo pair)
3. Raspberry Pi 4 (jarvis_core Python)
4. Sonoff ZBMINI × 2 (gizli butonlar)
5. TTP223 + ESP32 (kapasitif dokunma)
6. OpenAI + ElevenLabs API abonelikleri

### Faz 2 (Atmosfer — Işık + Ses + Koku)
7. ESP32 + INMP441 + WS2812B (audio reactive WLED)
8. Alüminyum difüzör profil (premium görünüm)
9. Tuya difüzör + esans yağları
10. Tuya galaksi projeksiyon

### Faz 3 (Konfor — Kahve + Perde + Sabah)
11. Shelly Plug s × 4 (güç ölçümlü prizler)
12. SwitchBot Curtain (akıllı perde)
13. NFC NTAG215 × 2 (kahve + bardak altlığı)
14. Çift cidarlı fincanlar + Monin şurupları

### Faz 4 (Gelişmiş — Radar + Şef + Ayna)
15. HLK-LD2410B + COB LED (yatak altı)
16. MPU6050 (intimacy ritim)
17. TP-Link Tapo C200 × 2 (yüz tanıma + mutfak)
18. Broadlink RM4 Mini (IR kumanda)
19. Two-way mirror akrilik + LCD + Pi Zero (akıllı ayna)
20. **Kablo gizleme malzemeleri** (aşağıdaki tabloya bakın)

---

## 🎨 Kablo Gizleme ve Estetik Montaj Malzemeleri

> **"Tony Stark / Premium Lounge" teması için KRİTİK.**
> WLED şeridinin, kameranın veya radarın kablosu duvardan siyah/kırmızı şekilde sarkarsa, misafirin gözünde lüks algısı anında "öğrenci işi kablo karmaşasına" döner. Tüm kablolar görünmez olmalıdır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Kablo Gizleyici Kılıf | Cırtlı kablo sleeve (duvar renginde/beyaz) | 5m | ~$8 | Birden fazla kabloyu tek tüp içinde toplar, duvar rengine uyumlu |
| 2 | İnce Kablo Kanalı | PVC kablo kanalı (beyaz/duvar rengi, 15×10mm) | 5m | ~$5 | Duvar kenarında, baseboard boyunca gizli kablo geçişi |
| 3 | Çift Taraflı Bant | 3M VHB (siyah/beyaz) | 2 rulo | ~$10/adet | ESP32 ve sensörleri mobilya altına sıfır görünür şekilde bantlama |
| 4 | Kablo Bağı | Siyah kelebek kablo bağı | 100 adet | ~$5 | Kablo demetlerini sabitleme |
| 5 | Duvar Rengi Boya | Kablo kanalı ile aynı renk (küçük kutu) | 1 | ~$5 | Kablo kanalını duvar rengine boyama (tam gizleme) |
| 6 | Möbius / Felt Kılıf | Keçe kablo gizleyici (mobilya altı için) | 2m | ~$7 | Yatak/masa altında kabloları keçe içinde gizleme |
| 7 | USB Kablo (Düz) | Düz başlı USB-C/Micro-USB kablo (kısa, 30-50cm) | 5 | ~$3/adet | ESP32'leri güçlendirmek için kısa, gizli kablolar |
| 8 | Baseboard Kablo Kanalı | Zemin süpürgeliği arkası kablo kanalı | 5m | ~$8 | Oda çevresi kablo geçişi (tam gizli) |

### Kablo Gizleme Kuralları

| Kural | Açıklama |
|---|---|
| **Sadece uçlar görünür** | Sensörlerin ve LED'lerin sadece fonksiyonel uçları görünmeli, kablolar asla |
| **Duvar rengine uyum** | Kablo kanalları ve sleeve'ler duvar rengine boyanmalı veya aynı renkte seçilmeli |
| **Mobilya altı bantlama** | Tüm ESP32'ler ve kablolar yatak/masa/komodin altına 3M VHB ile bantlanmalı |
| **Baseboard kullanımı** | Oda çevresi kablolar baseboard (zemin süpürgeliği) arkasından geçmeli |
| **Kısa kablo prensibi** | Mümkün olan en kısa kablo kullanılmalı (sarkma olmasın) |
| **Kablo sleeve ile toplama** | Birden fazla kablo tek sleeve içinde toplanmalı (dağınıklık yok) |
| **Güç kabloları ayrı** | 220V güç kabloları veri kablolarından ayrı kanalda (EMI önleme) |

---

*Bu dosya, projenin tüm donanım ihtiyaçlarını listeler. Yeni modüller eklendikçe güncellenir.*