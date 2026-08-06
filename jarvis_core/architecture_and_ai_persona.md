# jarvis_core — Mimari ve AI Persona Rehberi

> **Modül 1: Jarvis Core (OpenAI Destekli Ana Beyin)**
> Standart sıkıcı asistanları devreden çıkarıp; OpenAI DeepSeek V4-Pro mantığıyla düşünen, bağlamı anlayan ve MiniMax Voice Cloning üzerinden karizmatik gerçekçi sesle konuşan "Premium Yapay Zeka Uşak" yaratmak.

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
  │  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │    │
  │  │  │ MiniMax Sesten-Sese │  │  MiniMax API  │  │  MiniMax Voice Cloning │  │    │
  │  │  │ (Ses→Metin)  │  │  (DeepSeek V4-Pro)    │  │  (Metin→Ses)    │  │    │
  │  │  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │    │
  │  │         │                │                   │            │    │
  │  │         ▼                ▼                   ▼            │    │
  │  │  ┌──────────────────────────────────────────────────┐    │    │
  │  │  │          JARVIS CORE (Orkestra Şefi)              │    │    │
  │  │  │  - Doğal dil işleme (NLP)                        │    │    │
  │  │  │  - Modül tetikleme (11 modül)                    │    │    │
  │  │  │  - Bağlam anlama (context awareness)             │    │    │
  │  │  │  - Persona (karizmatik uşak)                     │    │    │
  │  │  └──────────────────────────────────────────────────┘    │    │
  │  └──────────────────────────────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────────┘
```

### Bileşen Detayları

| Bileşen | Rol | Konum |
|---|---|---|
| **Mikrofon** | Ses yakalama (gizli, görünmez) | Oda |
| **ESP32-S3 (Audio Hub)** | Mikrofon → MQTT, MQTT → Hoparlör | Oda |
| **GL-MT3000** | Yerel ağ + MQTT broker + Tailscale client | Oda |
| **Tailscale VPN** | Oda ↔ VPS şifreli tünel | Oda ↔ VPS |
| **Home Assistant** | Orkestra şefi, otomasyon motoru | VPS (Docker) |
| **MiniMax Sesten-Sese** | Ses → metin (OpenAI MiniMax Sesten-Sese API) | VPS (HA üzerinden) |
| **OpenAI DeepSeek V4-Pro** | Doğal dil işleme, karar verme | Bulut (MiniMax API) |
| **MiniMax Voice Cloning** | Metin → ses (karizmatik, gerçekçi) | Bulut (MiniMax Voice Cloning API) |

### Sesli Komut Akışı (Latency)

```
  Kullanıcı konuşur → Mikrofon → ESP32-S3 → MQTT → HA (GL-MT3000 → VPS)
  → MiniMax Sesten-Sese (~500ms) → DeepSeek V4-Pro (~1-2sn) → Intent işleme (~100ms)
  → Modül tetikleme (~100ms) → MiniMax Voice Cloning (~500ms) → MQTT → ESP32-S3 → Hoparlör

  Toplam gecikme: ~2-3 saniye (kabul edilebilir — "düşünüp cevap veren" hissi)
```

> **Neden 2-3 saniye kabul edilebilir?** İnsan beyni, "düşünüp cevap veren" bir asistan için 2-3 saniyeyi "doğal" algılar. Anında cevap = "robot"; 2-3 saniye = "düşünen kişi". Jarvis'in "kısa bir duraklama sonra zarif cevap" vermesi → "karizmatik" hissi.

---

## 🎙️ Neden MiniMax Voice Cloning? (TTS Seçimi)

### Robotik Ses vs MiniMax Voice Cloning

| Faktör | HA TTS (Google/AWS) | MiniMax Voice Cloning |
|---|---|---|
| **Ses Kalitesi** | Robotik, sentetik | İnsan gibi, doğal |
| **Duygu** | Düz, monoton | Tonlama, vurgu, duygu |
| **Aksan** | Standart | İngiliz aksanı (premium) |
| **Hissi** | "Asistan" | "Uşak/Butler" |
| **Misafir Algısı** | "Teknoloji" | "İnsan gibi, karizmatik" |
| **Fiyat** | Ücretsiz/ucuz | ~$5/ay (5,000 karakter) |

### Sinematik Etki

```
  ❌ GOOGLE TTS (Robotik)
  "Barista mode activated. Pre-heating the espresso machine."
  → Düz, monoton, "asistan" hissi → "teknoloji"

  ✅ MiniMax Voice Cloning (Karizmatik)
  "Barista mode activated. Pre-heating the espresso machine."
  → İngiliz aksanı, zarif tonlama, hafif gülümseme → "uşak" hissi → "premium"
```

> **Misafir Algısı:** Misafir, robotik bir ses duyduğunda "teknoloji" düşünür. MiniMax Voice Cloning'in insansı sesini duyduğunda "bir kişiyle konuşuyorum" hisseder → "premium" algı. Tony Stark'ın Jarvis'i gibi — robotik değil, karizmatik.

### MiniMax Voice Cloning Kurulum

1. **MiniMax Voice Cloning hesabı:** MiniMax Voice Cloning.io → kayıt ol → API key al
2. **HA entegrasyonu:** HACS → MiniMax Voice Cloning custom component
3. **Ses seçimi:** "Adam" (derin, erkek, İngiliz aksan) veya "Antoni" (zarif, sıcak)
4. **HA configuration:**
   ```yaml
   tts:
     - platform: MiniMax Voice Cloning
       api_key: "YOUR_MiniMax Voice Cloning_API_KEY"
       voice: "Adam"
   ```

---

## 🎤 Mikrofon Konumlandırması — Calm Technology

### "Görünmez Teknoloji" İlkesi

Mikrofon, **asla görünür olmamalıdır**. Misafir, "dinlenildiğini" hissetmemeli — sadece "oda akıllı" hissetmeli.

### Konum Stratejileri

| Konum | Gizlilik | Ses Kalitesi | Öneri |
|---|---|---|---|
| **Tavan lamba içinde** | ✅ Tam gizli | ⚠️ Uzak | İyi |
| **Komodin içinde** | ✅ Gizli | ✅ Yakın | En iyi |
| **Kitaplık rafı** | ✅ Gizli | ✅ İyi | İyi |
| **Duvar paneli arkası** | ✅ Tam gizli | ⚠️ Duvar engeli | Orta |
| **Masada görünür** | ❌ Görünür | ✅ Çok iyi | ASLA |

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

> Tony Stark'ın Jarvis'i bir "asistan" değil, bir "uşak"tır. "Asistan" emir bekler; "uşak" ihtiyacı sezer. "Asistan" konuşur; "uşak" eyleme geçer.

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
| 1 | Audio Hub | ESP32-S3 | 1 | Mikrofon + hoparlör yönetimi |
| 2 | Mikrofon | INMP441 I2S | 1 | Komodin içinde gizli |
| 3 | Hoparlör | 2x Echo Dot (stereo pair) | 1 set | Spatial audio (Modül 5) |
| 4 | API | OpenAI DeepSeek V4-Pro | 1 | Doğal dil işleme |
| 5 | API | MiniMax Voice Cloning | 1 | Karizmatik ses |
| 6 | API | OpenAI MiniMax Sesten-Sese | 1 | STT (ses→metin) |

---

## ✅ Kurulum Kontrol Listesi

- [ ] ESP32-S3 + INMP441 mikrofon komodin içine gizlendi
- [ ] ESP32-S3 MQTT üzerinden HA'a ses verisi gönderiyor
- [ ] HA'a MiniMax Sesten-Sese entegrasyonu eklendi
- [ ] HA'a Extended OpenAI Conversation entegrasyonu eklendi
- [ ] OpenAI DeepSeek V4-Pro API anahtarı HA'a girildi
- [ ] HA'a MiniMax Voice Cloning entegrasyonu eklendi
- [ ] MiniMax Voice Cloning sesi "Adam" (veya tercih edilen) olarak ayarlandı
- [ ] `openai_conversation_agent.yaml` HA'a yüklendi (system prompt ile)
- [ ] `master_orchestration_intents.yaml` HA'a yüklendi
- [ ] Test: "Jarvis" de → "Anlaşıldı efendim" cevabı (MiniMax Voice Cloning sesiyle)
- [ ] Test: "Misafirimizi ağırlayalım" → barista + diffuser tetiklenir
- [ ] Test: "Modumuzu değiştir" → audio reactive + spatial audio tetiklenir