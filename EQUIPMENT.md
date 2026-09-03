# 📋 EQUIPMENT.md — Akıllı Yurt Odası Teçhizat Listesi

> Bu dosya, projenin tüm modülleri için gereken donanım, sensör, kablo ve materyallerin eksiksiz listesidir. Modüllere göre sıralanmıştır.

---

## ⚡ Mimaride Devrim: Beyin Bulutta (Raspberry Pi YOK)

> **"Yerel sunucu tutmayız. Beyni bulutta (VPS), dağıtıcılığı GL-MT3000 modemde."**

| Katman | Cihaz | Görev |
|---|---|---|
| **Beyin (Bulut)** | VPS (Docker) | Home Assistant + jarvis_core 3.0 (Python) + ChromaDB (yüz hafızası) + Mealie + OpenClaw |
| **Dağıtıcı (Yerel)** | GL-MT3000 (Beryl AX) | WiFi 6 AP + Tailscale client + Yerel MQTT broker + cihaz izolasyonu (iptables) |
| **Uç Cihazlar (Yerel)** | ESP32'ler, Tuya cihazlar, Yeelight, Echo Dot | Sensör, ses, ışık, röle — hepsi MQTT/WiFi ile GL-MT3000 üzerinden VPS'e bağlanır |

**Sonuç:** Yurt odasında sıfır sunucu donanımı. Hiçbir fan sesi, hiçbir ekstra elektrik, hiçbir fiziksel erişim ihtiyacı. SSH ile her şey uzaktan yönetilir.

---

## 🗑️ Çöpe Ayrılan Bileşenler (Mimari Değişiklik)

| Bileşen | Eski Görev | Neden Çöp? |
|---|---|---|
| **Raspberry Pi 4** | jarvis_core Python + ChromaDB (Faz 1) + CocktailBerry (Faz 16) | Beyin VPS'e taşındı. Yerel sunucu = fan sesi + elektrik + fiziksel erişim + Kıb-Tek kesintisinde çökme. VPS 7/24 çalışır |
| **Raspberry Pi Zero 2 W** | MagicMirror² (Modül 4) | MagicMirror² artık VPS Docker'da web servisi olarak çalışır → TV üzerinde Mi Box S (3rd Gen) tarayıcısında tam ekran gösterilir. Yerel donanım gerekmez |
| **Sonoff ZBMINI × 2** | Gizli Zigbee butonlar (Modül 2) | Yurt odasının priz/anahtar tesisatı sökülmeyecek. Gizli tetikleyiciler TTP223 dokunmatik sensörlerle (×5, ELDE) masa altına yapıştırılır |
| **Zigbee2MQTT Dongle (CC2652R)** | Zigbee koordinatör | Zigbee cihaz kalmadı (ZBMINI çöp). Tüm yerel cihazlar WiFi (Tuya LocalTuya / Yeelight LAN / ESPHome MQTT) |
| **Broadlink RM4 Mini** | IR kumanda (Modül 8) | Yerine Tuya WiFi Smart IR+RF Akıllı Kumanda alındı (ELDE) — klima + vantilatör bağlı. HA'da `tuya-local` entegrasyonu ile tam yerel kontrol |
| **SwitchBot Curtain** | Perde motoru (Modül 7) | Yerine 28BYJ-48 Step Motor + ULN2003 Sürücü Kiti (ELDE) — 3000₺ hazır cihaz yerine ~150₺ DIY robotik parça. ESP32 + ESPHome stepper ile sürülür |
| **Xiaomi Mi Smart Multi Cooker 3L** | Akıllı tencere (Modül 28) | Yerine Hisense HMC6SBK 6L Multicooker (ELDE) alındı — 2× kapasite, 1500W. WiFi YOK → Tuya akıllı prizle güç izleme + Vision-Cooker orkestrasyonu |

---

## ⏸️ Beklemede: Robotik Projeler (Modül 29, 30, 31)

> **"Önce odanın temeli (ses, ışık, otomasyon). Robotiğe 1 kuruş yok."**

| Modül | Proje | Durum | Tahmini Maliyet (ileride) |
|---|---|---|---|
| Modül 29 | Embodied Jarvis Avatar (5-DOF robotik lamba) | ⏸️ BEKLEMEDE | ~$105 |
| Modül 30 | Desktop Pet Kame32 (dört bacaklı robot) | ⏸️ BEKLEMEDE | ~$45 |
| Modül 31 | Siber Barmen (CocktailBerry) | ⏸️ BEKLEMEDE | ~$265 |

> Bu modüllerin dokümantasyonu ve kod tabanı korunur — oda temeli bitince aynı planlarla devam edilir. Ancak satın alma listesinden çıkarılırlar.

---

## 📦 Mevcut Envanter (Alındı — Kurulum Bekliyor)

> Bu parçalar satın alındı ancak henüz hiçbir kurulum yapılmadı. Faz 1-4 kurulumlarının ham maddesi.

| # | Parça | Adet | Kullanılacağı Yer | Durum |
|---|---|---|---|---|
| 1 | ESP32-S3 N8R2 WiFi+BT Board | 2 | #1: Ses Hub (INMP441 stereo) — #2: WLED Audio Hub (INMP441 + WS2812B) | ✅ Elde |
| 2 | INMP441 MEMS I2S Mikrofon | 2 | 1× Ses Hub (Jarvis mikrofonu) + 1× WLED Audio (ritim analizi) | ✅ Elde |
| 3 | TTP223B Dijital Dokunmatik Sensör | 5 | Modül 2 — masa altı gizli tetikleyiciler (ahşap üzerinden algılar) | ✅ Elde |
| 4 | NFC Etiket NTAG213 (25mm) | 8 | Kahve + bardak altlığı + Study Book + misafir etiketleri | ✅ Elde |
| 5 | MPU6050 6-Eksen Gyro/İvmeölçer | 1 | Modül 12 — yatak ritim algılama (intimacy sync) | ✅ Elde |
| 6 | HLK-LD2410B+BLE 24GHz Radar | 1 | Modül 6 — yatak altı varlık/mesafe algılama | ✅ Elde |
| 7 | TSOP1838 38KHz IR Alıcı (Metal) | 1 | Modül 8 — IR kod öğrenme (kumanda kodlarını ESP32'ye öğret) | ✅ Elde |
| 8 | LTE-4206 3mm 940nm IR LED | 2 | Modül 8 — ESP32 IR blaster (TV/eski cihazlar için yedek) | ✅ Elde |
| 9 | 2N2222 Transistör (NPN TO-92) | 2 | IR LED sürücü katı (ESP32 GPIO → transistör → IR LED) | ✅ Elde |
| 10 | 220R 4+1 Sıra Direnç | 1 | IR LED akım sınırlama | ✅ Elde |
| 11 | 100nF 63V Polyester Kondansatör | 10 | INMP441 VDD filtresi + WS2812B güç filtresi | ✅ Elde |
| 12 | MCU2812B WS2812B RGB LED (tek modül) | 1 | WS2812B prototip testi (300'lük şerit alınmadan önce doğrulama) | ✅ Elde |
| 13 | Breadboard Mini (Yapışkanlı) | 1 | Prototip kurulum (kalıcı montaj öncesi test) | ✅ Elde |
| 14 | Dişi-Dişi Jumper (40'lı, 20cm) | 1 | Sensör → ESP32 bağlantıları | ✅ Elde |
| 15 | Erkek-Erkek Jumper (40'lı, 20cm) | 1 | Breadboard prototip | ✅ Elde |
| 16 | Erkek-Dişi Jumper (40 pin, 20cm) | 1 | Breadboard → ESP32 | ✅ Elde |

---

## 🛒 Yeni Alınan Ekipmanlar (Eylül 2026)

| # | Ekipman | Fiyat (≈) | Durum | Not |
|---|---|---|---|---|
| 1 | **Yeelight Smart LED Color Bulb 1S** (WiFi) | ~$15 | ✅ Alındı | Oda ambiyans aydınlatması. HA yerel Yeelight entegrasyonu (LAN Control aç) — bulut YOK, Zero-Trust uyumlu |
| 2 | **Tuya WiFi Smart IR+RF Akıllı Kumanda** | ~$18 | ✅ Alındı | Klima + vantilatör Tuya Smart ile bağlı ✅. TV bağlanamadı (TV'nin IR alıcısı arızalı — TV değişecek). HA'da `tuya-local` entegrasyonu: remote entity + learn_command + send_command, tam yerel |
| 3 | **Hisense HMC6SBK Multi Cooker 6L** | ~$80 | ✅ Alındı | 1500W, 10-13 program, paslanmaz çelik iç kap. WiFi YOK → Tuya akıllı prizle güç izleme (1500W ısınma / ~40W keep-warm tespiti) + Vision-Cooker orkestrasyonu |
| 4 | **HAUSBERG HB3723 Espresso Kahve Makinesi** | ~$70 | ✅ Alındı | WiFi yok → Tuya akıllı prizle güç izleme (ısıtma ~900W / hazır bekleme ~50W tespiti → "kahve hazır" bildirimi) |
| 5 | **28BYJ-48 Step Motor + ULN2003 Sürücü Kiti** | ~$4 | ✅ Alındı | DIY perde motoru (Modül 7). 3000₺ hazır SwitchBot yerine ~150₺ robotik parça. ESP32 + ESPHome `stepper` bileşeni ile sürülür |
| 6 | **Echo Dot 5. Gen × 2** | ~$100/çift | ✅ Alındı | Odanın sağ ve sol köşesi — stereo ses hub (spatial audio). Alexa integration veya Bluetooth hoparlör olarak jarvis_core'a bağlanır |

---

## 🤔 Planlanan Alımlar (Öncelik Sırasıyla)

| # | Ekipman | Fiyat (≈) | Öncelik | Not |
|---|---|---|---|---|
| 1 | **WS2812B LED Şerit (300 LED — 5m × 60/m)** | ~$20 | 🔴 YÜKSEK | Her LED adreslenebilir → şarkı ritmiyle tek tek eşleşme (audio reactive). MCU2812B test modülü ile prototip doğrulandı |
| 2 | **Tuya WiFi UK Smart Plug (güç ölçümlü) × 3-4** | ~$12/adet | 🔴 YÜKSEK | Hausberg espresso + Hisense multicooker + klima güç izleme. LocalTuya ile yerel kontrol |
| 3 | **Xiaomi Mi Box S 4K 32GB WiFi 6 (3rd Gen)** | ~$60 | 🟡 ORTA | TV'nin IR alıcısı arızalı → TV değişecek. Mi Box: Google TV 14 + Chromecast dahil + HA Android TV entegrasyonu (ADB) + MagicMirror² web gösterimi |
| 4 | ESP32 DevKit V1 × 1-2 | ~$5/adet | 🟡 ORTA | Sensör Hub (LD2410 + MPU6050 + TTP223 + 28BYJ-48 perde + IR blaster konsolidasyonu) |
| 5 | COB LED Şerit (12V sıcak beyaz) + 12V 2A adaptör + IRLZ44N MOSFET | ~$25 | 🟡 ORTA | Modül 6 — yatak altı rehber aydınlatma (LD2410 ile tetiklenir) |
| 6 | Tuya Galaksi Projeksiyon | ~$30 | 🟢 DÜŞÜK | Modül 3 — derin uzay illüzyonu (Tuya Local ile yerel) |
| 7 | Tuya Akıllı Difüzör + esans yağları | ~$25 + $45 | 🟢 DÜŞÜK | Modül 9 — koku otomasyonu |
| 8 | TP-Link Tapo C200 × 2 | ~$50/çift | 🟢 DÜŞÜK | Yüz tanıma (Modül 1) + mutfak vision (Modül 13) — RTSP yerel |
| 9 | Hisense D16CW Nem Alıcı + BME280 | ~$125 | 🟢 DÜŞÜK | Modül 32 — İklim Kalkanı (Kıbrıs rutubeti) |

---

## 🌐 Genel Altyapı

| # | Bileşen | Model / Tip | Adet | Modül | Fiyat (≈) | Not |
|---|---|---|---|---|---|---|
| 1 | VPS | DigitalOcean / Hetzner (2 vCPU, 4GB RAM) | 1 | Tümü | ~$10/ay | HA + jarvis_core + ChromaDB + Mealie + OpenClaw (hepsi Docker) |
| 2 | Yönlendirici | GL-MT3000 (Beryl AX) | 1 | Tümü | ~$80 | WiFi 6 + Tailscale client + MQTT broker + iptables izolasyon |
| 3 | Tailscale VPN | Tailscale (ücretsiz plan) | — | Tümü | $0 | VPS ↔ GL-MT3000 şifreli tünel |
| 4 | Home Assistant | HA Core (Docker, VPS) | 1 | Tümü | $0 | VPS üzerinde |
| 5 | **Akım Korumalı Priz (Surge Protector)** | APC / Brennenstuhl / Tunçmatik | 2 | Tümü | ~$25-40/adet | Kıb-Tek dalgalanmalarına karşı GL-MT3000 + Echo Dot + TV'yi korur |
| 6 | **UPS (opsiyonel)** | APC Back-UPS 600VA | 1 | Tümü | ~$50-70 | Şebeke kesintisinde GL-MT3000 + ESP32'leri 10-15 dk çalıştırır (VPS zaten kesintiden etkilenmez) |

> **Not:** Zigbee2MQTT dongle KALDIRILDI — Zigbee cihaz kalmadı. Tüm yerel cihazlar WiFi üzerinden: ESPHome (MQTT), LocalTuya, Yeelight LAN.

---

## 🧠 Modül 1: jarvis_core (Sistemin Beyni — VPS'te)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | **ESP32-S3 N8R2** (ELDE) | 1 | ~$10 | Ses hub — INMP441 mikrofon yönetimi + BT proxy |
| 2 | Dijital Mikrofon | **INMP441 I2S** (ELDE) | 1 | ~$5 | Komodin içinde gizli, 24-bit |
| 3 | IP Kamera (Yüz Tanıma) | TP-Link Tapo C200 | 1 | ~$25 | RTSP, oturma alanı (planlanan) |
| 4 | Akıllı Hoparlör | **Echo Dot 5. Gen × 2** (ELDE) | 2 | ~$100/çift | Stereo pair (spatial audio) |
| 5 | MiniMax API | **Speech 2.8 Turbo** (sesten-sese, voice cloning) | — | ~$10/ay | <300ms, voice cloning, duygu kontrol |
| 6 | DeepSeek API | **DeepSeek V4-Pro** (ağır zeka) | — | ~$1-2/ay | Günlük özet, kod, analiz |
| 7 | Qwen-VL API | **Qwen-VL Max** (görüntü analizi) | — | ~$2/ay | Kamera/vision analizi |
| 8 | (Yazılım) | jarvis_core 3.0 Python + ChromaDB | — | $0 | **VPS Docker'da** — yerel sunucu YOK |
| 9 | Kondansatör | **100nF** (ELDE) | 1 | ~$0.1 | INMP441 VDD filtresi |

> **Not:** Raspberry Pi 4 ÇÖP — jarvis_core Python + ChromaDB VPS Docker'da çalışır.

---

## 🔘 Modül 2: hidden_triggers (Gizli Tetikleyiciler)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Kapasitif Sensör | **TTP223B** (ELDE) | 5 | ~$2/adet | Ahşap masa altına yapıştır — ahşabın üstünden dokunma algılar |
| 2 | Mikrodenetleyici | ESP32 DevKit V1 (Sensör Hub ile paylaşımlı) | — | ~$5 | TTP223 ×5'i okur (tek ESP32 yeter — GPIO bol) |
| 3 | NFC Etiket | **NTAG213** (ELDE) | 8 | ~$0.30/adet | Bardak altlığı + kahve + Study Book + misafir etiketleri |
| 4 | NFC Okuyucu | PN532 / RC522 (ESP32'ye bağlı) | 1 | ~$5 | Masa üstüne gizli (planlanan) |
| 5 | Çift Taraflı Bant | 3M VHB | 1 rulo | ~$5 | Gizleme için |

> **Not:** Sonoff ZBMINI ÇÖP — yurt priz/anahtar tesisatı sökülmüyor. TTP223 ×5 (ELDE) masa altına.

---

## 🌌 Modül 3: space_projection (Derin Uzay Projeksiyonu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Galaksi Projeksiyon | Tuya Galaxy Projector | 1 | ~$30 | Nebula + lazer (lazer kapatılacak) — planlanan |
| 2 | IR Kumanda | **Tuya IR+RF** (ELDE) veya ESP32 IR blaster | — | $0 | Tuya projeksiyon LocalTuya ile, IR'li ise Tuya IR+RF ile |

---

## 🪞 Modül 4: magic_mirror (Akıllı Ayna — TV Üzerinde)

> **Mimari değişiklik:** Raspberry Pi Zero ÇÖP. MagicMirror² VPS Docker'da web servisi olarak çalışır → TV'de Mi Box S (3rd Gen) tarayıcısında tam ekran (Kiosk) gösterilir.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | MagicMirror² (Docker, VPS) | 1 | $0 | Web server modu — `http://vps-ip:8080` |
| 2 | TV Box | **Xiaomi Mi Box S 4K** (planlanan) | 1 | ~$60 | TV'de tarayıcı Kiosk → MagicMirror² tam ekran |
| 3 | Two-way Mirror Akrilik (opsiyonel) | Şeffaf ayna filmli akrilik | 1 | ~$40 | TV önüne yerleştirilirse gerçek ayna illüzyonu |
| 4 | Akıllı Priz | Tuya UK Smart Plug | 1 | ~$12 | TV/Mi Box gücünü keser/açar (varlık algılama ile) |

---

## 🔊 Modül 5: spatial_audio (Konumsal Ses)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Hoparlör | **Echo Dot 5. Gen × 2** (ELDE) | 2 | ~$100/çift | Stereo pair, çapraz köşelerde |
| 2 | Spotify Premium | Spotify abonelik | — | ~$10/ay | Çalma listeleri için |

---

## 🛏️ Modül 6: underbed_lighting (Yatak Altı Aydınlatma)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Radar Sensör | **HLK-LD2410B+BLE** (ELDE) | 1 | ~$5 | 24GHz mmWave, mesafe algılama |
| 2 | Mikrodenetleyici | ESP32 DevKit V1 (Sensör Hub ile paylaşımlı) | — | ~$5 | LD2410 okur (UART) |
| 3 | COB LED Şerit | 12V sıcak beyaz (2700K) | 2-3m | ~$10/m | Pürüzsüz ışık (Floating Bed) — planlanan |
| 4 | MOSFET Modülü | IRLZ44N | 1 | ~$2 | ESP32 PWM → COB LED sürme |
| 5 | Güç Kaynağı | 12V 2A | 1 | ~$8 | COB LED için — planlanan |
| 6 | Jumper Wire | **Dişi-Dişi** (ELDE) | 4 | $0 | LD2410 → ESP32 |

---

## 🌅 Modül 7: morning_after (Ertesi Sabah — DIY Perde Motoru)

> **Mimari değişiklik:** SwitchBot Curtain (3000₺) ÇÖP → 28BYJ-48 Step Motor + ULN2003 (ELDE, ~150₺) DIY kurgu.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Step Motor | **28BYJ-48** (ELDE) | 1 | ~$3 | Perdeyi çekecek — 1:64 redüktör, tork yeterli (hafif perde) |
| 2 | Sürücü Kartı | **ULN2003** (ELDE) | 1 | ~$1.5 | 28BYJ-48 sürücü (Darlington transistör dizisi) |
| 3 | Mikrodenetleyici | ESP32 DevKit V1 (Sensör Hub ile paylaşımlı) | — | ~$5 | ESPHome `stepper` bileşeni ile sürer |
| 4 | Dişli/Kayış Mekanizması | 3D baskı dişli veya halat+kasnak | 1 set | ~$5 | Motor → perde mekanik bağlantısı |
| 5 | Güç Kaynağı | 5V 1A (motor için) | 1 | ~$4 | 28BYJ-48 beslemesi (ULN2003 üzerinden) |
| 6 | Limit Switch (opsiyonel) | Mikro switch × 2 | 2 | ~$1/adet | Açık/kapalı uç pozisyon tespiti |

> **Not:** 28BYJ-48 yavaştır (~15 RPM) — perde tam açılış ~30-60 sn. Bu "premium" yavaşlık aslında sinematik avantaj: perde yavaş açılır → güneş kademeli girer.

---

## 📡 Modül 8: invisible_remote (Görünmez Kumanda)

> **Mimari değişiklik:** Broadlink RM4 Mini ÇÖP → Tuya WiFi Smart IR+RF (ELDE) ana kumanda + ESP32 IR blaster (ELDE parçalarla) yedek.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı IR+RF Kumanda | **Tuya WiFi Smart IR+RF** (ELDE) | 1 | ~$18 | Klima ✅ + vantilatör ✅ bağlı. TV arızalı (TV değişecek). HA `tuya-local`: remote entity, learn/send command, tam yerel |
| 2 | IR Alıcı (öğrenme) | **TSOP1838** (ELDE) | 1 | ~$1 | ESP32'ye bağlı — orijinal kumanda kodlarını öğrenir |
| 3 | IR LED (blaster) | **LTE-4206 940nm** (ELDE) | 2 | ~$0.5/adet | ESP32 IR blaster — Tuya kumandanın görmediği köşeler için |
| 4 | Transistör | **2N2222 NPN** (ELDE) | 2 | ~$0.2/adet | IR LED sürücü katı (GPIO → transistör → LED) |
| 5 | Direnç | **220R sıra direnç** (ELDE) | 1 | ~$0.2 | IR LED akım sınırlama |
| 6 | Mikrodenetleyici | ESP32 DevKit V1 (Sensör Hub ile paylaşımlı) | — | ~$5 | IR öğrenme + blaster (ESPHome `remote_transmitter` + `remote_receiver`) |
| 7 | Akıllı Priz (Klima) | Tuya UK Smart Plug (planlanan) | 1 | ~$12 | Klima güç izleme (geri besleme: komut işe yaradı mı?) |

---

## 🌿 Modül 9: smart_diffuser (Akıllı Difüzör)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Difüzör | Tuya/SmartLife uyumlu | 1 | ~$25 | WiFi, LocalTuya ile kontrol — planlanan |
| 2 | Esans Yağı — Sandalağacı | Monin / Plant Therapy | 1 | ~$15 | Topraklayıcı, sakinleştirici |
| 3 | Esans Yağı — Amber | Monin / Nemat | 1 | ~$15 | Lüks, güven hissi |
| 4 | Esans Yağı — Ylang-Ylang | Plant Therapy / Monin | 1 | ~$15 | Afrodizyak, duygusal açılım |
| 5 | Cam Şişe (karışım) | 10ml pipetli | 3-4 | ~$2/adet | Mod bazlı karışımlar için |

---

## 💡 Modül 10: audio_reactive_wled (Sese Duyarlı WLED)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Mikrodenetleyici | **ESP32-S3 N8R2** (ELDE) | 1 | ~$10 | FFT + I2S — WLED Audio Hub |
| 2 | Dijital Mikrofon | **INMP441 I2S** (ELDE) | 1 | ~$5 | 24-bit, düşük gürültü — ritim analizi |
| 3 | LED Şerit | **WS2812B 300 LED (5m × 60/m)** | 1 | ~$20 | Her LED adreslenebilir → şarkı ritmiyle tek tek eşleşme. MCU2812B test modülü ile doğrulandı — planlanan |
| 4 | Güç Kaynağı | 5V 10A (300 LED tam beyaz ~18A, pratik efektler ~8-10A) | 1 | ~$15 | LED şerit için harici güç — planlanan |
| 5 | Difüzör Profil | Alüminyum + mat akrilik | 5m | ~$8/m | Premium görünüm için şart |
| 6 | Kondansatör | **100nF** (ELDE) + 1000µF (alınacak) | 1+1 | ~$0.5 | INMP441 VDD + WS2812B güç filtresi |
| 7 | Direnç | 330Ω | 1 | ~$0.1 | WS2812B veri hattı koruması |
| 8 | Jumper Wire | **Dişi-Dişi** (ELDE) | 6 | $0 | INMP441 → ESP32-S3 |

> **Not:** 300 LED = 60 LED/m × 5m. Her LED'in kendi adresi var → WLED "Sound Reactive" modu her beat'te farklı LED segmentlerini yakar → duvar boyunca "akan enerji dalgası" efekti.

---

## ☕ Modül 11: barista_mode (Kahve Otomasyonu — HAUSBERG)

> **Mimari değişiklik:** Anonim kahve makinesi → HAUSBERG HB3723 Espresso (ELDE). WiFi yok → Tuya akıllı prizle güç izleme.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Espresso Makinesi | **HAUSBERG HB3723** (ELDE) | 1 | ~$70 | 15 bar pompa, buharla süt köpürtme. WiFi YOK |
| 2 | Akıllı Priz (Güç Ölçümlü) | Tuya UK Smart Plug (planlanan) | 1 | ~$12 | Güç izleme: ısıtma ~900W → hazır bekleme ~50W → "kahve hazır" tespiti |
| 3 | NFC Etiket | **NTAG213** (ELDE) | 1 | $0 | Masanın altına gizli — "kahve modu" tetikleyici |
| 4 | Çift Cidarlı Fincan | Porselen | 2-4 | ~$5-20/adet | Premium sunum |
| 5 | Vanilya Şurubu | Monin Vanilla | 1 | ~$10 | Tatlı, kremamsı |
| 6 | Karamel Şurubu | Monin Caramel | 1 | ~$10 | Zengin tat |
| 7 | Kahve (Çekirdek) | Espresso çekirdeği | 1 paket | ~$15 | HAUSBERG öğütücü dahilse çekirdek, değilse öğütülmüş |
| 8 | Sunum Tepsisi | Bambu / Ceviz ahşap | 1 | ~$15 | Premium sunum |

> **Güç izleme mantığı:** Tuya priz watt'ı okur → 900W (ısıtma) → 50W'a düşer (hazır) → HA otomasyonu "Kahve hazır" → Jarvis sesli bildirir + WLED amber yanar.

---

## ❤️‍🔥 Modül 12: intimacy_sync_mode (Duyusal Senkron)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | İvmeölçer / Jiroskop | **MPU6050** (ELDE) | 1 | ~$3 | Yatak iskeletine gizli — ritim algılama |
| 2 | Mikrodenetleyici | ESP32 DevKit V1 (Sensör Hub ile paylaşımlı) | — | ~$5 | MPU6050 okur (I2C) |
| 3 | Jumper Wire | **Dişi-Dişi** (ELDE) | 4 | $0 | MPU6050 → ESP32 (I2C) |
| 4 | Köpük Şerit | 1-2mm | 1 | ~$2 | Sensör izolasyonu (yüksek frekans filtre) |
| 5 | Çift Taraflı Bant | 3M VHB | 1 | ~$3 | Sensör montajı |

---

## 🧑‍🍳 Modül 13: vision_chef_assistant (Mutfak Şefi)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | IP Kamera | TP-Link Tapo C200 | 1 | ~$25 | RTSP, mutfak dolabı altı — planlanan |
| 2 | USB Güç Adaptörü | 5V 1A | 1 | ~$3 | Kamera beslemesi |
| 3 | Çift Taraflı Bant | 3M VHB | 1 | ~$3 | Dolap altı montaj |
| 4 | Akıllı Priz (Multicooker) | Tuya UK Smart Plug (planlanan) | 1 | ~$12 | Hisense HMC6SBK güç izleme (pişirme durumu tespiti) |

> **Not:** Zigbee mutfak butonu ÇÖP — TTP223 (ELDE) mutfak tezgahına yapıştırılır.

---

## 📚 Modül 15: immersive_language_tutor (Dil Eğitmeni)

> **Ekstra donanım GEREKMEZ!** Tamamen yazılım tabanlı. Mevcut Jarvis Core, WLED, Spatial Audio, TV/Mi Box (MagicMirror² web) ve klima (Tuya IR+RF) altyapısını kullanır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | NFC Etiket (Study Book) | **NTAG213** (ELDE) | 1 | $0 | "Study Book" etiketi |
| 2 | Odaklanma Esansı (opsiyonel) | Biberiye / Limon esansı | 1 | ~$10 | Difüzör için odaklanma kokusu |
| 3 | vocabulary.json | Kelime listesi (100+ çift) | 1 | $0 | TV/Mi Box MagicMirror² için JSON dosya |

---

## 🧬 Modül 16: holistic_life_os (Yaşam İşletim Sistemi)

> **Ekstra donanım GEREKMEZ!** Mevcut akıllı saat, yatak radarı (LD2410, ELDE), kamera ve HA altyapısını kullanır.
>
> ⚠️ **ÖNEMLİ:** LD2410 radar kalp atışı ve nefes ÖLÇMEZ. Kalp atışı/nefes/uyku evreleri akıllı saatten (Apple Health/Google Fit) gelir. Radar sadece varlık/hareket için.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Saat | Apple Watch SE / Wear OS | 1 | ~$200 | Kullanıcının mevcut saati — ANA KAYNAK |
| 2 | (Yazılım) | CalDAV / Google Calendar API | — | $0 | Takvim entegrasyonu |
| 3 | (Yazılım) | Google Fit API / Apple Health | — | $0 | Sağlık verisi erişimi |
| 4 | (Opsiyonel) | HLK-LD6002 (60GHz Vital Signs Radar) | 1 | ~$25-40 | Temassız kalp atışı + solunum |

---

## 🎬 Modül 17: hyperion_media_sync (Ekran Senkronizasyonu)

> **Mimari değişiklik:** Raspberry Pi 4 Hyperion sunucusu ÇÖP → Hyperion.ng VPS Docker'da çalışır. HDMI grabber hala yerel gerekir (USB cihaz) — bu modül ileri tarihe bırakılabilir veya ESP32-grabber alternatifi araştırılır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Hyperion Sunucu | Hyperion.ng (Docker, VPS) | 1 | $0 | VPS üzerinde — yerel sunucu YOK |
| 2 | HDMI Grabber | UCV007 / MS2109 USB | 1 | ~$10 | HDMI → USB — yerel bir cihaza bağlanmalı (bu modül ileri faz) |
| 3 | HDMI Splitter | 1x2 HDMI splitter | 1 | ~$10 | Kaynak → TV + grabber |

> **Not:** WLED (Modül 10) kurulu olduğu sürece Hyperion "ekran senk" ileride eklenir. Öncelik değil.

---

## 📱 Modül 18: life_os_superapp (PWA SuperApp)

> **Ekstra donanım GEREKMEZ!** Mevcut HA PWA + HACS + ESP32-S3 (ELDE) kullanır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | Mushroom Cards + Bubble Card (HACS) | — | $0 | Modern UI |
| 2 | (Yazılım) | HA Companion App | — | $0 | PWA + çağrı sensörü |
| 3 | (Donanım) | ESP32-S3 BT Proxy (ELDE) | — | $0 | Modül 1 ile paylaşımlı |

---

## 📞 Modül 19: call_routing_and_ceo_mode (CEO Çağrı Modu)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | I2S DAC | MAX98357A | 1 | ~$3 | Hoparlör sürücü (çağrı sesi → oda) |
| 2 | (Donanım) | ESP32-S3 (ELDE, Modül 1 paylaşımlı) | — | $0 | BT Proxy + HFP + I2S |
| 3 | (Donanım) | INMP441 (ELDE, Modül 1 paylaşımlı) | — | $0 | Mikrofon |
| 4 | (Yazılım) | HA Companion App | — | $0 | phone_call_state sensörü |

---

## 🪞 Modül 20: magic_mirror_comm_and_grooming (Ayna İletişim + Stil Koçu)

> **Mimari değişiklik:** Pi Zero ÇÖP → TV + Mi Box (Modül 4) üzerinden. USB kamera/mikrofon Mi Box'a bağlanır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | USB Web Kamera | Logitech C270 (720p mini) | 1 | ~$25 | TV üstüne / ayna çerçevesine gizli |
| 2 | USB Mikrofon | Mini USB mic | 1 | ~$10 | Gizli |
| 3 | Hoparlör | Mini 3W speaker | 1 | ~$5 | TTS + arama |
| 4 | (Donanım) | Mi Box S 4K (planlanan, Modül 4 paylaşımlı) | — | $0 | USB port üzerinden kamera/mic bağlanır |

---

## 🚗 Modül 21-25: Araç Modülleri (Knight Rider, Omniscience, Stealth, Edge-AI, Sentry)

> Araç modülleri ayrı satın alma fazındadır (yurt odası bitmeden öncelik değil). Detaylı listeler modül klasörlerindeki `hardware_and_*.md` dosyalarında korunur.

| Modül | Ana Donanım | Fiyat (≈) | Durum |
|---|---|---|---|
| 21 — car_knight_rider_core | Android Head Unit + OBD2 ELM327 | ~$170-275 | 🟢 İleri faz |
| 22 — car_omniscience_copilot | FLIR One IR kamera + OBD2 Wi-Fi | ~$220 | 🟢 İleri faz |
| 23 — car_stealth_and_seduction | (Yazılım ağırlıklı) | ~$0-35 | 🟢 İleri faz |
| 24 — car_edge_ai_vision | Jetson Nano 4GB + IMX219 | ~$200-250 | 🟢 İleri faz |
| 25 — car_sentry_mode_security | PIR + 12V röle | ~$12-27 | 🟢 İleri faz |

---

## 🖥️ Modül 27: OpenClaw Digital Sandbox

> Donanım YOK — tamamen VPS üzerinde Docker. Sadece yazılım.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Dijital Ajan | OpenClaw v2026.4.15 (MIT, açık kaynak) | 1 | $0 | browser-use + shell + file ops |
| 2 | Tarayıcı Otomasyon | browser-use (Playwright) | 1 | $0 | AI-native, headless mode |
| 3 | Docker Sandbox | Docker CE (VPS üzerinde) | 1 | $0 | Zero Trust 7 katman |
| 4 | Mealie (tarif DB) | Mealie 3.13+ (Docker) | 1 | $0 | Açık kaynak tarif yöneticisi, REST API |

---

## 🍳 Modül 28: Multicooker Chef Automation (Hisense HMC6SBK)

> **Mimari değişiklik:** Xiaomi Mi Smart Multi Cooker 3L → **Hisense HMC6SBK 6L** (ELDE). 2× kapasite, 1500W. WiFi YOK → güç izleme + Vision-Cooker orkestrasyonu.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Multicooker | **Hisense HMC6SBK 6L** (ELDE) | 1 | ~$80 | 1500W, 10-13 program (basınçlı pişirme, slow cook, pilav, buğulama, yoğurt), paslanmaz çelik iç kap. WiFi YOK |
| 2 | Akıllı Priz (Güç Ölçümlü) | Tuya UK Smart Plug (planlanan) | 1 | ~$12 | Güç izleme: 1500W (ısınma) → ~40W (keep-warm) → "pişirme bitti" tespiti |
| 3 | Mealie Docker | (Modül 27 ile paylaşımlı) | — | $0 | Aynı Docker instance |
| 4 | (Yazılım) | Vision-Cooker orkestrasyonu | — | $0 | Tapo C200 (Modül 13) malzemeleri görür → Mealie tarif eşleştirir → kullanıcı başlatır → güç izleme bitişi tespit eder → bildirim |

> **Neden WiFi'siz Hisense ve Xiaomi değil?** Hisense 6L (Xiaomi 3L), 1500W (Xiaomi 700W), ~$80 (Xiaomi ~$45 + Çin bulut riski). Hisense'in "akıllı" kısmı Jarvis'te: kamera görür, Mealie eşleştirir, priz izler, Jarvis bildirir. Tencerenin kendisinin WiFi'ye ihtiyacı yok — zeka bulutta.

---

## ⏸️ Modül 29: Embodied Jarvis Avatar — BEKLEMEDE

> Robotik proje — oda temeli bitene kadar satın alma YOK. Dokümantasyon `embodied_jarvis_avatar/` klasöründe korunur.

---

## ⏸️ Modül 30: Desktop Pet Kame — BEKLEMEDE

> Robotik proje — oda temeli bitene kadar satın alma YOK. Dokümantasyon `desktop_pet_kame/` klasöründe korunur.

---

## ⏸️ Modül 31: Siber Barmen (CocktailBerry) — BEKLEMEDE

> Robotik proje — oda temeli bitene kadar satın alma YOK. Dokümantasyon `siber_barmen_cocktailberry/` klasöründe korunur. Raspberry Pi gerektirdiğinden, ileride tekrar değerlendirilir (VPS + ESP32 röle alternatifi).

---

## 🛡️ Modül 32: Yurt İklim ve Solunum Kalkanı (Planlanan)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Nem Alma Cihazı | Hisense D16CW (1.6L/gün) | 1 | ~$120 | Kompresörlü, Auto-Restart — planlanan |
| 2 | Akıllı Priz | Tuya UK Smart Plug | 1 | ~$12 | Hisense'i otonom tetikler + güç izleme |
| 3 | Sensör | BME280 (Sıcaklık + Nem + Basınç) | 1 | ~$5 | I2C, ESP32'ye bağlı — planlanan |
| 4 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | ~$5 | BME280 okur, MQTT yayınlar |
| 5 | HEPA Filtre + 12V PC Fanı | DIY hava temizleyici | 1 set | ~$25 | Toz/küf/polen filtreleme |

> **Not:** Klima kontrolü artık Broadlink yerine **Tuya IR+RF** (ELDE) ile — klima zaten bağlı. Gece modu: Hisense kapat + klima 26°C + swing tavan (boğaz koruması).

---

## 💡 Modül 33: Yeelight Ambiyans Aydınlatma (Yeni — ELDE)

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Akıllı Ampul | **Yeelight Smart LED Color Bulb 1S** (ELDE) | 1 | ~$15 | 16M renk, WiFi. HA yerel Yeelight entegrasyonu — LAN Control aç (bulut YOK) |
| 2 | (Yazılım) | HA Yeelight integration + music mode | — | $0 | Music mode: >60 istek/dk limiti kalkar → hızlı efekt geçişleri |

> **Kullanım:** WLED duvar şeridi ile birlikte çalışır — Yeelight oda genel ambiyansı (tavan lambası), WLED duvar ritmi. "Sinema modu" → Yeelight %10 kehribar + WLED off. "Parti" → Yeelight renk döngüsü + WLED audio reactive.

---

## 📺 Modül 34: TV Medya Merkezi (Mi Box S — Planlanan)

> TV'nin IR alıcısı arızalı → TV değişecek. Yeni TV + Mi Box S 4K ile tam akıllı medya merkezi.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | TV Box | **Xiaomi Mi Box S 4K 32GB WiFi 6 (3rd Gen)** | 1 | ~$60 | Google TV 14, AMLogic S905X5M, 4×2.5GHz, 2GB RAM, HDMI 2.1a, Dolby Vision/Atmos, Chromecast dahil |
| 2 | (Yazılım) | HA Android TV integration (ADB) | — | $0 | Power, volume, app kontrolü — yerel ağ |
| 3 | (Yazılım) | Chromecast (dahili) | — | $0 | Spotify/video cast — jarvis_core media_player |
| 4 | (Yazılım) | MagicMirror² web Kiosk | — | $0 | Tarayıcıda tam ekran → TV ayna (Modül 4) |

> **Neden Mi Box S 4K?** Chromecast dahil (jarvis_core medya cast), Google TV (HA Android TV entegrasyonu ile tam kontrol), MagicMirror² tarayıcı gösterimi, 32GB depolama, WiFi 6. Fire TV Stick (Amazon bulutu) ve Chromecast 4K (tek fonksiyon) yerine çok daha yetenekli.

---

##  Toplam Maliyet Özeti

### Aktif Sistem (Oda Temeli — Ses, Işık, Otomasyon)

| Kategori | Adet | Toplam Fiyat (≈) |
|---|---|---|
| **Genel Altyapı** (VPS, GL-MT3000, akım koruma) | — | ~$120 + $10/ay |
| **Mikrodenetleyiciler** (ESP32-S3 ×2 ELDE + ESP32 DevKit ×1-2 plan) | 3-4 | ~$25 |
| **Sensörler** (LD2410, MPU6050, TTP223 ×5, INMP441 ×2, TSOP1838 — HEPSİ ELDE) | 10 | ~$25 |
| **Hoparlörler** (Echo Dot 5 ×2 — ELDE) | 2 | ~$100 |
| **Kameralar** (Tapo C200 ×2 — plan) | 2 | ~$50 |
| **Akıllı Prizler** (Tuya UK ×3-4 — plan) | 4 | ~$48 |
| **LED & Aydınlatma** (WS2812B 300 LED plan + Yeelight ELDE + COB plan + difüzör profil) | — | ~$130 |
| **Mutfak** (HAUSBERG espresso ELDE + Hisense multicooker ELDE) | 2 | ~$150 |
| **Perde Motoru** (28BYJ-48 + ULN2003 — ELDE) | 1 | ~$4 |
| **IR+RF Kumanda** (Tuya — ELDE) | 1 | ~$18 |
| **TV Medya** (Mi Box S 4K — plan) | 1 | ~$60 |
| **Difüzör + Esanslar** (plan) | — | ~$70 |
| **Kablo & Direnç & Kondansatör** (çoğu ELDE) | — | ~$15 |
| **API Abonelikleri** (MiniMax, DeepSeek, Qwen-VL, Spotify) | — | ~$15/ay |
| **TOPLAM (Tek Seferlik — Aktif)** | — | **~$815** |
| **TOPLAM (Aylık)** | — | **~$25/ay** (VPS $10 + API $15) |

> **Not:** ~$815'in ~$290'ı zaten ELDE (envanter + yeni alınanlar). Kalan ~$525 satın alma listesinde.

### Beklemede (Robotik — Oda Temeli Bitince)

| Kategori | Fiyat (≈) |
|---|---|
| Modül 29 (Lamba) | ~$105 |
| Modül 30 (Kame) | ~$45 |
| Modül 31 (CocktailBerry) | ~$265 |
| **TOPLAM (Beklemede)** | **~$415** |

### Planlanan (İklim + Araç — İleri Faz)

| Kategori | Fiyat (≈) |
|---|---|
| Modül 32 (İklim Kalkanı) | ~$181 |
| Modül 21-25 (Araç) | ~$600-800 |
| **TOPLAM (Planlanan)** | **~$780-980** |

---

## 🛒 Satın Alma Öncelik Sırası (Yeniden Yapılandırılmış)

> **Prensip: "Önce odanın temeli (ses, ışık, otomasyon). Robotiğe ve lükse 1 kuruş yok."**

### Faz 1 (TEMEL — Beyin + Ses) — Çoğu ELDE ✅
1. VPS kurulumu (Docker: HA + jarvis_core + ChromaDB) — $10/ay
2. GL-MT3000 + Tailscale tüneli (ELDE/mevcut)
3. **ESP32-S3 #1 + INMP441 #1** (ELDE) → Ses Hub kurulumu
4. **Echo Dot 5 × 2** (ELDE) → stereo pair + HA entegrasyonu
5. MiniMax + DeepSeek + Qwen-VL API abonelikleri
6. **Tuya IR+RF** (ELDE) → klima + vantilatör HA `tuya-local` entegrasyonu

### Faz 2 (IŞIK — WLED + Yeelight)
7. **WS2812B 300 LED şerit** (~$20) + 5V 10A güç (~$15) → ESP32-S3 #2 (ELDE) + INMP441 #2 (ELDE) ile WLED Audio Hub
8. **Yeelight Bulb 1S** (ELDE) → HA Yeelight yerel entegrasyonu (LAN Control)
9. Alüminyum difüzör profil (premium görünüm)
10. MCU2812B (ELDE) ile prototip doğrulama → sonra 300'lük şerit montajı

### Faz 3 (KONFOR — Mutfak + Perde + Prizler)
11. **Tuya UK Smart Plug × 3-4** (~$12/adet) → Hausberg espresso + Hisense multicooker + klima güç izleme
12. **HAUSBERG HB3723** (ELDE) + priz → "kahve hazır" güç analizi otomasyonu
13. **Hisense HMC6SBK** (ELDE) + priz → "pişirme bitti" güç analizi otomasyonu
14. **28BYJ-48 + ULN2003** (ELDE) + ESP32 DevKit (~$5) → DIY perde motoru (ESPHome stepper)
15. **NFC NTAG213 × 8** (ELDE) + PN532 okuyucu (~$5) → gizli NFC tetikleyiciler

### Faz 4 (SENSÖR + GİZLİ TETİK)
16. **TTP223B × 5** (ELDE) → masa altı gizli dokunmatik (ESP32 Sensör Hub)
17. **HLK-LD2410B** (ELDE) + COB LED (~$25) → yatak altı rehber aydınlatma
18. **MPU6050** (ELDE) → yatak ritim algılama (intimacy sync)
19. **TSOP1838 + LTE-4206 + 2N2222 + 220R** (ELDE) → ESP32 IR öğrenme + blaster (yedek kumanda)

### Faz 5 (MEDYA — TV + Mi Box)
20. **Xiaomi Mi Box S 4K 32GB WiFi 6** (~$60) → HA Android TV + Chromecast + MagicMirror² web Kiosk
21. TV değişimi (IR alıcısı arızalı — mevcut TV çöpe/nakit)

### Faz 6 (ATMOSFER — Projeksiyon + Difüzör)
22. Tuya Galaksi Projeksiyon (~$30) → derin uzay illüzyonu
23. Tuya Difüzör (~$25) + esans yağları (~$45) → koku otomasyonu

### Faz 7 (GÜVENLİK + VISION)
24. Tapo C200 × 2 (~$50/çift) → yüz tanıma + mutfak vision (Qwen-VL)

### Faz 8 (İKLİM KALKANI)
25. Hisense D16CW (~$120) + Tuya priz → nem alma otomasyonu
26. BME280 + ESP32 (~$10) → nem sensörü
27. DIY HEPA + fan (~$25) → hava temizleyici

### ⏸️ BEKLEMEDE (Oda Temeli Bitince)
- Modül 29: Robotik Lamba (~$105)
- Modül 30: Kame Robot (~$45)
- Modül 31: CocktailBerry (~$265)
- Modül 21-25: Araç modülleri (~$600-800)

---

## 🎨 Kablo Gizleme ve Estetik Montaj Malzemeleri

> **"Premium Lounge" teması için KRİTİK.**
> WLED şeridinin, kameranın veya radarın kablosu duvardan siyah/kırmızı şekilde sarkarsa, misafirin gözünde lüks algısı anında "öğrenci işi kablo karmaşasına" döner. Tüm kablolar görünmez olmalıdır.

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Kablo Gizleyici Kılıf | Cırtlı kablo sleeve (duvar renginde/beyaz) | 5m | ~$8 | Birden fazla kabloyu tek tüp içinde toplar |
| 2 | İnce Kablo Kanalı | PVC kablo kanalı (beyaz/duvar rengi, 15×10mm) | 5m | ~$5 | Duvar kenarında, baseboard boyunca |
| 3 | Çift Taraflı Bant | 3M VHB (siyah/beyaz) | 2 rulo | ~$10/adet | ESP32 ve sensörleri mobilya altına bantlama |
| 4 | Kablo Bağı | Siyah kelebek kablo bağı | 100 adet | ~$5 | Kablo demetlerini sabitleme |
| 5 | Duvar Rengi Boya | Kablo kanalı ile aynı renk | 1 | ~$5 | Tam gizleme |
| 6 | Möbius / Felt Kılıf | Keçe kablo gizleyici | 2m | ~$7 | Yatak/masa altı |
| 7 | USB Kablo (Düz) | Düz başlı USB-C (kısa, 30-50cm) | 5 | ~$3/adet | ESP32'ler için kısa, gizli kablolar |
| 8 | Baseboard Kablo Kanalı | Zemin süpürgeliği arkası | 5m | ~$8 | Oda çevresi (tam gizli) |

### Kablo Gizleme Kuralları

| Kural | Açıklama |
|---|---|
| **Sadece uçlar görünür** | Sensörlerin ve LED'lerin sadece fonksiyonel uçları görünmeli, kablolar asla |
| **Duvar rengine uyum** | Kablo kanalları ve sleeve'ler duvar rengine boyanmalı |
| **Mobilya altı bantlama** | Tüm ESP32'ler ve kablolar yatak/masa/komodin altına 3M VHB ile bantlanmalı |
| **Baseboard kullanımı** | Oda çevresi kablolar baseboard arkasından geçmeli |
| **Kısa kablo prensibi** | Mümkün olan en kısa kablo (sarkma olmasın) |
| **Kablo sleeve ile toplama** | Birden fazla kablo tek sleeve içinde |
| **Güç kabloları ayrı** | 220V güç kabloları veri kablolarından ayrı kanalda (EMI önleme) |

---

*Bu dosya, projenin tüm donanım ihtiyaçlarını listeler. Mimari değişiklikler (Pi'siz bulut beyni) ve yeni alımlar yansıtılmıştır. Yeni modüller eklendikçe güncellenir.*
