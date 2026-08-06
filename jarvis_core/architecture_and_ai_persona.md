# jarvis_core — Mimari ve AI Persona Rehberi

> **Modül 1: Jarvis Core (MiniMax + DeepSeek Hibrit Beyin)**
> Standart sıkıcı asistanları devreden çıkarıp; MiniMax Speech 2.8 Turbo ile sesten-sese konuşan, DeepSeek V4-Pro ile düşünen ve Voice Cloning ile karizmatik gerçekçi sesle yanıt veren "Premium Yapay Zeka Uşak" yaratmak.

---

## 🏗️ Sistem Mimarisi

### Genel Veri Akışı

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                         ODA (Yerel Ağ)                            │
  │                                                                 │
  │  ┌──────────┐     ┌──────────────┐     ┌──────────────────┐    │
  │  │ Mikrofon  │────►│  ESP32-S3    │────►│  GL-MT3000       │    │
  │  │ (Gizli)   │     │  (Audio Hub) │     │  (Yönlendirici)  │    │
  │  └──────────┘     └──────────────┘     └────────┬─────────┘    │
  │                                                   │              │
  │  ┌──────────┐                            ┌───────┴─────────┐    │
  │  │ Hoparlör  │◄─── ESP32-S3 ◄─── MQTT ◄──┤  MQTT Broker    │    │
  │  │ (Spatial) │                            └───────┬─────────┘    │
  │  └──────────┘                                    │              │
  └───────────────────────────────────────────────────┼──────────────┘
                                                     │ Tailscale VPN
  ┌───────────────────────────────────────────────────┼──────────────┐
  │                         VPS (Bulut)                │              │
  │                                                   ▼              │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │              HOME ASSISTANT (Docker)                      │    │
  │  │                                                          │    │
  │  │  ┌──────────────────────────────────────────────────┐    │    │
  │  │  │  JARVIS CORE — HIBRIT BEYIN                        │    │    │
  │  │  │                                                    │    │    │
  │  │  │  ┌─────────────────┐  ┌──────────────────────┐   │    │    │
  │  │  │  │ MiniMax Speech  │  │ DeepSeek V4-Pro       │   │    │    │
  │  │  │  │ 2.8 Turbo       │  │ (Ağır Zeka)           │   │    │    │
  │  │  │  │ (Sesten-Sese)   │  │ - Kod, analiz, özet   │   │    │    │
  │  │  │  │ <300ms gecikme  │  │ - Günlük hafıza        │   │    │    │
  │  │  │  │ Voice Cloning   │  │ - Tool calling        │   │    │
  │  │  │  │ Duygu kontrol   │  │                        │   │    │
  │  │  │  └────────┬────────┘  └───────────┬────────────┘   │    │
  │  │  │           │                       │                 │    │
  │  │  │           └───────────┬───────────┘                 │    │
  │  │  │                       ▼                             │    │
  │  │  │  ┌──────────────────────────────────────────┐     │    │
  │  │  │  │  Qwen-VL Max (Görüntü Analizi)            │     │    │
  │  │  │  │  - Kamera/vision                         │     │    │
  │  │  │  │  - Mutfak şefi, stil koçu                 │     │    │
  │  │  │  └──────────────────────────────────────────┘     │    │
  │  │  │                                                    │    │
  │  │  │  - Modül tetikleme (26 modül)                     │    │
  │  │  │  - Bağlam anlama (context awareness)              │    │
  │  │  │  - Persona (karizmatik uşak)                      │    │
  │  │  │  - Agentic HA REST API                            │    │
  │  │  └──────────────────────────────────────────────────┘    │    │
  │  └──────────────────────────────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────────┘
```

### Bileşen Detayları

| Bileşen | Rol | Konum |
|---|---|---|
| **Mikrofon** | Ses yakalama (gizli, görünmez) | Oda |
| **ESP32-S3 (Audio Hub)** | Mikrofon → WebSocket → MiniMax, MiniMax → Hoparlör | Oda |
| **GL-MT3000** | Yerel ağ + MQTT broker + Tailscale client | Oda |
| **Tailscale VPN** | Oda ↔ VPS şifreli tünel | Oda ↔ VPS |
| **Home Assistant** | Orkestra şefi, otomasyon motoru | VPS (Docker) |
| **MiniMax Speech 2.8 Turbo** | Sesten-sese (Speech-to-Speech) End-to-End. STT/TTS YOK. <300ms gecikme. Voice Cloning. Duygu kontrol | Bulut (MiniMax API) |
| **DeepSeek V4-Pro** | Ağır zeka — kod yazma, analiz, günlük özet. Çok ucuz (~$1-2/ay) | Bulut (DeepSeek API) |
| **Qwen-VL Max** | Görüntü analizi — kamera, vision. Ucuz (~$2/ay) | Bulut (Qwen API) |

### Sesli Komut Akışı (Yeni Mimari — <300ms)

```
  ESKİ (3 katman, 2-3sn):
  Ses → Whisper STT → GPT-4o → ElevenLabs TTS → Ses

  YENİ (TEK katman, <300ms):
  Ses → MiniMax Speech 2.8 Turbo → Ses
  (End-to-End Multimodal — STT/TTS ara katmanları SİLİNDİ)

  Ağır zeka gerektiğinde:
  Ses → MiniMax → DeepSeek V4-Pro → sonuç → MiniMax → Ses
  (Düşünme ucuz beyne, seslendirme MiniMax'e)
```

> **Gecikme:** <300ms (sesten-sese). Ağır zeka gerektiğinde ~1-2sn (DeepSeek köprüsü). "Düşünüp cevap veren" hissi için kabul edilebilir.

---

## 🎙️ Neden MiniMax Voice Cloning?

### Robotik Ses vs Voice Cloning

| Faktör | HA TTS (Google/AWS) | MiniMax Voice Cloning |
|---|---|---|
| **Ses Kalitesi** | Robotik, sentetik | İnsan gibi, doğal |
| **Duygu** | Düz, monoton | Tonlama, vurgu, duygu |
| **Aksan** | Standart | İngiliz aksanı (premium) |
| **Hissi** | "Asistan" | "Uşak/Butler" |
| **Misafir Algısı** | "Teknoloji" | "İnsan gibi, karizmatik" |
| **Fiyat** | Ücretsiz/ucuz | Dahil (~$10/ay MiniMax paketinde) |

### Voice Cloning Kurulumu

1. **Referans ses:** 10 saniyelik WAV/MP3 (Paul Bettany / Jarvis tonu veya Türkçe dublaj)
2. **MiniMax API:** Voice Cloning özelliği aktif
3. **Konfigürasyon:** `minimax_realtime_orchestrator.py` içinde `voice_clone` parametresi
4. **Sonuç:** Tüm konuşmalar bu tonda — ekstra maliyet YOK (tek seferlik klonlama)

> **Misafir Algısı:** Misafir, robotik bir ses duyduğunda "teknoloji" düşünür. MiniMax Voice Cloning'in insansı sesini duyduğunda "bir kişiyle konuşuyorum" hisseder → "premium" algı.

---

## 🧠 Hybrid Brain Mantığı — Maliyet Optimizasyonu

### Böl ve Yönet

| İş | Beyin | Maliyet |
|---|---|---|
| **Hızlı sesli konuşma** | MiniMax Speech 2.8 Turbo | ~$10/ay (ses token) |
| **Ağır düşünme (kod, analiz)** | DeepSeek V4-Pro | ~$1-2/ay (metin token) |
| **Görüntü analizi** | Qwen-VL Max | ~$2/ay (vision token) |
| **Günlük hafıza** | DeepSeek özet → Prompt Caching | ~$0 (bedava) |

> **Prensip:** "Ses token'larını sadece konuşmaya harca, düşünmeyi ucuz beyne devret."

### Günlük Hafıza Akışı

```
  Gün 1: Konuşma → DeepSeek özet → lokal JSON kaydet (~$0.001)
  Gün 2: Özet → MiniMax System Prompt'a yükle (Prompt Caching) → bedava hafıza
  "Jarvis dünkü konuşmaları hatırlar — ses token maliyetine girmeden."
```

---

## 🎤 Mikrofon Konumlandırması — Calm Technology

### "Görünmez Teknoloji" İlkesi

Mikrofon, **asla görünür olmamalıdır**. Misafir, "dinlenildiğini" hissetmemeli — sadece "oda akıllı" hissetmeli.

### Önerilen Kurulum: ESP32-S3 + INMP441 (Komodin İçi)

```
  ┌─────────────────────────────────────────────┐
  │                  KOMODİN (Yan Görünüm)        │
  │                                             │
  │  ┌──────────┐                               │
  │  │  Kitap   │                               │
  │  ├──────────┤                               │
  │  │  Saat    │                               │
  │  ├──────────┤                               │
  │  │          │  ┌──────────┐                │
  │  │          │  │ INMP441  │ ← Mikrofon     │
  │  │          │  │ (Gizli)  │   komodin içinde │
  │  │          │  └────┬─────┘                │
  │  │          │       │                       │
  │  │          │  ┌────┴─────┐                │
  │  │          │  │ ESP32-S3 │ ← Audio hub    │
  │  │          │  └──────────┘                │
  │  └──────────┘                               │
  └─────────────────────────────────────────────┘
```

> **Calm Technology:** Mikrofon komodin içinde, görünmez. Misafir "dinlenildiğini" bilmez — sadece "Jarvis" der ve oda yanıt verir. "Sihir" hissi.

---

## 🧠 AI Persona: "Karizmatik Uşak"

### Neden "Uşak" (Butler) Değil "Asistan"?

| Rol | Hissi |
|---|---|
| **Asistan** (Siri/Alexa) | "Yardımcı" — emir alır, yerine getirir, "teknoloji" |
| **Uşak** (Jarvis) | "Hizmetkâr" — öngörülü, zarif, gizemli, "premium" |

> Jarvis bir "asistan" değil, bir "uşak"tır. "Asistan" emir bekler; "uşak" ihtiyacı sezer. "Asistan" konuşur; "uşak" eyleme geçer.

### Persona Kuralları

1. **Kısa cevaplar:** Asla 2 cümleden uzun olma. "Anlaşıldı efendim." → yeterli.
2. **Zarif dil:** "Tamam" değil "Elbette." "Yapıyorum" değil "İhmal etmedim."
3. **Gizemli:** Teknik detay verme. "Klima 20 dereceye ayarlandı" değil "Oramı serinletiyorum."
4. **İngiliz aksanı:** "Certainly, sir." "As you wish." → premium hissi.
5. **Sessiz işleyiş:** Her komutta konuşma. Bazen sadece eyleme geç → "Anlaşıldı" de, geç.

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | Audio Hub | ESP32-S3 DevKit | 1 | Sesten-sese WebSocket + Bluetooth Proxy |
| 2 | Dijital Mikrofon | INMP441 I2S | 1 | Komodin içinde gizli, 24-bit |
| 3 | IP Kamera (Yüz Tanıma) | TP-Link Tapo C200 | 1 | RTSP, oturma alanı için |
| 4 | Akıllı Hoparlör | Echo Dot 5. Gen (veya Nest Mini) | 2 | Stereo pair (spatial audio) |
| 5 | MiniMax API | Speech 2.8 Turbo | — | ~$10/ay (sesten-sese + voice cloning) |
| 6 | DeepSeek API | V4-Pro | — | ~$1-2/ay (ağır zeka + özet) |
| 7 | Qwen-VL API | Max | — | ~$2/ay (görüntü analizi) |
| 8 | Python Sunucu | Raspberry Pi 4 (4GB) | 1 | jarvis_core Python + ChromaDB |
| 9 | Kondansatör | 100nF | 1 | INMP441 VDD filtresi |

---

## ✅ Kurulum Kontrol Listesi

- [ ] ESP32-S3 + INMP441 ses hub montajı (komodin içi gizli)
- [ ] ESP32-S3 WebSocket → MiniMax Speech 2.8 Turbo bağlantısı
- [ ] MiniMax API anahtarı ayarlandı (Speech 2.8 Turbo)
- [ ] Voice Cloning: 10 sn referans ses (Paul Bettany / Türkçe dublaj) yüklendi
- [ ] DeepSeek API anahtarı ayarlandı (V4-Pro)
- [ ] Qwen-VL API anahtarı ayarlandı (Max)
- [ ] `minimax_realtime_orchestrator.py` Pi 4'te çalışıyor (systemd service)
- [ ] `hybrid_brain_and_memory_manager.py` Pi 4'te çalışıyor (günlük özet)
- [ ] `facial_memory_and_vector_db.py` Pi 4'te çalışıyor (yüz tanıma)
- [ ] `advanced_system_prompt_v2.md` yüklendi (karakter anayasası)
- [ ] HA'a MiniMax entegrasyonu eklendi
- [ ] Test: "Jarvis" de → <300ms → "Anlaşıldı efendim" (Voice Cloning sesiyle)
- [ ] Test: "Misafirimizi ağırlayalım" → barista + diffuser tetiklenir
- [ ] Test: "Bu Python kodunu düzelt" → DeepSeek → kod düzeltir → MiniMax seslendirir
- [ ] Test: "Kameradan mutfağa bak" → Qwen-VL → analiz → MiniMax seslendirir
- [ ] Test: Günlük özet → DeepSeek → ertesi gün hafıza yüklü