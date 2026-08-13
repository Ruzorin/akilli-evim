# 🏨 Jarvis Premium Automation Suite — Executive Edition (2026)

> **"Sinematik atmosfer, duyusal optimizasyon ve otonom yapay zeka ile yaşam ve mobil alanları tek bir akıllı ekosistemde birleştiren premium otomasyon platformu."**

Bu proje, bir yaşam alanını ve aracı; sesli komutlarla yönetilebilen, sensörlerle çevresel farkındalığa sahip, görsel-işitsel-duyusal olarak sinematik bir atmosfer sunan ve çok-modelli yapay zeka ile proaktif karar veren **premium bir otomasyon ekosistemine** dönüştürür. Sistem, merkezi bir hibrit zeka beyni (`jarvis_core` — MiniMax + DeepSeek) etrafında **30 modülden** oluşan tek bir kod tabanı (Single Codebase) mimarisiyle inşa edilmiştir. Sistem, dijital ajan (OpenClaw), fiziksel avatarlar (5-DOF robotik lamba + dört bacaklı robot evcil hayvan) ve akıllı mutfak otomasyonu ile fiziksel-dijital dünyayı birleştirir.

---

## 🏗️ Executive Mimarisi Özeti

### Bulut / Sunucu Altyapısı
- **VPS (Bulut):** Docker tabanlı Home Assistant + jarvis_core 3.0 (Python) + ChromaDB (yüz hafızası)
- **Tailscale VPN:** VPS ↔ GL-MT3000 (Beryl AX) arasında şifreli mesh tünel (<50ms gecikme)
- **Edge-to-Cloud:** Tüm yerel cihazlar (ESP32, WLED, Jetson Nano) bu tünel üzerinden VPS tarafından milisaniyelik hızda kontrol edilir

### Yapay Zeka Beyni (Hybrid Brain — Maliyet Optimize)
- **MiniMax Speech 2.8 Turbo:** Sesten-sese (Speech-to-Speech) End-to-End Multimodal. STT/TTS ara katmanları YOK. <300ms gecikme. Voice Cloning (10 sn referans → Jarvis tonu). Duygu kontrol (charming/sarcastic/intimate/authoritative). ~$10/ay
- **DeepSeek V4-Pro:** Ağır zeka (kod yazma, analiz, günlük özet). Çok ucuz (~$1-2/ay). MiniMax → DeepSeek → sonuç → MiniMax seslendirir
- **Qwen-VL Max:** Görüntü analizi (kamera, vision). Ucuz (~$2/ay). "Kameradan mutfağa bak" → Qwen-VL → analiz → MiniMax seslendirir
- **Günlük Hafıza:** Konuşma → DeepSeek özet → ertesi gün MiniMax System Prompt'a yükle (Prompt Caching). Ses token maliyetine girmeden geçmişi hatırla
- **Agentic Framework:** Statik intent'ler YOK — AI dinamik karar verir, HA REST API'yi doğrudan manipüle eder

### Maliyet Karşılaştırması
| Eski (OpenAI / Google) | Yeni (MiniMax + DeepSeek + Qwen) |
|---|---|
| GPT-4o Realtime API ~$50-100/ay | MiniMax Speech 2.8 Turbo ~$10/ay |
| OpenAI TTS Voice ~$5/ay | Voice Cloning dahil (ekstra $0) |
| Gemini Vision (Görüntü) ~$10/ay | Qwen-VL Max ~$2/ay |
| Toplam: ~$65-115/ay | **Toplam: ~$12-15/ay** |

### Donanım Katmanı
- **Mikrodenetleyiciler:** ESP32/ESP32-S3, ESPHome 2026
- **Aydınlatma:** WLED (Sound Reactive) + COB LED + Hyperion.ng (ekran senk)
- **Sensörler:** LD2410/LD2450 mmWave radar, MPU6050 ivmeölçer, TTP223 kapasitif, INMP441 I2S mikrofon
- **Araç:** OBD2 ELM327, Nvidia Jetson Nano 4GB + Sony IMX219 (Edge-AI ADAS)
- **Gömülü:** Raspberry Pi Zero 2 W (Magic Mirror), Raspberry Pi 4 (jarvis_core + Hyperion)

### Modül İsimlendirme Standartları
Bu projede modüller, fonksiyonel amaçlarını net bir şekilde yansıtan teknik isimlerle tanımlanmıştır. Tüm modüllerin arkasındaki mantık (çevresel senkronizasyon, otonom iklim ayarı, akustik optimizasyon ve duyusal tetikleyiciler) tam güçle ve eksiksiz bir şekilde çalışmaktadır.

---

## 📐 Proje Vizyonu

- **Sinematik Atmosfer:** Tavan projeksiyonu ile "derin uzay" illüzyonu, sese duyarlı ambiyans aydınlatması, konumsal ses yönlendirme
- **Premium Otel Konforu:** Akıllı koku difüzörü, yatak altı rehber aydınlatma, otomatik perde, kahve makinesi otomasyonu
- **Görünmez Kontrol:** Flic butonları, gizli dokunmatik yüzeyler, NFC etiketleri, kapasitif ahşap dokunma
- **Duyusal Senkronizasyon:** Fiziksel ritmi algılayan ivmeölçer ile ışık nabzı, ses, iklim ve koku senkronizasyonu
- **Yapay Zeka Orkestrasyonu:** MiniMax Speech 2.8 Turbo (sesten-sese) + DeepSeek V4-Pro (ağır zeka) + Qwen-VL Max (vision) + Yüz Tanıma + Hafıza + Proaktif konuşma
- **Mutfak Şefi:** Qwen-VL Max ile tezgah analizi, tarif önerisi, güvenlik uyarısı, karizmatik şef kişiliği
- **Fiziksel Avatarlar:** 5-DOF robotik masa lambası (Autonomous OS — Jarvis'in fiziksel yüzü) + Kame32 dört bacaklı robot evcil hayvan (ESP32 — Jarvis'in fiziksel evcil hayvanı). Kamera/mikrofon YOK — tüm zeka Jarvis'ten MQTT ile gelir
- **Dijital Ajan (OpenClaw):** Zero Trust Docker sandbox içinde otonom tarayıcı/masaüstü ajanı. Fiziksel lamba ile MQTT senkron — görev tamam → lamba başını sallar, hata → sallar
- **Akıllı Mutfak:** Xiaomi/Tuya akıllı tencere (Çin bulutundan izole, yerel LAN) + Vision-Cooker kapalı döngü (Qwen-VL malzeme görür → tarif önerir → kullanıcı onayı → tencere pişirir → sesli/ışıklı bildirim)
- **Vücut Sağlığı Kalkanı:** Postür koruması (MediaPipe Pose), anti-mavi ışık protokolü, ekran parlaklık/renk sıcaklığı otonom ayarı

---

## 🌐 Ağ ve Donanım Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                         VPS (Bulut)                              │
│  ┌─────────────────┐    ┌──────────────────────────────────┐    │
│  │  Tailscale VPN   │◄──►│  Home Assistant (Docker)         │    │
│  │  (Mesh Ağı)      │    │  - Otomasyon Motoru              │    │
│  │                  │    │  - Zigbee2MQTT                   │    │
│  │                  │    │  - SmartIR / LocalTuya           │    │
│  └────────┬─────────┘    └──────────────────────────────────┘    │
└───────────┼─────────────────────────────────────────────────────┘
            │ Tailscale VPN (Şifreli Tünel)
┌───────────┼─────────────────────────────────────────────────────┐
│           ▼            Oda (Yerel Ağ)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GL-MT3000 (Beryl AX) — Yerel Yönlendirici               │   │
│  │  - WiFi 6 + Tailscale Client + Yerel MQTT Broker         │   │
│  └───────────┬──────────────────────┬───────────────────────┘   │
│              │                      │                            │
│     ┌────────┴────────┐   ┌────────┴─────────┐                  │
│     │  ESP32 (ESPHome) │   │  Zigbee Ağı      │                  │
│     │  - WLED Audio    │   │  (Sensörler,     │                  │
│     │  - LD2410 Radar  │   │   Prizler,       │                  │
│     │  - MPU6050       │   │   Perdeler,      │                  │
│     │  - TTP223 Touch  │   │   Butonlar)      │                  │
│     │  - INMP441 Mic   │   │                  │                  │
│     │  - Kame32 (8srv) │   │                  │                  │
│     └─────────────────┘   └──────────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Raspberry Pi │  │ Tuya Proj.   │  │ Broadlink / Akıllı    │  │
│  │ Zero (Ayna)  │  │ + Difüzör    │  │ Prizler / IP Kamera  │  │
│  │ Pi 4 (Lamp)  │  │ + Multicooker│  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Edge-to-Cloud Mimari — Donanım Maliyetini Sıfırlama

> **"Premium otomasyon bir sunucu odası tutmaz. Bulutun gücünü cebine koyar."**

Bu proje, fiziksel bir Raspberry Pi / PC sunucusu gerektirmez. Sistem **ucuz bir Bulut VPS** üzerinde kurulur ve **Tailscale VPN** aracılığıyla Kıbrıs'taki yurt odasında bulunan **GL-MT3000 (Beryl AX)** yönlendiriciye tünellenir.

### Edge-to-Cloud Architecture

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    BULUT VPS (~$10/ay)                       │
  │                                                             │
  │  ┌─────────────────┐  ┌──────────────────────────────────┐  │
  │  │  Tailscale VPN  │  │  Home Assistant (Docker)          │  │
  │  │  (Mesh Ağı)     │  │  + jarvis_core 3.0 (Python)      │  │
  │  │  Şifreli tünel   │  │  + ChromaDB (Yüz hafızası)       │  │
  │  │  <50ms gecikme   │  │  + Multi-Model Orchestrator      │  │
  │  └────────┬─────────┘  └──────────────────────────────────┘  │
  └───────────┼─────────────────────────────────────────────────┘
              │ Tailscale VPN (Şifreli tünel — WireGuard tabanlı)
              │ Gecikme: <50ms (Kıbrıs ↔ VPS arası)
              │
  ┌───────────┼─────────────────────────────────────────────────┐
  │           ▼            Kıbrıs / Yurt Odası (Edge)            │
  │  ┌────────────────────────────────────────────────────────┐ │
  │  │  GL-MT3000 (Beryl AX) — Yerel Yönlendirici             │ │
  │  │  - WiFi 6 Erişim Noktası                               │ │
  │  │  - Tailscale Client (VPS'e köprü)                      │ │
  │  │  - Yerel MQTT Broker (ESP32 ↔ HA arası)                │ │
  │  │  - Zigbee2MQTT (USB dongle)                            │ │
  │  └───────────┬──────────────────────┬──────────────────────┘ │
  │              │                      │                          │
  │     ┌────────┴────────┐   ┌────────┴─────────┐              │
  │     │  ESP32 (ESPHome) │   │  Zigbee Ağı      │              │
  │     │  - WLED Audio    │   │  (Sensörler,     │              │
  │     │  - LD2410 Radar  │   │   Prizler,       │              │
  │     │  - MPU6050       │   │   Perdeler,      │              │
  │     │  - TTP223 Touch  │   │   Butonlar)      │              │
  │     │  - INMP441 Mic   │   │                  │              │
  │     │  - Kame32 (8srv) │   │                  │              │
  │     └─────────────────┘   └──────────────────┘              │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
  │  │ Pi Zero (Ayna)│  │ Tuya Proj.   │  │ Broadlink/Prizler│  │
  │  │ Pi 4 (Lamp)  │  │ + Multicooker│  │                  │  │
  │  └──────────────┘  └──────────────┘  └──────────────────┘  │
  └────────────────────────────────────────────────────────────┘
```

### Neden Edge-to-Cloud?

| Faktör | Fiziksel Sunucu (Evde) | Edge-to-Cloud (VPS + Tailscale) |
|---|---|---|
| **Maliyet** | ~$55 (Pi 4) + elektrik + internet | ~$10/ay VPS (elektrik/internet dahil) |
| **Kesinti** | Kıb-Tek kesintisi → HA çöker | VPS 7/24 çalışır, Kıb-Tek bağımsız |
| **Güncelleme** | Manuel, fiziksel erişim gerekir | SSH ile uzaktan, her yerden |
| **Gecikme** | 0ms (yerel) | <50ms (Tailscale VPN) — yeterli |
| **Güvenlik** | Yerel ağ, fiziksel erişim riski | Tailscale (WireGuard) şifreli tünel |
| **Scalability** | Sabit donanım | VPS yükseltilebilir (RAM, CPU) |

> **Sonuç:** Fiziksel sunucu almak yerine, ~$10/ay VPS + Tailscale ile tüm sistem bulutta çalışır. Yurt odasındaki GL-MT3000, VPS'e şifreli tünel üzerinden bağlanır. ESP32'ler, WLED, Zigbee cihazları — hepsi bu tünel üzerinden milisaniyelik hızla VPS'teki HA tarafından kontrol edilir. **Donanım maliyeti sıfırlanır, sadece ~$10/ay bulut bedeli.**

---

## 📦 Modüller (30 Modül — 2026)

### 1. `jarvis_core` — Sistemin Beyni 🧠 (Core 3.0 — 2026 AGI)

**Sürüm 1 (HA Orkestrasyonu):**
- DeepSeek V4-Pro + Extended OpenAI Conversation entegrasyonu (metin tabanlı fallback)
- MiniMax Speech 2.8 Turbo (sesten-sese, <300ms) + Voice Cloning (Jarvis tonu)
- System Prompt: Karizmatik uşak kişiliği (kısa cevap, zarif dil, gizemli, sessiz işleyiş)
- 10 function calling: ışık, difüzör, klima, medya, perde, projeksiyon, modül tetikleme
- NLP Intent Script'leri: "Misafirimizi ağırlayalım" → barista + diffuser, "Modumuzu değiştir" → audio + spatial

**Sürüm 2.0 (Bilinç Kazandı):**
- **Zero-Latency Voice Pipeline:** MiniMax Realtime API (WebRTC streaming) → <500ms gecikme (deprecated — v4.0'da MiniMax Speech 2.8 Turbo ile değiştirildi)
- **Duygusal Tonlama (Voice Design):** 5 duygu profili — charming, sarcastic, neutral, intimate, authoritative
- **Yüz Tanıma + Hafıza:** IP kamera → OpenCV face_recognition → ChromaDB (yerel vektör DB). Tüm veriler LOKAL
- **Karakter Anayasası (v2):** 10 kural — karizmatik uşak kişiliği, hafif alaycı, wingman, proaktif
- **Proaktif Sohbet (Autonomous):** 15dk sessizlik → sohbet başlat. Bilinen misafir → ismiyle karşıla

**Sürüm 3.0 (2026 AGI — Agentic Orchestrator):**
- **Hibrit Beyin:** MiniMax Speech 2.8 Turbo (sesten-sese, <300ms, Voice Cloning, duygu kontrolü), DeepSeek V4-Pro (ağır zeka, kod, günlük özet, ~$1-2/ay), Qwen-VL Max (görüntü analizi, ~$2/ay)
- **Agentic HA API:** Statik intent script'leri YOK. DeepSeek V4-Pro, HA REST API'yi doğrudan manipüle eder. "Bize cyberpunk ortamı yap" → DeepSeek KENDİSİ WLED JSON + Spotify + klima ÜRETİR → HA'a gönderir → MiniMax kısa sesli cevap verir
- **Biyometrik Duygu Sync:** Akıllı saat (Apple Health/Google Fit → nabız) + kamera mikro-ifadeleri (Qwen-VL Max) → DeepSeek V4-Pro → duygu analizi → proaktif ortam ayarı (üzgün → sıcak amber + rahatlatıcı müzik)
- **AGI System Prompt 2026:** 6 kural — Agentic zihin, dinamik dil eğitimi, proaktif empati, karakter, agentic HA, duygu verisi okuma
- **Günlük Hafıza:** DeepSeek günü özetler → Prompt Caching → ertesi gün MiniMax yükler (bedava hafıza)

### 2. `hidden_triggers` — Gizli Tetikleyiciler 🔘

- **Zigbee Mini Buton:** Sonoff/Tuya ZBMINI, yatak başı + masa altı gizli. Tek tık → Lounge, çift tık → Sinema, basılı tut → sistem kapat
- **TTP223 Kapasitif Dokunmatik:** Ahşap masa altına yapıştırılmış, ahşabın üstünden dokunma algılar. 2sn basılı tutma → Intimacy modu. ESP32 + ESPHome, debounce kalibrasyonu (ahşap kalınlığına göre)
- **NFC Bardak Altlığı:** NTAG215 bardak altlığı altında. Telefon koy → auto-ducking (müzik %15'e kıs, sohbet modu)
- **Gecikmesiz çalışma:** <100ms → "sihir" hissi

### 3. `space_projection` — Derin Uzay Projeksiyonu 🌌

- **Tuya Galaksi Projeksiyon:** Yatak başucunda, doğrudan yukarı bakar. Nebula (bulutsu) + yeşil lazer (yıldız)
- **Yeşil lazer KAPALI:** "Çocuk odası" hissinden kaçınılır, sadece yavaş dönen nebula → "Interstellar" sinematik hissi
- **Motor hızı %10:** Çok yavaş → hipnotik, meditatif. Hızlı = "disko" → göz yorucu
- **5 sahne:** Deep Space (derin mavi), Romantic Nebula (koyu pembe), Cinema Night (lacivert), Morning Amber (kehribar), Off
- **Broadlink IR alternatifi:** Tuya uyumlu değilse, Broadlink ile IR kontrol
- **Sleep Fade-Out:** 45dk hareketsizlik → projeksiyon kapat → melatonin → derin uyku

### 4. `magic_mirror` — Akıllı Ayna 🪞

- **Two-way mirror akrilik + çerçevesiz LCD:** Siyah bant ile ışık sızdırmazlık
- **Akıllı priz mantığı:** LCD siyah ekran gösterse bile backlight çalışır → ayna illüzyonu bozulur. Güç kesik → %100 normal ayna
- **MagicMirror²:** Saf beyaz yazı, siyah arka plan (OLED hissi). Renkli ikonlar YOK. Saat (sağ üst), hava (sol üst), MMM-Spotify (alt orta — o an çalan şarkı), MMM-MQTT (orta — sinematik mesajlar)
- **Calm Technology:** Kullanılmadığında sadece ayna, kişi yaklaştığında "canlanır" (~10-15sn boot)
- **3 senaryo:** Yaklaşma → ekran aç, Intimacy/Date → MQTT mesajı ("Atmosphere set to Deep Flow..."), Uzaklaşma → 1dk sonra kapat

### 5. `spatial_audio` — Konumsal Ses 🔊

- **Stereo Pair (Cocoon Effect):** İki Echo Dot çapraz köşelerde, kulak hizasının altında, gizli. Tek hoparlör = "müzik orada", stereo pair = "müzik her yerde"
- **7 Mood:** acoustic_morning, lofi_focus, deep_rnb_date, intimacy_flow, coffee_shop, sleep_ambient, party_energy
- **Fade Script:** `audio_fade` — kademeli ses artırma/azaltma (0.5sn adımlar, insan kulağı fark etmez). Müzik ASLA aniden başlamaz/durmaz
- **Intimacy Dynamic Volume:** Activity Level arttıkça ses %25→%35 dinamik ayar
- **Sleep Timer:** 30 dakikada 6 adımda kademeli kısma → %0 → durdurma. "Müzik yavaşça uzaklaşıyor" → uykuya dalma

### 6. `underbed_lighting` — Yatak Altı Aydınlatma 🛏️

- **HLK-LD2410 mmWave Radar:** PIR sensörlerin 5 sorununu çözer (hareketsizken kapanma, yatakta dönmeyi algılama, sıcaklık bağımlılık, ölü bölge, gecikme)
- **Gate Filtresi (KRİTİK):** Gate 0-2 (0-2.25m) = yatak yanı → algıla. Gate 3+ (2.25m+) = yatak içi → görmezden gel. Yatakta dönmek ışığı tetiklemez
- **COB LED (Pürüzsüz Işık):** WS2812B noktasal LED yerine COB → "Floating Bed" illüzyonu (yatak havada duruyor)
- **3 senaryo:** Gece yönlendirmesi (ayak algıla → %15 aç, 3sn transition), Kapanış (2dk sonra fade-out), Vibe/Date modu (gece yönlendirmesi OFF, %30 sabit amber)

### 7. `morning_after` — Ertesi Sabah 🌅

- **Sirkadiyen Ritim:** Kortizol uyanış tepkisi — sesli alarm = "savaş ya da kaç" stresi, ışıkla uyanış = doğal ritim
- **SwitchBot Curtain:** Kornişe kırma-dökme yapmadan takılır, sessiz mod (~40dB)
- **WLED Yapay Gündoğumu:** 10 dakikada 4 aşama — #100000 (koyu bordo) → #FF4500 (turuncu) → #FFD700 (altın) → #FFAA55 (sıcak beyaz). transition: 180-240sn → "korkutmadan" uyanış
- **T-Eksi Orkestra:** T-10dk (WLED gündoğumu + perde %20), T-5dk (Spotify %5→%15 fade-in), T-0dk (perde %100 + barista_mode), T+2dk (Jarvis "Good morning. Weather is 24 degrees. Your espresso machine is ready.")
- **Barista entegrasyonu:** T-0dk'da barista_mode tetiklenir → espresso ısınmaya başlar → T+5dk "Espresso ready"

### 8. `invisible_remote` — Görünmez Kumanda 📡

- **Broadlink RM4 Mini:** 360° IR, TV ve klimayı görecek konumda gizli
- **SmartIR:** Klimayı termostat olarak HA'a entegre (sıcaklık, fan hızı, mod). 100+ klima markası hazır kod veritabanı
- **TV IR Script'leri:** Power, HDMI 1/2, Volume Up/Down, Mute. Kompozit script: Power → 3sn bekle → HDMI 1
- **Stealth otomasyonlar:** Intimacy → klima 20°C quiet (sessizce, arka planda). Netflix & Chill → TV aç + HDMI + sinema ışıkları. Oda boş 1saat → klima otomatik kapat
- **ESP32 + IR LED alternatifi:** Broadlink yerine ESP32 + ESPHome

### 9. `smart_diffuser` — Akıllı Koku Difüzörü 🌿

- **LocalTuya:** Bulut gecikmesi olmadan (<100ms) difüzör kontrolü
- **Koku Psikolojisi:** Koku → amigdala doğrudan (limbik sistem). Sandalağacı (topraklayıcı), Amber (lüks/güven), Ylang-Ylang (afrodizyak)
- **5 karışım reçetesi:** Pre-Arrival (Amber+Sandal 60/40), Date/Lounge (Sandal+Ylang 60/40), Intimacy (Ylang+Sandal 50/50), Barista (Amber+Vanilya 70/30), Deep Sleep (Sandal 100%)
- **RGB KAPALI:** Difüzörün ucuz RGB LED'i WLED ile çakışır → her zaman KAPALI. "Difüzör sadece koku yayar, ışık vermez"
- **3 senaryo:** Pre-Arrival (GPS yaklaşıma → high mist), Intimacy/Date (modül tetikleme → low/medium mist), Maintenance (oda boş/deep sleep → kapat)

### 10. `audio_reactive_wled` — Sese Duyarlı Ambiyans 💡

- **ESP32 + INMP441 I2S Mikrofon:** ESP8266 yetersiz (FPU yok, I2S yok). FFT için ESP32 şart
- **Difüzör Profil:** Çıplak LED = "oyuncu odası", alüminyum + mat akrilik difüzör = "premium lounge"
- **4 Preset:** Date Lounge (Amber/Kırmızı, Gravimeter bas odaklı), Deep Focus (Koyu Mavi, statik nefes), Party Energy (Turuncu+Altın+Magenta, Freqwave), Rest Idle (Loş amber, sabit)
- **Gökkuşağı YOK:** Sadece sıcak tonlar (amber, kırmızı, altın) → "premium" hissi. Gökkuşağı = "ucuz pavyon"
- **3 otomasyon:** Müzik başladı → Date Lounge preset (güneş batmışsa), Müzik durdu → Rest Idle, Mod değiştir (parti/odaklanma/lounge)

### 11. `barista_mode` — Kahve Otomasyonu ☕

- **NFC Etiketi (NTAG215):** Masanın altına gizli, telefon dokundur → kahve makinesi ısınmaya başlar
- **Güç Ölçüm (Smart Readiness):** Akıllı priz Watt değerini izler. 1000W+ (ısınma) → 20W altı (hazır) tespiti. "Su kaynadı" anını yakalama
- **Premium materyaller:** Çift cidarlı porselen fincan, Monin vanilya/karamel şurupları, Nespresso/Illy kahve, bambu sunum tepsisi
- **Atmosfer:** Işıklar %30 amber (2700K), WLED kahverengi/altın, Lo-Fi müzik %15
- **TTS:** "Barista mode activated. Pre-heating the espresso machine." → "The water is at optimal temperature. Your espresso is ready to brew."

### 12. `intimacy_sync_mode` — Sensory Rhythm ❤️‍🔥

- **MPU6050 İvmeölçer:** Yatak iskeletine gizli, fiziksel ritim algılama. ESP32 + ESPHome
- **Ritim Algılama Algoritması (C++ lambda):** 4 aşama — birleşik ivme, RMS pencere filtresi (tek darbeleri eler), ritmik hareket tespiti (ardışık darbe ±%30), Activity Level (0-100, EMA yumuşatma)
- **Duyusal Senkron:** Activity Level → WLED kırmızı nabız hızı + renk (#8B0000→#FF4500), Spatial Audio %25→%35, klima 20°C quiet, difüzör Ylang-Ylang+Sandalağacı
- **3 senaryo:** Başlat (ışıklar kırmızı, müzik R&B, klima serin, koku), Dinamik senkron (Activity Level'a göre WLED hızı/parlaklığı), Kapat (30dk hareketsizlik → otomatik)

### 13. `vision_chef_assistant` — Multimodal Aşçı 🧑‍🍳

- **IP Kamera (RTSP):** TP-Link Tapo, mutfak dolabı altına gizli, SADECE tezgahı görür (privacy)
- **Qwen-VL Max:** Kameradan kare → base64 → Vision API → tarif/uyarı/eleştiri
- **On-Demand Analiz:** Sürekli analiz YOK — sadece istek geldiğinde (CPU + API tasarrufu). Güvenlik modunda 0.5 FPS
- **Karizmatik şef kişiliği:** Hafif kibirli, zekice dalga geçen, yardımcı şef. Wingman taktiği (misafir varsa patronu ezerek misafiri yücelt)
- **3 senaryo:** "Bunlardan ne çıkar?" → tarif öner, Duman/yanma → proaktif uyarı + mobil critical bildirim, Çift tık → komik durum güncellemesi

### 14. `wingman_guest_protocol` — Giriş/Karşılama ve Wingman *(Planlanan)*

> Misafir odaya girişte Jarvis'in proaktif karşılama, yüz tanıma ile isimle hitap, geçmiş sohbet hatırlama, flörtöz wingman taktiği ve "premium hospitality" deneyimi.

### 15. `immersive_language_tutor` — Derinlemesine Dil Eğitmeni 📚

- **Ekstra donanım YOK:** Mevcut Jarvis Core, WLED, Spatial Audio, Magic Mirror ve klima altyapısını kullanarak odayı fiziksel bir "dil kapsülü"ne çevirir
- **Dil Eğitmeni Kişiliği:** Jarvis "Language Coach" moduna geçer — ASLA Türkçe konuşma, sadece hedef dil (İngilizce/Fransızca). Hataları doğal akış içinde düzeltme ("Şunu demek istedin sanırım..."). Uluslararası dil sınavı (IELTS/TEF/TCF) odaklı role-play ve pratik senaryolar
- **Fiziksel Çalışma Kapsülü:** WLED soğuk beyaz (5000K, zihin açıcı), klima 21°C (uyanık tutan serin), difüzör biberiye/limon (odaklanma) veya kapat, Spatial Audio kelimesiz Lo-Fi/Binaural Beats %10
- **Magic Mirror Pasif Öğrenme:** Ayna ekranında her 4 saatte bir değişen 5 İngilizce-Fransızca kelime çifti (MMM-Vocabulary modülü). Kullanıcı aynaya baktıkça bilinçaltı kaydeder
- **2 senaryo:** Başlat ("Fransızca çalışmaya başlayalım" / NFC "Study Book" → ortam + Jarvis dil eğitmeni), Kapat (2 saat otomatik veya sesli komut)

### 16. `holistic_life_os` — Yaşam İşletim Sistemi 🧬

- **Ekstra donanım GEREKMEZ:** Mevcut akıllı saat (Apple Watch/Wear OS), yatak radarı (LD2450), kamera ve HA altyapısını kullanır
- **Sensor Fusion:** Yatak radarı (kalp atışı + nefes + uyku evreleri) + akıllı saat (uyku süresi + adım + nabız) birleştirilir → en doğru uyku analizi
- **Agentic Takvim Esnetme:** Kötü uyku + esnetilebilir etkinlik → "10:00 toplantısını 11:00'e kaydırmamı ister misin?" → kullanıcı "evet" → Google Calendar API → etkinlik taşınır
- **Kan Tahlili Analizi:** PDF → PyPDF2 → metin → DeepSeek V4-Pro (2M token) → değerleri referans aralıklarıyla karşılaştır → "D vitamini düşük, demir eksik" + beslenme önerileri
- **Sabah Brifingi:** Magic Mirror'da takvim + ilaç/takviye checklist'i (D vitamini, B12, saç spreyi)
- **Takvim Çatışması:** Gece 02:00 + ışıklar açık + sabah sınav → "Verimliliğiniz için uyku moduna geçiyorum" → sistem kapat + alarm erken ayarla
- **Kalori Takibi:** "Bu yemeği kalori takibime ekle" → Vision API → kalori + makro → günlük hedefe ekle
- **Sağlık Koçu Kişiliği:** Doktor değil ama tatlı sert, bilimsel, isabetli tavsiyeler. "D vitamini düşük. Güneşe çıkın. Pencereden bakmak sayılmaz."

### 17. `hyperion_media_sync` — Ekran Senkronizasyonu ve Medya Atmosferi 🎬

- **Hyperion.ng:** Ekran kenar piksellerini anlık olarak WLED'e UDP ile yansıtır (<16ms = 1 frame). "Ekranın sınırları kaybolur" → imersif deneyim. UDP seçimi KRİTİK (TCP çok yavaş)
- **HDMI Grabber:** UCV007/MS2109 USB grabber + HDMI splitter → kaynak → TV + grabber → Hyperion
- **Stadyum Modu:** "Jarvis, maç başlıyor" → Hyperion ON + takım renkleri (GS Sarı-Kırmızı, FB Sarı-Lacivert, BJK Siyah-Beyaz) + difüzör narenciye/mentol + klima 20°C. 2 saat sonra otomatik Rest Idle
- **Agentic Media Orchestrator:** Qwen-VL Max ekranı analiz eder → içerik tipi (cyberpunk, nature, horror, romance, action, sports, anime, sci_fi) → AI KENDİSİ WLED/difüzör/klima/Spotify JSON üretir → HA REST API. "Blade Runner" → neon pembe + synthwave; doğa belgeseli → yeşil + ambient
- **Medya Yoldaşı Kişiliği:** Maç izlerken fanatik ama zeki spor yorumcusu (nadiren, tam yerinde). Film izlerken sinema eleştirmeni (trivia + tavsiye, sadece başlangıç/bitiş). "Sessizlik, en iyi yoldaşlıktır"

### 18. `life_os_superapp` — PWA SuperApp ve Çağrı Yönlendirme 📱

- **Ekstra donanım GEREKMEZ:** Mevcut HA PWA + Mushroom/Bubble Card (HACS) + ESP32-S3 Bluetooth Proxy (Modül 1) kullanır
- **PWA (Progressive Web App):** HA'ı telefona tam ekran native uygulama olarak ekle (adres çubuğu yok, kendi ikonu, app drawer'da)
- **Mushroom + Bubble Card:** Apple/Tesla tarzı minimalist UI — yuvarlak kartlar, boşluklu tasarım, swipeable sekmeler. "Kontrol paneli" değil "yaşam alanı" hissi
- **SuperApp Dashboard:** Üst (karşılama + takvim), Orta (swipeable: Ev kontrolü + Sağlık), Alt (Spotify/Hyperion medya), Sağ alt (floating AGI chat)
- **AGI Chat (Floating):** Sağ alt köşede sürekli duran chat butonu → MiniMax Speech 2.8 Turbo/DeepSeek V4-Pro'a yazılı komut → "Bize cyberpunk ortamı yap" → oda değişir. Fotoğraf at → "Bunu kalori takibime ekle" → Vision API
- **Bluetooth Proxy Çağrı Yönlendirme:** Telefon çağrısı → müzik duraklat + WLED mavi yanıp sönme → çağrı cevapla → ESP32-S3 BT Proxy → ses odaya aktar (hands-free) → çağrı bitince atmosfer geri döner

### 19. `call_routing_and_ceo_mode` — Gelişmiş Çağrı Yönlendirme ve CEO Modu 📞

- **Ekstra donanım:** I2S DAC (MAX98357A, ~$3) — diğer her şey Modül 1 ile paylaşımlı
- **Bluetooth Proxy + HFP:** ESP32-S3, HFP (Hands-Free Profile) ile telefon çağrısını alır → I2S DAC → oda hoparlörü (karşı taraf) + INMP441 mikrofon → çağrıya (senin sesin). Gecikme <50ms, AEC (yankı önleme)
- **CEO Modu:** Çağrı gel → Auto-Ducking (müzik %5) + WLED "Görüşme Modu" (sakin beyaz/mavi nefes) + klima quiet + difüzör kapat + projeksiyon kapat. "Oda bir yönetim merkezine dönüşür"
- **Akıllı Kimlik Analizi:** Arayan VIP mi? → Jarvis "Önemli arama efendim, [Ad] arıyor". Normal arama → sessiz (sadece ambiyans değişir)
- **Eller Serbest (Hands-Free):** Çağrı cevapla → BT Proxy ON → telefon cebinde, oda seni duyar. Normal ses tonuyla konuş, bağırmadan. "Telefon kulakta" değil "oda konferans salonu"
- **Kapanış:** Çağrı bit → BT Proxy OFF + müzik fade-in (5sn, pre_call_volume) + WLED eski atmosfere + klima eski fan + Jarvis "Görüşme sona erdi"

### 20. `magic_mirror_comm_and_grooming` — Ayna İletişim Konsolu ve Stil Koçu 🪞

- **Ekstra donanım:** USB web kamera (Logitech C270, ~$25), USB mikrofon (~$10), mini hoparlör (~$5), USB hub (~$5) — Pi Zero 2 W (Modül 4) üzerine monte
- **Görüntülü Arama (WebRTC):** Ayna kamerası + mikrofon + hoparlör → WebRTC peer connection → WhatsApp/Telegram görüntülü arama. "Jarvis, aramayı aynadan aç" → kamera/mikrofon otomatik görüşmeye yönlendirilir
- **Dijital Stil Koçu (Qwen-VL Max):** "Jarvis, kombin nasıl?" → ayna kamerasından snapshot → Qwen-VL Max → kıyafet/saç/tarz analizi → MiniMax Voice Cloning (charming) → "Kombin harika ama o ayakkabılar bu ceketle gitmemiş patron"
- **İmaj Danışmanı (Life OS Entegre):** Takvim (etkinlik tipi: formal/business/casual/date) + hava durumu + Vision analizi → "Bugün CEO görüşmesi var ama tişört casual kalmış, lacivert ceket giymelisin. Saçında yatışmazlık var, acele et"
- **Grooming Checklist UI:** MagicMirror² sağ alt köşede minimalist checklist (diş ipi, saç spreyi, D vitamini, B12) + kombin puanı (75/100) + öneri. Telefondan onayladıkça maddeler silinir

---

## 🚗 Araç Modülleri (Modül 21-24 — Mobil Komuta Merkezi)

### 21. `car_knight_rider_core` — Araç Beyni ve The Giant's Throne 🚗

- **Android Multimedya Ekranı:** 9-10" Head Unit → HA Companion App (PWA) + Tailscale → VPS. "Aractayım ama evim elimde"
- **OBD2 → HA:** ELM327 Bluetooth/Wi-Fi adaptörü → Torque/Car Scanner app → Webhook → HA sensörleri (RPM, hız, yakıt, motor sıcaklığı, DTC kodları)
- **The Giant's Throne:** Sürücüye özel milimetrik koltuk + direksiyon + dikiz aynası senkronizasyonu. Telefon aracın BT ağına bağlanınca → koltuk, direksiyon ve aynalar kullanıcının kayıtlı anatomik pozisyonuna otomatik ayarlanır. "Araç sürücüye uyum sağlar"
- **İklim Optimizasyonu:** Araç içi sıcaklık → kullanıcının tercih ettiği seviyeye önceden ayar (21°C)
- **Tesla Tarzı Dashboard:** Hız (renkli: >120 kırmızı), RPM, yakıt + ev durumu (sıcaklık, kilit, WLED, difüzör) + Jarvis sesli komut + DTC arıza kodları

### 22. `car_omniscience_copilot` — Gözetmen Copilot ve OBD2 Kehanet 🔮

- **IR Kamera + Akıllı Saat + OBD2 Sensor Fusion:** FLIR One / Seek Thermal IR kamera → PERCLOS (göz kırpma oranı) + esneme tespiti. Akıllı saat → nabız, HRV, stres. OBD2 Wi-Fi → MAF, yağ basıncı, şanzıman sıcaklığı
- **Fatigue & Ergonomic Guard:** PERCLOS >%15 → klima -2°C + difüzör nane/limon + Jarvis "Mola verin". >%25 → koltuk bel desteği %100 şişir + "Mola zorunlu". Omurga stres skoru (sürücü anatomisine göre hesaplanır) >70 → bel desteği şişir
- **Predictive Maintenance (Kehanet):** OBD2 trend analizi → arıza lambası yanmadan tespit. "Yağ basıncı düşüyor, 500 km içinde bakım" / "Şanzıman 95°C, yağ kontrolü" / "MAF sapması, hava filtresi temizliği" / "Bujiler kontrol" / "Akü 11.5V, değişim"
- **G-Kuvveti Optimizasyonu:** Yatay G >0.8g → "Viraj sert, yavaşlayın" + çekiş kontrolü enhanced. Yağmurlu zemin (sürtünme <0.5) → "Fren mesafesi 2x" + çekiş maximum + motor freni soft. Agresif fren (<-0.7g) → ABS maximum + mobil bildirim. Sürücü ağırlığına göre dinamik fren mesafesi hesaba katılır

### 23. `car_stealth_and_seduction` — Blackout, Seduction Suite, Sci-Fi Soundspace 🌑

- **Night Ops / Blackout:** "Jarvis, Blackout" → ekran %0 parlaklık + konsol ışıkları off + minimalist HUD (sadece hız + navigasyon). "Savaş uçağı cockpit'i — sadece yol, gerisi karanlık"
- **Mobile Seduction Suite:** "Date Mode" → WLED derin Yakut Kırmızısı #8B0000 + "Breathe" nefes efekti + klima 21°C quiet + difüzör imza koku (Odunsu/Amber — Pavlov etkisi) + Spotify "deep_rnb_date" %12 fade-in. "Misafir araca bindiğinde → bu bir araç değil, bir deneyim"
- **Sci-Fi Soundspace:** OBD2 RPM → fütüristik uzay gemisi sesi (sawtooth dalga, 55-220Hz, %8 volüm). RPM yükseldikçe hum frekansı yükselir → "sci-fi cockpit" hissi. Gece only, müzikten ayrı → "duyulmaz ama hissedilir"

### 24. `car_edge_ai_vision` — Nvidia Jetson Nano Edge-AI Vision & ADAS 🚀

- **Nvidia Jetson Nano 4GB + Sony IMX219:** 128 CUDA core, JetPack SDK (CUDA + TensorRT + OpenCV GPU). Kamera dikiz aynası arkasına monte (70° FOV, yola bakar)
- **OpenADAS + YOLO:** Açık kaynaklı OpenADAS projesi → YOLOv4-Tiny / YOLOv5s ağırlıkları → TensorRT FP16 optimizasyonu (FP32: 200ms/5FPS → FP16: 30ms/30FPS → gerçek zamanlı)
- **Canlı Şerit Takibi:** Canny edge + Hough transform → neon mavi/yeşil şerit çizgileri (sol yeşil, sağ sarı). 30 FPS gerçek zamanlı
- **Nesne Algılama (Bounding Box):** YOLO → araç, kamyon, otobüs, yaya, tabela algılama → renkli kutular + etiket
- **Forward Collision Warning (FCW):** Ön aracın Bounding Box genişliği → mesafe tahmini → genişlik >200px → kırmızı kutu + "FCW: COLLISION WARNING" → MQTT → HA → WLED kırmızı strobe + Jarvis sesli uyarı (~110ms gecikme)
- **MQTT → HA → WLED + TTS:** Tehlike → `jarvis/car/adas/warning` → HA → WLED kırmızı strobe (brightness 255, effect Strobe, transition 0) + TTS "{{ message }}" + 5sn sonra WLED normale. 5 uyarı tipi: FCW, LDW, AEB, PEDESTRIAN, TAILGATING

### 25. `car_sentry_mode_security` — Sentry Mode ve Akıllı Güvenlik 🛡️

- **Jetson Nano Deep Sleep:** Park halinde ~0.5W (GPU kapalı, sadece GPIO interrupt). 60Ah akü → 5 gün güvenli park. Akü <11.5V → akıllı röle → Jetson tamamen kapanır
- **PIR + Şok Tetikleme:** HC-SR501 PIR (GPIO 7) + MPU6050 şok (I2C + INT GPIO 8). Hareket/darbe → milisaniyeler içinde Jetson uyanır → kamera aç → snapshot + 30sn video kayıt
- **Telegram/WhatsApp Anlık Bildirim:** Snapshot → Telegram Bot API → "⚠️ Dikkat! Aracınızın yanına biri yaklaştı. Kayıt başlatıldı." + fotoğraf → telefona anlık (2-5sn). WhatsApp Business API alternatif
- **HA SuperApp Sentry Panel:** Tek dokunuş → Sentry ON/OFF. Son ihlal fotoğrafı + zaman + toplam ihlal sayısı + 7 gün ihlal geçmişi (history graph). "Tesla Sentry Mode" standardı

### 26. `jarvis_body_sync_medical` — Medikal Kalkan ve Kişisel Yaşam Desteği 🩺

- **Anti-VSS Lighting Protocol:** Visual Snow Syndrome için nöro-optik aydınlatma. WLED transition ≥3000ms (ani ışık YASAK), mavi ışık KAPALI (sadece kehribar/yeşil), Strobe/Flash efektleri engellenir. MagicMirror CSS: saf beyaz yerine koyu gri/kehribar, kontrast düşük, gölge yok
- **Posture & Spinal Guard:** MediaPipe Pose Estimation ile servikal açı analizi. Boyun 15°+ öne ("Tech Neck") → 30sn sürerse Jarvis "Postürünüzü düzeltin". 25°+ → "Ciddi postür bozukluğu" + WLED kehribar (rahatlatıcı). Skolyoz ve ileri baş postürü için ortopedik koruma
- **Tansiyon Senkronizasyonu:** Omron BLE tansiyon aleti → HA. >130/85 → "Yüksek Tansiyon Protokolü": barista mode KAPAT (kafein = tansiyon ↑), difüzör Ylang-Ylang (tansiyon ↓), klima 20°C (serin = tansiyon ↓). >160/100 → mobil critical bildirim + "Doktor kontrolü öneririm"
- **Biyometrik Brifing:** Tansiyon ölçümünden sonra Magic Mirror'da + sesli olarak: dünkü uyku kalitesi, tansiyon grafiği, omurga esneme hatırlatıcısı. "Düşük uyku kalitesi tansiyonunuzu etkileyebilir"

---

## 🤖 Dijital ve Fiziksel Ajan Modülleri (Modül 27-30 — Fiziksel-Dijital Köprü)

> Jarvis artık sadece ses ve ekrandan ibaret değil. Bilgisayarda sizin için iş yapan bir dijital ajanı, masada başını sallayan fiziksel bir lambası ve masada dans eden bir robot köpeği var. Bu dört modül, fiziksel ve dijital dünyaları birbirine bağlar.

### 27. `openclaw_digital_sandbox` — OpenClaw Dijital Ajan ve Zero Trust Sandbox 🖥️

- **Jarvis'in Dijital Elleri:** OpenClaw, Jarvis'in bilgisayarda sizin için iş yapan dijital ajanı. Tarayıcıda gezinir, dosya okur, shell komutları çalıştırır. "Bana uçuş ara" → OpenClaw tarayıcıyı açar, siteleri gezer, sonuçları getirir
- **Gerçek Dünya Siparişleri:** Sesli veya yazılı komutla günlük işleri otomatik halleder. "Yemeksepeti'den lahmacun söyle" → tarayıcıyı açar, restoranı bulur, siparişi verir. "İstanbul-Ankara otobüs bileti al" → sitesi açar, koltuk seçer, bileti alır. "Marketten süt ve ekmek sipariş et" → sepete ekler, teslimat saatini seçer. "Jarvis'e söyle, o halleder"
- **Otonom Tarif Avcısı (Mealie Recipe Hunter):** "Bana tarif bul" dediğinizde OpenClaw arka planda çalışır — ekranda pencere açmadan. Browser MCP ile 10+ kaynak tarar, Context7 MCP ile her tarifin protein oranı ve malzeme kalitesini doğrular, çöp tarifleri eler. Doğrulanan tarifleri Mealie (Modül 28) veritabanına otomatik kaydeder. İşlem bitince Lamba (Modül 29) başını sallar ve yeşil yanar. "Siz konuşurken, o arka planda tarif avlar"
- **Yemeksepeti Makro Enjektörü (Bio-Hacking):** "Sipariş verdim" dediğinizde OpenClaw tarayıcıda sepetinizi okur (2 lahmacun + 1 ayran), DeepSeek'e gönderir, "Yaklaşık 700 kcal, 28g protein" tahminini yapar ve Modül 16 (Life OS) günlük kalori hedefinize otomatik ekler. Tek tuşa basmazsınız — kalori hedefiniz arka planda güncellenir. "Sipariş verdim dersin, gerisini o halleder"
- **Zero Trust Güvenlik (7 Katman):** OpenClaw hiçbir zaman serbest çalışmaz. Docker konteyner içinde, root yetkisi olmadan, dosya sistemi kilitli, ağ kısıtlı. Tehlikeli komutlar otomatik engellenir. Önemli işlerde mobil onay ister — "Bu işlem için onayınız gerekli"
- **Fiziksel Lamba ile Senkron:** OpenClaw bir görevi bitirdiğinde masadaki robotik lamba (Modül 29) başını sallar ve yeşil ışık yanar. Görev hata alırsa lamba sallanır ve kırmızı yanar. Onay beklerken lamba size bakar ve kehribar renk yanar. "Dijital ajanınız fiziksel olarak size haber verir"

### 28. `multicooker_chef_automation` — Mealie + Multicooker Chef Automation 🍳

- **Thermomix'e Açık Kaynak Rakip:** 100.000₺'lik Thermomix'in kapalı Cookidoo ekosistemi yerine, Mealie (açık kaynak tarif yöneticisi) + Xiaomi akıllı tencere (~3.000₺) ile aynı fonksiyonları fazlasıyla karşılar. Üstelik makro hesabı, görüntü tanıma ve sesli kontrol Thermomix'te YOK. "Açık kaynak, kapalı sisteme karşı"
- **Mealie Tarif Kütüphanesi:** Bir tarif sitesinin URL'ini yapıştırırsınız → Mealie otomatik malzeme, talimat ve besin değerlerini çıkarıp veritabanına kaydeder. Tüm tarifler sizin sunucunuzda, hiçbir bulut bağımlılığı yok. "Tarif sitenizin URL'ini yapıştırın, gerisini Mealie halleder"
- **Sporcu Makro Orkestrasyonu:** DeepSeek, kilonuzu ve hedefinizi (bulk/cut/maintenance) alır, günlük protein/karb/yağ hedeflerinizi hesaplar. Mealie'deki tarifleri bu hedeflere göre dinamik olarak ölçekler — "125kg'sınız ve bakım modundasınız, bu tarifi 3 porsiyona çıkarıyorum, 810 kalori 68g protein" der. "Sporcu beslenmesi artık otomatik"
- **Gözle Pişir (Vision-to-Cook):** Modül 13'ün kamerası (Qwen-VL Max) tezgaha bakar, malzemeleri tanır. Mealie'deki tariflerle eşleştirir, size önerir. Onayladığınızda tencere otomatik başlar. "Kamera görür, Mealie eşleştirir, DeepSeek ölçekler, tencere pişirir"
- **VSS Dostu Bildirim:** Pişirme başlayınca WLED ışıklar pürüzsüz geçişle turuncu yanar (strobe YASAK, sadece kehribar/yeşil). Lamba (Modül 29) tencereye eğilir. Pişirme bittiğinde Lamba başını sallar ve yeşil yanar. Jarvis "Yemeğiniz hazır" der

### 29. `embodied_jarvis_avatar` — Embodied Jarvis Avatar (5-DOF Robotik Lamba) 💡

- **Jarvis'in Fiziksel Yüzü:** 3D yazıcı ile basılan 5 eksenli robotik bir masa lambası. Autonomous OS (açık kaynak robot işletim sistemi) ile çalışır. Beyin bulut VPS'de, Raspberry Pi sadece "gövde" — komutları alır ve servo motorları hareket ettirir. "Jarvis artık sadece ses değil, hareket eden bir fiziksel varlık"
- **Sana Bakar, Seni İzler:** Lamba size doğru dönebilir, size bakabilir, başını sallayabilir. Inverse kinematics ile yumuşak ve doğal hareketler. Acil durumlarda E-STOP ile anında durur
- **Postür Kalkanı:** MediaPipe Pose ile boyun açısı sürekli ölçülür. Boyun 15°+ öne eğilirse ("Tech Neck") lamba size döner, kehribar ışıkla nabız atar ve Jarvis "Postürünüzü düzeltin" der. 25°+ ise daha güçlü uyarı. Düzeltince lamba başını sallar ve yeşil yanar. "Lambanız aynı zamanda postür koçunuz"
- **Dijital Ajan ile Konuşur:** OpenClaw (Modül 27) bir iş bitirdiğinde lamba başını sallar. Kame (Modül 30) dans ettiğinde lamba ritme ayak uydurur. "Fiziksel ve dijital ajanlar birbiriyle konuşur"

### 30. `desktop_pet_kame` — Desktop Pet Kame32 (Dört Bacaklı Robot) 🐕

- **Jarvis'in Robot Köpeği:** Masada yaşayan, 3D basılmış, dört bacaklı bir robot. ESP32 + 8 ucuz servo motor (SG90/MG90S). Kamera ve mikrofonu YOK — tüm zekası Jarvis'ten MQTT ile gelir. "Köpeğin gözleri ve kulakları Jarvis'in kamerası ve mikrofonu"
- **Müziğe Dans Eder:** Modül 10'un mikrofonu (WLED INMP441) müziğin ritmini (BPM) analiz eder. Ritmi Kame'ye MQTT ile gönderir. Kame müziğin beat'ine göre çömelir, kalkar, ayak vurur, döner. "Müzik çalınca masanızdaki köpek dans eder"
- **Eye of Sauron — Otonom Şarj:** Kame'nin bataryası %20'ye düşünce, Tapo C200 kamera (Modül 13) OpenCV ile Kame'yi masada bulur. Kame'ye adım adım yürüme komutları gönderir, şarj pad'ine park eder. "Köpek kendi kendine şarja gider"
- **Wingman Karşılama:** Misafir geldiğinde (Modül 2 NFC veya Modül 13 yüz tanıma) Kame ayağa kalkar, 3 adım yürür, reverans yapar ve Jarvis sesli olarak karşılar. Misafir gidince uyku moduna geçer. Gece 23:00'da uyur, sabah 08:00'da uyanır. "Size gelen misafiri önce köpeğiniz karşılar"

---

## 🔗 Modüller Arası Haberleşme

### MQTT Topic Yapısı
```
jarvis/#
├── jarvis/core/command              → Jarvis komut kanalı
├── jarvis/audio/in                  → Mikrofon → Jarvis
├── jarvis/audio/out                 → Jarvis → Hoparlör
├── jarvis/voice/emotion             → Duygu profili (charming/sarcastic/intimate)
├── jarvis/face/detected             → Bilinen yüz algılandı
├── jarvis/face/new                  → Yeni yüz algılandı
├── jarvis/context                   → Bağlam (yüz, modül durumu)
├── jarvis/mirror/message            → Magic Mirror sinematik mesaj
├── jarvis/triggers/desk_touch       → TTP223 dokunma
├── jarvis/triggers/desk_touch/gesture → Jest (single/double/long_press)
├── jarvis/intimacy/rhythm           → Ritim verisi
├── jarvis/intimacy/active           → Intimacy modu ON/OFF
├── jarvis/chef/analysis             → Şef analiz sonucu
├── jarvis/chef/warning              → Şef güvenlik uyarısı
├── jarvis/chef/safety_mode          → Güvenlik modu ON/OFF
├── jarvis/lighting/wled             → WLED efekti
├── jarvis/lighting/underbed         → Yatak altı ışık
├── jarvis/audio/preset             → Spatial audio mood
├── jarvis/remote/ir                 → IR komutu
├── jarvis/diffuser/scene            → Difüzör sahnesi
└── jarvis/sensor/presence           → Varlık sensörü
├── jarvis/persona/switch            → Jarvis kişiliği değiştir (default/language_tutor)
├── jarvis/mirror/vocabulary         → Magic Mirror kelime modülü ON/OFF
├── jarvis/chef/safety_mode          → Mutfak güvenlik modu
├── kame/command/move                → Kame32 yürü (dir, steps)
├── kame/command/dance               → Kame32 dans (bpm, beat)
├── kame/command/pose                → Kame32 poz ver (bow/wave/tilt)
├── kame/status/battery              → Kame32 batarya %
├── jarvis/lamp/motion/command       → Lamba (Modül 29) hareket komutu
├── jarvis/lamp/posture/warning      → Lamba postür uyarısı (Tech Neck)
├── openclaw/status/task             → OpenClaw (Modül 27) görev durumu
├── openclaw/approval/request        → OpenClaw onay talebi
├── multicooker/command             → Multicooker (Modül 28) pişirme komutu
├── multicooker/status               → Multicooker pişirme durumu
├── jarvis/chef/ingredients_detected → Modül 13 malzeme tespiti → Mealie eşleştirme
├── jarvis/chef/recipe_suggestion   → Mealie tarif önerisi (besin değerleri ile)
├── jarvis/chef/recipe_approved     → Kullanıcı tarif onayı → pişirme başlat
├── jarvis/lamp/motion/command       → Lamba (Modül 29) fiziksel onay (nod/shake/aim)
└── jarvis/lifeos/nutrition/inject   → OpenClaw Yemeksepeti makro → Modül 16 Life OS
```

### Haberleşme Protokolleri
- **MQTT:** Olay tabanlı, düşük gecikme (<100ms). ESP32 ↔ HA, modüller arası
- **HA REST/WebSocket API:** Cihaz kontrolü, durum sorgulama
- **Webhook:** Harici tetikleyiciler (jarvis_core Python → HA)
- **MiniMax Speech 2.8 Turbo (WebSocket):** Sesten-sese, <300ms gecikme, Voice Cloning
- **Qwen-VL API:** Görüntü analizi (mutfak şefi)

---

## 📁 Klasör Yapısı

```
akilli-evim/
├── README.md                          ← Bu dosya (Proje Anayasası)
├── EQUIPMENT.md                       ← Tüm teçhizat listesi
├── jarvis_core/                       ← Modül 1: Sistemin Beyni (9 dosya)
│   ├── architecture_and_ai_persona.md
│   ├── openai_conversation_agent.yaml
│   ├── master_orchestration_intents.yaml
│   ├── zero_latency_voice_pipeline.py  ← (deprecated — eski mimari)
│   ├── minimax_realtime_orchestrator.py
│   ├── hybrid_brain_and_memory_manager.py
│   ├── facial_memory_and_vector_db.py
│   ├── advanced_system_prompt_v2.md
│   └── autonomous_conversation_trigger.yaml
├── hidden_triggers/                   ← Modül 2: Gizli Tetikleyiciler
│   ├── hardware_and_stealth_psychology.md
│   ├── stealth_button_esphome.yaml
│   └── invisible_orchestration_automations.yaml
├── space_projection/                  ← Modül 3: Derin Uzay Projeksiyonu
│   ├── hardware_and_visual_psychology.md
│   ├── tuya_projector_config.yaml
│   └── celestial_automations.yaml
├── magic_mirror/                      ← Modül 4: Akıllı Ayna
│   ├── hardware_and_glass_crafting.md
│   ├── magicmirror_config.js
│   └── mirror_presence_automation.yaml
├── spatial_audio/                     ← Modül 5: Konumsal Ses
│   ├── hardware_and_acoustic_design.md
│   ├── media_player_integration.yaml
│   └── dynamic_volume_automations.yaml
├── underbed_lighting/                 ← Modül 6: Yatak Altı Aydınlatma
│   ├── hardware_and_radar_tech.md
│   ├── ld2410_bed_radar_esphome.yaml
│   └── night_routing_automations.yaml
├── morning_after/                     ← Modül 7: Ertesi Sabah
│   ├── hardware_and_morning_psychology.md
│   ├── sunrise_simulation.yaml
│   └── morning_orchestration_automation.yaml
├── invisible_remote/                  ← Modül 8: Görünmez Kumanda
│   ├── hardware_and_ir_hacking.md
│   ├── smartir_climate_media.yaml
│   └── stealth_automations.yaml
├── smart_diffuser/                    ← Modül 9: Akıllı Difüzör
│   ├── hardware_and_scent_psychology.md
│   ├── tuya_local_integration.yaml
│   └── diffuser_automations.yaml
├── audio_reactive_wled/               ← Modül 10: Sese Duyarlı WLED
│   ├── hardware_and_wiring.md
│   ├── wled_api_presets.json
│   └── audio_wled_automation.yaml
├── barista_mode/                      ← Modül 11: Kahve Otomasyonu
│   ├── hardware_and_setup.md
│   ├── barista_automation.yaml
│   └── smart_readiness_sensor.yaml
├── intimacy_sync_mode/                ← Modül 12: Duyusal Senkron
│   ├── hardware_and_setup.md
│   ├── bed_sensor_esphome.yaml
│   └── intimacy_automation.yaml
└── vision_chef_assistant/             ← Modül 13: Mutfak Şefi
│   ├── hardware_and_counter_vision.md
│   ├── vision_frame_analyzer.py
│   ├── chef_persona_system_prompt.yaml
│   └── kitchen_automations.yaml
└── immersive_language_tutor/          ← Modül 15: Dil Eğitmeni
│   ├── tutor_persona_prompt.yaml
│   ├── study_environment_automation.yaml
│   └── mirror_vocabulary_integration.js
└── holistic_life_os/                 ← Modül 16: Yaşam İşletim Sistemi
│   ├── health_and_calendar_integrations.md
│   ├── biometric_fusion_engine.py
│   ├── routine_and_medical_tracker.yaml
│   └── life_coach_prompt_extension.md
└── hyperion_media_sync/             ← Modül 17: Ekran Senkronizasyonu
│   ├── hardware_and_hyperion_setup.md
│   ├── dynamic_stadium_atmosphere.yaml
│   ├── agentic_media_orchestrator.py
│   └── media_companion_prompt.md
└── life_os_superapp/                ← Modül 18: PWA SuperApp
│   ├── ui_and_pwa_architecture.md
│   ├── superapp_lovelace_dashboard.yaml
│   ├── agi_chat_interface.yaml
│   └── call_routing_automation.yaml
└── call_routing_and_ceo_mode/       ← Modül 19: CEO Çağrı Modu
│   ├── bluetooth_proxy_audio_config.md
│   ├── ceo_call_routing_automation.yaml
│   └── hands_free_interraction_script.yaml
└── magic_mirror_comm_and_grooming/  ← Modül 20: Ayna İletişim + Stil Koçu
│   ├── mirror_comm_hardware_setup.md
│   ├── whatsapp_video_integration_module.py
│   ├── digital_grooming_coach_vision.yaml
│   ├── digital_grooming_coach_module.yaml
│   └── grooming_checklist_mirror_ui.js
└── car_knight_rider_core/          ← Modül 21: Araç Beyni + Giant's Throne
│   ├── car_hardware_and_obd2_architecture.md
│   ├── giants_throne_automation.yaml
│   └── car_android_dashboard_config.yaml
└── car_omniscience_copilot/        ← Modül 22: Gözetmen Copilot + OBD2 Kehanet
│   ├── omniscience_copilot_architecture.md
│   ├── fatigue_and_ergonomic_guard.py
│   ├── predictive_maintenance_obd2.py
│   └── g_force_and_driving_dynamics.yaml
└── car_stealth_and_seduction/      ← Modül 23: Blackout + Seduction + Sci-Fi
│   ├── car_stealth_architecture.md
│   ├── stealth_blackout_protocol.yaml
│   ├── mobile_seduction_suite.yaml
│   └── scifi_soundspace_augmenter.py
└── car_edge_ai_vision/             ← Modül 24: Jetson Nano Edge-AI + ADAS
│   ├── jetson_hardware_and_sdk_setup.md
│   ├── open_adas_installation_script.sh
│   ├── adas_hmi_display_config.py
│   └── adas_home_assistant_bridge.py
└── car_sentry_mode_security/       ← Modül 25: Sentry Mode + Güvenlik
│   ├── sentry_hardware_and_power_architecture.md
│   ├── sentry_motion_trigger_daemon.py
│   ├── telegram_whatsapp_alert_bridge.py
│   └── car_security_home_assistant_integration.yaml
└── jarvis_body_sync_medical/       ← Modül 26: Medikal Kalkan + VSS
    ├── medical_hardware_and_vss_psychology.md
    ├── anti_vss_lighting_protocol.yaml
    ├── posture_and_spinal_guard.py
    └── hypertension_and_recovery_orchestrator.yaml
├── openclaw_digital_sandbox/       ← Modül 27: OpenClaw Dijital Ajan (Zero Trust Sandbox)
│   ├── sandbox_and_security.md
│   ├── digital_physical_sync.yaml
│   ├── vss_screen_shield.py
│   ├── openclaw_recipe_hunter_prompt.md  ← Otonom tarif avcısı sistem prompt'u
│   ├── mealie_recipe_hunter.py           ← Browser MCP + Context7 + Mealie API tarif avı
│   ├── yemeksepeti_macro_injector.py     ← Yemeksepeti sepet → DeepSeek makro → Modül 16 Life OS
│   └── config.yaml
├── multicooker_chef_automation/    ← Modül 28: Mealie + Multicooker Chef
│   ├── hardware_and_local_isolation.md  ← Mealie Docker + Thermomix rakip + Xiaomi/Tuya izolasyon
│   ├── mealie_macro_orchestrator.py     ← Mealie REST API + DeepSeek makro + porsiyon ölçekleme
│   ├── vision_cooker_orchestration.yaml ← Vision-to-Cook kapalı döngü (Qwen-VL → Mealie → Tencere)
│   ├── cooking_notification_automation.yaml ← VSS dostu bildirim + Lamba fiziksel onay
│   └── config.yaml
├── embodied_jarvis_avatar/         ← Modül 29: Embodied Jarvis Avatar (5-DOF Lamba)
│   ├── hardware_and_kinematics.md
│   ├── autonomous_os_setup.md
│   ├── embodied_lamp_driver.py
│   ├── posture_shield_daemon.py
│   ├── posture_shield_automation.yaml
│   ├── DEVICE.md
│   ├── SOUL.md
│   ├── SAFETY.md
│   └── config.yaml
└── desktop_pet_kame/               ← Modül 30: Desktop Pet Kame (8-DOF Quadruped)
    ├── hardware_and_assembly.md
    ├── kame_esp32_firmware.ino
    ├── audio_reactive_dance.yaml
    ├── eye_of_sauron_parking.py
    ├── wingman_greeting_protocol.yaml
    └── config.yaml
```

---

## 🚀 Geliştirme Yol Haritası

1. **Faz 1 — İskelet:** Klasör yapısı + yapılandırma dosyaları ✅
2. **Faz 2 — Modül 12-9:** Ambient Rhythm → Barista → WLED → Diffuser ✅
3. **Faz 3 — Modül 8-6:** Invisible Remote → Morning → Underbed ✅
4. **Faz 4 — Modül 5-3:** Spatial Audio → Magic Mirror → Space Projection ✅
5. **Faz 5 — Modül 2-1:** Hidden Triggers → Jarvis Core ✅
6. **Faz 6 — Core 2.0:** Zero-Latency + Face ID + Memory + Proactive ✅
7. **Faz 7 — Modül 13-20:** Vision Chef → Dil Eğitmeni → Life OS → Hyperion → SuperApp → Stil Koçu ✅
8. **Faz 8 — Modül 21-25:** Araç modülleri (Knight Rider → Omniscience → Stealth → Edge-AI → Sentry) ✅
9. **Faz 9 — Modül 26:** Medikal Kalkan (VSS + Postür + Tansiyon) ✅
10. **Faz 10 — Maliyet Devrimi:** MiniMax Speech 2.8 Turbo + DeepSeek Hybrid Brain + Voice Cloning ✅
11. **Faz 11 — Entegrasyon:** Tüm modüllerin Jarvis ile orkestrasyonu ✅
12. **Faz 12 — Modül 27:** OpenClaw Dijital Ajan (Zero Trust Docker Sandbox + VSS Ekran Kalkanı) ✅
13. **Faz 13 — Modül 28:** Multicooker Chef (Xiaomi/Tuya yerel izolasyon + Vision-Cooker kapalı döngü) ✅
14. **Faz 14 — Modül 29:** Embodied Jarvis Avatar (5-DOF robotik lamba + Autonomous OS + Postür Kalkanı) ✅
15. **Faz 15 — Modül 30:** Desktop Pet Kame (8-DOF quadruped + Audio-Reactive Dans + Eye of Sauron Park + Wingman Karşılama) ✅

---

## ⚙️ Teknoloji Yığını

| Katman | Teknoloji (2026 — Ağustos) |
|---|---|
| Yapay Zeka | **MiniMax Speech 2.8 Turbo** (sesten-sese, voice cloning, <300ms), **DeepSeek V4-Pro** (ağır zeka, kod, özet), **Qwen-VL Max** (görüntü analizi) |
| Ses | MiniMax Voice Cloning (10 sn referans → Jarvis tonu), duygu kontrol (charming/sarcastic/intimate/authoritative) |
| Hafıza | DeepSeek günlük özet → Prompt Caching → MiniMax System Prompt (bedava hafıza) |
| Orkestrasyon | Home Assistant (Docker), Python 3.13, MQTT 5.0, Agentic HA REST API |
| Dijital Ajan | **OpenClaw v2026.4.15** (browser-use + shell + file ops), **browser-use** (Playwright), Docker Zero Trust sandbox (7 katman) |
| Fiziksel Avatar | **Autonomous OS** (autonomous-ai/autonomous-os — edge_body_only), **PCA9685** I2C PWM driver, MG996R + SG90 servo, inverse kinematics |
| Robotik Evcil Hayvan | **Kame32** (ESP32 DevKit V1 + 8× SG90/MG90S), ESP32Servo kütüphanesi, paralelgram mekanizması, F693ZZ rulman |
| Akıllı Mutfak | **Mealie** (açık kaynak tarif yöneticisi, REST API, URL scrape), **Xiaomi Miot Auto** (`miot_local: true`), **Tuya Local**, router `iptables` ile Çin bulutu izolasyonu, DeepSeek sporcu makro orkestrasyonu |
| Ağ | Tailscale VPN, GL-MT3000 (Beryl AX), WiFi 6 |
| Mikrodenetleyici | ESP32/ESP32-S3 (ESPHome 2026), ESP32 DevKit V1 (Kame32 — Arduino IDE) |
| Sensör | LD2410/LD2450 (mmWave radar — varlık/hareket), MPU6050 (ivmeölçer), TTP223 (kapasitif), INMP441 (I2S mic). ⚠️ Kalp atışı/nefes için akıllı saat (Apple Health/Google Fit) veya HLK-LD6002 (60GHz Vital Signs Radar) gerekir. LD2410/LD2450/LD2420/LD6001 kalp/nefes ÖLÇMEZ |
| Kablosuz | Zigbee (Zigbee2MQTT), WiFi 6, IR (Broadlink) |
| Görüntü | OpenCV 2026, MediaPipe Pose (postür analizi), face_recognition, ChromaDB (vektör DB), Hyperion.ng (ekran senk) |
| Medya | Spotify Web API, WLED (Sound Reactive), Tuya, Hyperion (Ambilight) |
| Gömülü | Raspberry Pi Zero 2 W (Magic Mirror), Raspberry Pi 4 (Jarvis Core + Hyperion + Autonomous OS Body), Nvidia Jetson Nano 4GB (Edge-AI ADAS) |
| Sağlık | Apple Health / Google Fit (akıllı saat), CalDAV/Google Calendar, PyPDF2 (kan tahlili), Omron BLE (tansiyon), FL-41 Rose Tint (VSS aydınlatma) |
| VSS Kalkanı | MediaPipe Pose (servikal açı), WLED anti-mavi ışık protokolü, Windows WMI / brightnessctl (ekran parlaklık), Night Light 3400K |
| Maliyet | **~$12-15/ay** (MiniMax ~$10 + DeepSeek ~$2 + Qwen-VL ~$2) |

---

## 📝 Lisans

Bu proje kişisel kullanım için geliştirilmiştir. Tüm API anahtarları ve hassas bilgiler `.env` dosyasında saklanmalıdır. Yüz tanıma verileri LOKAL saklanır (buluta gönderilmez).

---

*Bu README, projenin anayasasıdır. Modüller geliştikçe bu dosya güncellenmektedir.*