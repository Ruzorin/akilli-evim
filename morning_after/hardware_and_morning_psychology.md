# morning_after — Donanım ve Sabah Psikolojisi Rehberi

> **Modül 7: Morning After (Ertesi Sabah Premium Uyanış)**
> Şiddetli telefon alarmlarını ortadan kaldırıp; güneş ışığını, yavaşça artan akustik müziği ve kahve kokusunu kullanarak lüks bir tatil köyü deneyimi sunan organik uyanış süreci.

---

## 🌅 Sirkadiyen Ritim ve Kortizol Uyanış Tepkisi

### Neden Sesli Alarm Değil?

İnsan vücudu, milyonlarca yıllık evrim boyunca **güneşin doğuşuna** göre programlanmıştır. Sirkadiyen ritim (biyolojik saat), kortizol hormonunun sabah erken saatlerde kademeli olarak artmasını sağlar — bu, doğal uyanış sürecidir.

```
  DOĞAL UYANIŞ (Kortizol Eğrisi)            TELEFON ALARMI
  ┌──────────────────────────────┐          ┌──────────────────────────────┐
  │                              │          │                              │
  │         ╭────╮               │          │  ┌────╮                      │
  │        ╭╯    ╰╮              │          │  │BİP!│ ← Aniden, şiddetli    │
  │       ╭╯      ╰╮             │          │  └─┬──┘                      │
  │      ╭╯        ╰──           │          │    │                         │
  │     ╭╯                       │          │    ▼ Adrenalin patlaması     │
  │    ╭╯                        │          │      → "Savaş ya da kaç"    │
  │   ╭╯                         │          │      → Kalp atışı fırlar     │
  │  ╭╯                          │          │      → Stres hormonu         │
  │ ╭╯                           │          │                              │
  │╭╯                            │          │  "Korkuyla uyanma"            │
  │╯                             │          │  → Günü stresle başlatma     │
  │                              │          │                              │
  │ "Yavaşça uyanma"             │          │                              │
  │ → Sakin başlangıç            │          │                              │
  │ → İyi his                     │          │                              │
  └──────────────────────────────┘          └──────────────────────────────┘
```

### Kortizol Uyanış Tepkisi (Cortisol Awakening Response - CAR)

| Faktör | Doğal Uyanış | Telefon Alarmı |
|---|---|---|
| **Kortizol Artışı** | Kademeli (30-45 dk) | Aniden (saniyeler içinde) |
| **Uyku Evresi** | REM/Light'tan kademeli çıkış | Derin uykudan aniden çıkış → "Sleep inertia" (sersemlik) |
| **Kalp Atışı** | Yavaş artış | Aniden fırlar (adrenalin) |
| **Ruh Hali** | Sakin, dinç | Stresli, huzursuz |
| **Günün Geri Kalanı** | Enerjik başlangıç | Yorgun, gergin |

> **Bilimsel Gerçek:** Çalışmalar, sesli alarmla uyanan kişilerin gün boyunca daha yüksek stres hormonu seviyesine sahip olduğunu ve sabah sersemliği (sleep inertia) yaşadığını göstermektedir. Işıkla uyanan kişiler ise daha az sersemlik ve daha iyi bilişsel performans gösterir.

### Premium Uyanış Protokolü

Bu modül, doğal gündoğumunu taklit eden 3 aşamalı bir uyanış süreci tasarlar:

1. **Işık (T-10dk):** Koyu kırmızı → turuncu → sıcak beyaz (WLED yapay gündoğumu) + perde %20 aralık
2. **Ses (T-5dk):** Akustik müzik %5'ten %15'e kademeli artış (fade-in audio)
3. **Koku (T-0dk):** Perde %100 + barista_mode tetiklenir → espresso makinesi ısınır → kahve kokusu

> Bu üç duyusal kanal (ışık + ses + koku), misafirin **derin uykudan kademeli olarak** çıkmasını sağlar. Misafir, "bir şey tarafından uyandırıldığını" hissetmez; "doğal olarak uyandığını" hisseder — tatil köyünde güneşin doğuşuyla uyanmak gibi.

---

## 🪟 SwitchBot Curtain / Tuya Perde Motoru — Kurulum

### Donanım Seçimi

| Model | Tip | Fiyat | Avantaj | Dezavantaj |
|---|---|---|---|---|
| **SwitchBot Curtain** | U-rail / Rod | ~$90 | Kurulum kolay, HA entegrasyonu | Sadece belirli perde tipleri |
| **Tuya Perde Motoru** | Rod motor | ~$35 | Ucuz, Tuya/LocalTuya | Kurulum daha teknik |
| **Zigbee Perde Motoru** | Aqara vb. | ~$70 | Zigbee2MQTT, düşük güç | Marka uyumluluğu |

### SwitchBot Curtain — Kornişe Takım

SwitchBot Curtain, mevcut perde rayına (U-rail) veya perde çubuğuna (rod) **kırma-dökme yapmadan** takılır:

```
  ┌─────────────────────────────────────────────┐
  │              PERDE / KORNİŞ                 │
  │                                             │
  │  ┌───────────────────────────────────────┐ │
  │  │           Perde Rayı (U-rail)          │ │
  │  │  ┌─────┐                    ┌─────┐   │ │
  │  │  │Perde│◄─────────────────►│Perde│   │ │
  │  │  └──┬──┘                    └──┬──┘   │ │
  │  │     │                          │      │ │
  │  │  ┌──┴──┐                    ┌──┴──┐  │ │
  │  │  │Switch│                    │Switch│  │ │  ← İki motor (sağ/sol)
  │  │  │Bot 1 │                    │Bot 2 │  │ │     ray'a takılır
  │  │  └─────┘                    └─────┘  │ │
  │  └───────────────────────────────────────┘ │
  │                                             │
  │  SwitchBot Curtain, rayın içine "tırmanır"  │
  │  Vidalama gerekmez — sadece tak ve çalıştır  │
  └─────────────────────────────────────────────┘
```

### Kurulum Adımları

1. **SwitchBot app:** Motoru telefona bağla ve WiFi'ya (GL-MT3000) ekle
2. **HA Entegrasyonu:** SwitchBot resmi HA entegrasyonu veya BLE → MQTT köprüsü
3. **Entity:** `cover.smart_curtain` (aç/kapa, pozisyon %0-100)
4. **Kalibrasyon:** Perde tam açık ve tam kapalı pozisyonlarını kalibre et
5. **Sessiz Mod:** SwitchBot Curtain'in motor sesi ~40dB'dir (fısıltı seviyesi). Uyanış sırasında "sessiz mod" kullanılır → misafir motor sesini duymaz

### Tuya Perde Motoru Alternatifi

Tuya perde motoru, LocalTuya ile HA'a bağlanır (smart_diffuser modülündeki gibi). `cover.tuya_curtain` entity'si oluşur. Daha ucuzdur ama kurulum SwitchBot'tan daha teknik gerektirir.

---

## ☕ Barista Mode Entegrasyonu — Kusursuz Sabah Deneyimi

Bu modül, **Modül 11 (barista_mode)** ile kusursuz bir entegrasyon çalışır:

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    PREMIUM UYANIŞ SÜRECİ                     │
  │                                                             │
  │  [T-10dk]  IŞIK: WLED koyu kırmızı → turuncu → sıcak beyaz │
  │            PERDE: %20 aralık (güneş ışığı sızar)            │
  │                                                             │
  │  [T-5dk]   SES:  Akustik müzik %5 → %15 (fade-in)           │
  │                                                             │
  │  [T-0dk]   PERDE: %100 açık                                 │
  │            BARISTA MODE TETİKLENİR →                         │
  │            ┌─────────────────────────────────┐              │
  │            │ Espresso makinesi prizi açılır   │              │
  │            │ Makine ısınmaya başlar (1000W+)  │              │
  │            │ Oda ışıkları %30 amber (cafe)    │              │
  │            │ Lo-Fi müzik %15 (arka plan)      │              │
  │            │ Difüzör açılır (Amber esansı)    │              │
  │            └─────────────────────────────────┘              │
  │                                                             │
  │  [T+2dk]   JARVIS: "Good morning. Weather is 24 degrees.   │
  │                    Your espresso machine is ready."         │
  │                                                             │
  │  [T+5dk]   KAHVE HAZIR: "Espresso is ready to brew"        │
  │            (barista_mode smart_readiness_sensor)             │
  │                                                             │
  │  Sonuç: Misafir, güne kahve kokusu ve sakin müzikle başlar  │
  │         — telefon alarmı yok, stres yok, premium his        │
  └─────────────────────────────────────────────────────────────┘
```

### Entegrasyon Noktaları

| Zaman | morning_after Aksiyonu | barista_mode Tetiklemesi |
|---|---|---|
| T-0dk | Perde %100 açılır | `input_boolean.barista_mode_active` ON → priz açılır |
| T+2dk | Jarvis TTS anonsu | (barista_mode ısınmaya başlamıştır) |
| T+5dk | (müzik devam eder) | `smart_readiness_sensor` → "Espresso ready" anonsu |

> Bu entegrasyon, misafirin **üç duyusal kanaldan** (ışık + ses + koku) aynı anda uyanmasını sağlar. Her biri kademeli, organik ve stressiz. Misafir, "bir otomasyon tarafından uyandırıldığını" değil, "doğal olarak güne başladığını" hisseder.

---

## ✅ Kurulum Kontrol Listesi

- [ ] SwitchBot Curtain (veya Tuya perde motoru) satın alındı ve kornişe takıldı
- [ ] Perde motoru HA'a entegre edildi (`cover.smart_curtain`)
- [ ] Perde sessiz modda çalışıyor (motor sesi < 45dB)
- [ ] WLED sistemi çalışır durumda (`light.wled_ambient`)
- [ ] Spotify medya oynatıcı HA'a bağlı (`media_player.spotify`)
- [ ] `sunrise_simulation.yaml` HA'a yüklendi (WLED yapay gündoğumu)
- [ ] `morning_orchestration_automation.yaml` HA'a yüklendi
- [ ] barista_mode modülü çalışır durumda (Modül 11)
- [ ] Jarvis TTS çalışıyor (`tts.jarvis_voice`)
- [ ] Hava durumu sensörü HA'a bağlı (`weather.home`)
- [ ] Telefon alarm sensörü veya Jarvis "sabah X'te uyandır" komutu çalışıyor