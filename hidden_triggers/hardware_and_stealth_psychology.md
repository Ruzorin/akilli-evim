# hidden_triggers — Donanım ve Gizlilik Psikolojisi Rehberi

> **Modül 2: Hidden Triggers (Gizli Tetikleyiciler ve Butonlar)**
> Ortamda gözle görünür hiçbir kumanda veya teknolojik cihaz olmadan; masanın altına gizlenmiş kablosuz butonlar, bardak altlığına saklanmış NFC etiketleri veya ahşap masaya dokunarak odanın atmosferini anında değiştirmek. "Effortless Power" (Eforsuz Güç) hissi.

---

## 🎭 Seamless Interaction (Kesintisiz Etkileşim) Neden Kritik?

### Telefonla Oynamanın Ambiyansı Bozması

Misafir ağırlarken, her şeyin "premium" hissettirmesi gerekir. Ama misafir odaya girdiğinde:

```
  ❌ TELEFONLA KONTROL (Ambiyans Bozucu)        ✅ GİZLİ TETİKLEYİCİ (Seamless)
  ┌──────────────────────────────┐             ┌──────────────────────────────┐
  │  "Bir saniye, telefonu açayım"│             │  (Masaya dokun)               │
  │  → Cüzdanı çıkar              │             │  → Işıklar değişir            │
  │  → HA app'ini aç             │             │  → Müzik başlar               │
  │  → Dashboard'u bul           │             │  → Atmosfer değişir            │
  │  → Butona bas                │             │  → "Sihir" hissi               │
  │  → 5-10 saniye bekle         │             │  → "Premium" hissi             │
  │  → "Teknoloji" hissi         │             │                                │
  │  → Ambiyans BOZULDU          │             │                                │
  └──────────────────────────────┘             └──────────────────────────────┘
```

### Sesli Komutun Ambiyansı Bozması

"Jarvis, lounge modunu aç" demek bile bir "komut" gerektirir — misafirin "asistanla konuştuğunu" hissetmesi. Bu, "teknoloji kullanıyorum" hissidir.

Gizli tetikleyicilerde ise **komut yok** — sadece bir dokunuş. Misafir "bir şey yaptığını" fark etmez; sadece "oda değişti" hisseder. Bu, "sihir" hissidir.

| Yöntem | Gecikme | Hissi |
|---|---|---|
| Telefon app | 5-10 sn | "Teknoloji kullanıyorum" |
| Sesli komut | 2-3 sn | "Asistanla konuşuyorum" |
| Gizli buton | <100ms | "Sihir — oda beni hissetti" |
| Kapasitif dokunma | <50ms | "Telepati — masaya dokundum, oda değişti" |

> **Premium İlkesi:** Ne kadar az efor, o kadar premium. Misafir "çaba sarf etmeden" odayı kontrol ederse → "güç" hissi → "premium" hissi.

---

## 🔘 Sonoff/Tuya Zigbee Mini Buton — Gizleme

### Donanım

| Özellik | Detay |
|---|---|
| **Model** | Sonoff ZBMINI / Tuya Zigbee Mini Button |
| **Protokol** | Zigbee (Zigbee2MQTT üzerinden HA'a bağlanır) |
| **Boyut** | ~40mm × 40mm × 15mm (çok küçük) |
| **Pil** | CR2032 (1-2 yıl ömür) |
| **Fiyat** | ~$10-15 |

### Gizleme Konumları

```
  ┌─────────────────────────────────────────────┐
  │                  ODA YAN GÖRÜNÜM               │
  │                                             │
  │  ┌─────────┐                    ┌─────────┐│
  │  │ Komodin  │                    │ Komodin  ││
  │  │  ┌───┐  │                    │  ┌───┐  ││
  │  │  │ 🔘 │  │ ← Yatak başı       │  │ 🔘 │  ││ ← Masa altı
  │  │  │Buton│  │   gizli buton     │  │Buton│  ││   gizli buton
  │  │  └───┘  │                    │  └───┘  ││
  │  └─────────┘                    └─────────┘│
  │                                             │
  │         ┌─────────────────┐                 │
  │         │    YATAK         │                 │
  │         └─────────────────┘                 │
  └─────────────────────────────────────────────┘
```

| Konum | Jest | Aksiyon |
|---|---|---|
| **Yatak başı (komodin arkası)** | Tek tık | Lounge/Date modu |
| **Yatak başı** | Çift tık | Sinema modu |
| **Yatak başı** | Basılı tut | Sistem kapat |
| **Masa altı** | Tek tık | Lounge/Date modu |
| **Masa altı** | Çift tık | Sinema modu |
| **Masa altı** | Basılı tut | Sistem kapat |

### Gizleme Yöntemi

- **Çift taraflı bant (3M VHB):** Butonu komodinin arka yüzeyine veya masa altına yapıştır
- **Magnetik (opsiyonel):** Mıknatıs ile metal yüzeye takılabilir
- **Görünmezlik:** Buton ~15mm kalınlığında → komodin arkasında tamamen gizli

---

## ✨ DIY Sihir: TTP223 Kapasitif Dokunmatik Sensör

### "Ahşabın İçinden Dokunma" Mucizesi

TTP223, bir **kapasitif dokunmatik sensör** modülüdür. İnsan vücudunun elektriksel kapasitansını algılar. En sihirli özelliği: **İnce malzemelerin arkasından dokunmayı algılayabilir.**

```
  ┌─────────────────────────────────────────────┐
  │                  MASA ÜST GÖRÜNÜM              │
  │                                             │
  │         (Görünür bir şey YOK)                │
  │         Sadece ahşap masa yüzeyi             │
  │                                             │
  │         ✋ ← Parmağı ahşaba bas              │
  │                                             │
  ────────────────────────────────────────────────  ← Ahşap masa (5-10mm)
  │         ┌───────────┐                        │
  │         │  TTP223   │ ← Ahşabın ALTINA       │
  │         │  Sensör   │   yapıştırılmış         │
  │         └─────┬─────┘                        │
  │               │                              │
  │         ┌─────┴─────┐                        │
  │         │  ESP32    │ ← Masa altına gizli     │
  │         └───────────┘                        │
  └─────────────────────────────────────────────┘
```

### Nasıl Çalışır?

1. TTP223 sensörü, ahşabın **alt yüzeyine** yapıştırılır (sensör yüzü ahşaba bakar)
2. Ahşabın üst yüzeyine parmak basıldığında:
   - Parmak, ahşabın üzerinden sensöre doğru bir **kapasitans değişimi** yaratır
   - TTP223 bu değişimi algılar → dijital çıkış HIGH
   - ESP32, TTP223'ün sinyal pinini okur → HA'a "dokunma algılandı" gönderir
3. Ahşap **5-10mm** kalınlığında ise sensör hala çalışır (TTP223 ~10mm'ye kadar algılar)

### Kalınlık ve Hassasiyet

| Ahşap Kalınlığı | TTP223 Algılama | Hassasiyet Ayarı |
|---|---|---|
| 2-3mm | ✅ Mükemmel | Varsayılan (düşük threshold) |
| 5-8mm | ✅ İyi | Orta threshold |
| 10-15mm | ⚠️ Zor | Yüksek threshold + sensör anten genişletme |
| 15mm+ | ❌ Algılamaz | Bakır folyo ile alan genişlet |

> **İpucu:** Ahşap 10mm'den kalınsa, TTP223'ün sensör pad'ine bir **bakır folyo şerit** lehimleyin. Bu, algılama alanını genişletir ve daha kalın ahşaptan bile çalışır.

### TTP223 → ESP32 Pin Bağlantısı

| TTP223 Pin | ESP32 Pin | İşlev |
|---|---|---|
| **VCC** | **3.3V** | Güç |
| **GND** | **GND** | Toprak |
| **I/O (Signal)** | **GPIO 4** | Dokunma sinyali (HIGH = dokunuldu) |
| **A0 (Sensör pad)** | — | Bakır folyo ile genişletilebilir (opsiyonel) |

```
  ESP32                    TTP223
  ┌──────────┐             ┌──────────┐
  │  3.3V    ├────────────►│  VCC     │
  │  GND     ├────────────►│  GND     │
  │  GPIO 4  ├◄────────────┤  I/O     │  (HIGH = dokunma)
  └──────────┘             └──────────┘
```

---

## 📱 NFC Bardak Altlığı — Gizli NFC Etiketi

### Konsept

NFC etiketi (NTAG215), **bardak altlığının altına** yapıştırılır. Telefon bardak altına konduğunda NFC okunur → HA otomasyon tetiklenir.

```
  ┌─────────────────────────────────────────────┐
  │                  BARDAK ALTLIĞI               │
  │                                             │
  │         ┌───────────────┐                   │
  │         │   📱 Telefon   │ ← Üzerine koy    │
  │         └───────────────┘                   │
  │  ─────────────────────────────────────────  │  ← Bardak altlığı
  │         ┌───────────────┐                   │
  │         │  NFC NTAG215  │ ← Altına yapıştı  │
  │         └───────────────┘                   │
  └─────────────────────────────────────────────┘
```

| Özellik | Detay |
|---|---|
| **Etiket** | NTAG215 (bardak altlığı altına yapıştı) |
| **Okuma** | Telefon bardak altına konduğunda otomatik okur |
| **HA Tetikleme** | `tag_scanned` event → otomasyon |
| **Kullanım** | Müzik sesini kıs (auto-ducking) — sohbet için |

---

## ⚡ Gecikmesiz Çalışma — Neden Hayati?

### Premium Hissin Temeli: "Anında Tepki"

| Gecikme | Hissi |
|---|---|
| **<100ms** | "Sihir — oda beni hissetti" → Premium |
| **100-500ms** | "Hızlı — ama biraz bekledim" → İyi |
| **500ms-2sn** | "Biraz yavaş" → Orta |
| **2-5sn** | "Bekliyorum" → Telefon app'i gibi |
| **5-10sn** | "Çok yavaş" → Ambiyans bozuldu |

> **Kritik:** Gizli tetikleyiciler **<100ms** gecikmeyle çalışmalıdır. Zigbee buton → Zigbee2MQTT → HA → otomasyon → aksiyon zinciri normalde 200-500ms sürer. Ama bu, insan algısı için "anında" hissedilir. Sesli komut (2-3sn) veya telefon app (5-10sn) ile karşılaştırıldığında → "sihir" hissi.

### Neden Gecikme Premium'u Bozar?

Misafir masaya dokunur → 5 saniye sonra ışıklar değişirse → "teknoloji çalışıyor" hissi. Ama masaya dokunur → **anında** ışıklar değişirse → "oda beni hissetti" hissi → "sihir" → "premium".

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | Zigbee Mini Buton | Sonoff ZBMINI / Tuya | 2 | Yatak başı + masa altı |
| 2 | Kapasitif Sensör | TTP223 | 1 | Ahşap masa altına |
| 3 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | TTP223'ü okur |
| 4 | Bakır folyo (opsiyonel) | 5cm x 5cm | 1 | Kalın ahşap için alan genişletme |
| 5 | NFC Etiket | NTAG215 | 1 | Bardak altlığı altına |
| 6 | Çift taraflı bant | 3M VHB | 1 rulo | Gizleme için |

---

## ✅ Kurulum Kontrol Listesi

- [ ] Sonoff/Tuya Zigbee mini butonlar satın alındı
- [ ] Butonlar Zigbee2MQTT üzerinden HA'a eklendi
- [ ] Buton 1 (yatak başı) komodin arkasına gizlendi
- [ ] Buton 2 (masa altı) masa altına gizlendi
- [ ] TTP223 kapasitif sensör satın alındı
- [ ] TTP223 ahşap masa altına yapıştırıldı (sensör yüzü ahşaba bakar)
- [ ] TTP223 → ESP32 bağlandı (VCC→3.3V, GND→GND, I/O→GPIO4)
- [ ] `stealth_button_esphome.yaml` ESP32'ye yüklendi
- [ ] Hassasiyet (threshold) kalibre edildi (ahşap kalınlığına göre)
- [ ] HA'da `binary_sensor.desk_hidden_touch` sensörü görünüyor
- [ ] NFC NTAG215 etiketi bardak altlığı altına yapıştırıldı
- [ ] NFC etiketi HA Companion App ile tanımlandı
- [ ] `invisible_orchestration_automations.yaml` HA'a yüklendi
- [ ] Test: Masa altı buton tek tık → Lounge modu (<100ms)
- [ ] Test: Ahşaba 2sn bas → Intimacy modu
- [ ] Test: Telefon bardak altına → Müzik kısılır