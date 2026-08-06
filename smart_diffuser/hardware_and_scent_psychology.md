# smart_diffuser — Donanım ve Koku Psikolojisi Rehberi

> **Modül 9: Smart Diffuser (Akıllı Koku Difüzörü)**
> Odanın fiziksel ambiyansı (ışık ve ses) değiştiğinde, koku profilinin de otomatik olarak eşlik etmesi. Lüks bir otel lobisi veya high-end kulüp hissiyatı için derin, maskülen ve afrodizyak etkili esanslar.

---

## 🌿 Donanım Kurulumu

### Seçenek A: Tuya/SmartLife Uyumlu Akıllı Difüzör (Önerilen)

Tuya ekosistemine bağlı WiFi'li difüzörler, Home Assistant'a **LocalTuya** entegrasyonu ile bulut gecikmesi olmadan bağlanabilir.

| Özellik | Detay |
|---|---|
| **Platform** | Tuya / SmartLife |
| **Bağlantı** | WiFi 2.4GHz (GL-MT3000 ağına bağlanır) |
| **Kontrol Edilen Fonksiyonlar** | Aç/Kapa, Buhar Hızı (Düşük/Yüksek/Sürekli), RGB Işık, Zamanlayıcı |
| **Öneri** | Tuya 300ml veya 500ml kapasiteli ultrasonik difüzör |
| **Fiyat** | ~$20-35 |

#### Kurulum Adımları

1. **Tuya Smart App:** Difüzörü Tuya Smart (veya SmartLife) app'ine ekle
2. **Cloud Access:** Tuya IoT Platform'da (iot.tuya.com) bir proje oluştur ve HA'ya API anahtarı al
3. **LocalTuya:** HA'a LocalTuya entegrasyonunu kur (HACS → Integrations → LocalTuya)
4. **Cihaz Eşleştirme:** Difüzörün local key'ini al ve LocalTuya'ya gir
5. **Entity Eşleme:** Aç/Kapa → switch, Buhar hızı → select, RGB → light entity'lerini tanımla

> Detaylı LocalTuya konfigürasyonu için [`tuya_local_integration.yaml`](tuya_local_integration.yaml) dosyasına bakın.

### Seçenek B: "Dumb" Difüzör + Akıllı Priz (Alternatif)

Tuya uyumlu difüzör bulunamazsa, fiziksel anahtarlı basit bir difüzör + akıllı priz kombinasyonu kullanılabilir.

| Özellik | Detay |
|---|---|
| **Difüzör** | Herhangi bir ultrasonik difüzör (fiziksel ON/OFF anahtarlı) |
| **Akıllı Priz** | Shelly Plug S / Tapo P110 (güç ölçümlü) |
| **Kontrol** | Sadece Aç/Kapa (buhar hızı ayarı yok — sabit) |
| **Kurulum** | Difüzörün güç anahtarı sürekli ON konumda; akıllı priz üzerinden aç/kapa |

> **Dezavantaj:** Buhar hızı (low/high) kontrol edilemez; RGB ışık kapatılamaz (difüzörün kendi ışığı yanar). Bu, premium WLED tasarımını bozar. Mümkünse Seçenek A tercih edilmeli.

---

## 🧠 Koku Psikolojisi: Limbik Sistem ve Esans Seçimi

### Koku ve Beyin: Neden Koku Önemli?

Koku duyusu, beş duyu içinde **hipotalamus ve amigdalaya doğrudan bağlanan** tek duyudur. Diğer duyular (görme, işitme) önce talamus'ta işlenir; koku ise **doğrudan limbik sisteme** gider — yani duygusal hafıza ve içgüdü merkezine.

```
  Görme/İşitme:    Göz/Kulak → Talamus → Beyin kabuğu (korteks) → Duygu
  Koku:            Burun →     → Amigdala + Hipokampus (limbik sistem) → Duygu
                              ↑ Doğrudan bağlantı — filtre yok
```

> Bu, bir kokunun bir anı veya duyguyu **milisaniyeler içinde** tetikleyebildiği anlamına gelir. Misafir odaya girdiğinde, ışık ve müzikten ÖNCE koku algılanır. Koku, "ilk izlenim" silahıdır.

### Esans Profilleri ve Psikolojik Etkileri

#### 🪵 Sandalağacı (Sandalwood)

| Özellik | Detay |
|---|---|
| **Koku Profili** | Sıcak, odunsu, kremamsı, hafif tatlı |
| **Psikolojik Etki** | Topraklayıcı (grounding), sakinleştirici, meditatif |
| **Limbik Etki** | Amigdala üzerinde sakinleştirici etki; kalp atış hızını düşürür |
| **Kullanım** | Lounge, rahatlama, gece modu |
| **Neden Tercih Edildi?** | "Okyanus esintisi" gibi ucuz, sentetik kokular yerine; sandalağacı derin, maskülen ve olgun bir his verir. Misafir, "bir genç odasında" değil, "bir otel lobisinde" olduğunu hisseder |
| **Marka Önerisi** | Monin Sandalwood, Plant Therapy Sandalwood |

#### 🟡 Amber

| Özellik | Detay |
|---|---|
| **Koku Profili** | Sıcak, reçineli, tozlu, hafif vanilyalı |
| **Psikolojik Etki** | Güven, sıcaklık, "ev" hissi; lüks ve zenginlik algısı |
| **Limbik Etki** | Serotonin salınımını artırır; "güvenli alan" hissi yaratır |
| **Kullanım** | Misafir karşılaması, barista modu, genel lounge |
| **Neden Tercih Edildi?** | Amber, parfümeri dünyasında "lüks" ve "zenginlik" ile eşleştirilir. Bir odada amber kokusu, "buraya özen gösterilmiş" mesajı verir |
| **Marka Önerisi** | Monin Amber, Nemat Amber |

#### 🌺 Ylang-Ylang

| Özellik | Detay |
|---|---|
| **Koku Profili** | Çiçeksi, tatlı, egzotik, hafif baharatlı |
| **Psikolojik Etki** | Afrodizyak, duygusal açılım, romantik atmosfer |
| **Limbik Etki** | Endokrin sistemi uyarır; serotonin ve dopamin salınımını artırır |
| **Kullanım** | Intimacy mode, romantik akşam, date vibe |
| **Neden Tercih Edildi?** | Ylang-Ylang, psikolojik bariyerleri azaltır ve romantik ortamlarda "duygusal yakınlık" hissi yaratır. Ucuz çiçek kokularından farklı olarak, derin ve egzotiktir |
| **Marka Önerisi** | Plant Therapy Ylang-Ylang, Monin Ylang-Ylang |

### Esans Karışım Reçeteleri

| Mod | Karışım | Oran | Etki |
|---|---|---|---|
| **Pre-Arrival (Misafir Karşılaması)** | Amber + Sandalağacı | 60% / 40% | Lüks, güven, "otel lobisi" |
| **Date/Lounge Vibe** | Sandalağacı + Ylang-Ylang | 60% / 40% | Sakinleştirici + afrodizyak |
| **Intimacy Mode** | Ylang-Ylang + Sandalağacı | 50% / 50% | Dengeli afrodizyak + topraklayıcı |
| **Barista Mode** | Amber + Vanilya | 70% / 30% | Sıcak, "cafe" hissi |
| **Deep Sleep** | Sandalağacı (tek başına) | 100% | Derin sakinleştirme |

> **Uygulama Notu:** Esansları difüzörün su haznesine 3-5 damla ekle. Karışım için önceden küçük cam şişede harmanla. Her mod için ayrı şişe kullan.

---

## 🚫 Difüzör RGB Işığını Neden Kapalı Tutmamız Gerekiyor?

### Sorun

Çoğu Tuya difüzörün kendi üzerinde bir RGB LED halkası vardır. Bu LED'ler:
- **Ucuz ve göze batıcıdır** — genellikle mavi, yeşil, kırmızı renk döngüsü yapar
- **WLED ambiyans sistemiyle ÇAKIŞIR** — odada iki farklı ışık kaynağı birbiriyle yarışır
- **Premium hissi BOZAR** — WLED'de özenle seçilmiş amber/kırmızı paleti çalışırken, difüzörün üstünde gökkuşağı dönerse tüm atmosfer çöker

### Çözüm

```
  ❌ YANLIŞ: Difüzör RGB açık + WLED amber
  ┌──────────────────────────────────┐
  │  WLED: Amber/Kırmızı (Premium)   │
  │  Difüzör: 🌈 Gökkuşağı (Ucuz)    │  ← Çatışma! Atmosfer bozuldu
  └──────────────────────────────────┘

  ✅ DOĞRU: Difüzör RGB kapalı + WLED amber
  ┌──────────────────────────────────┐
  │  WLED: Amber/Kırmızı (Premium)   │
  │  Difüzör: ⚫ Işık kapalı (Sade)   │  ← Uyum! Atmosfer korunuyor
  └──────────────────────────────────┘
```

### Uygulama

- **LocalTuya entegrasyonunda** difüzörün RGB light entity'sini `light.diffuser_led` olarak tanımla
- **Tüm otomasyonlarda** difüzör açıldığında RGB ışığı KAPAT:
  ```yaml
  - service: light.turn_off
    target:
      entity_id: light.diffuser_led
  ```
- **Eğer difüzör RGB'si kapatılamıyorsa** (bazı modellerde yazılım kapatma yok):
  - Fiziksel olarak difüzörün LED'ini siyah elektrik bandı ile kapat
  - Veya difüzörün üstüne opak bir kapak/silikon kapağı tak

> **Altın Kural:** Odanın TEK ışık kaynağı WLED olmalıdır. Difüzör sadece koku yayar, ışık vermez.

---

## 🎭 Pavlov Koku Taktiği — İmza Parfüm Alt Notaları (Seduction & Dominance)

### "Güzel Koku" Değil — "Senin Kokun"

Sıradan bir difüzör "güzel koku" yayar. Ama Jarvis "güzel" ile yetinmez.
Jarvis, kullanıcının **imza parfümünün alt notalarını** difüzöre yükler.

| Kullanıcının Parfümü | Alt Notalar | Difüzör Esans Karışımı |
|---|---|---|
| **Tom Ford Oud Wood** | Oud (oud/agarwood), sandalağacı, vetiver | Oud esansı + Sandalağacı (50/50) |
| **Dior Sauvage** | Ambroxan, bergamot, lavanta, pepper | Amber + Bergamot + Lavanta (40/30/30) |
| **Creed Aventus** | Pineapple, birch, musk, oakmoss | Ananas esansı + Musk + Meşe yosunu (30/40/30) |
| **Bleu de Chanel** | Ginger, cedar, sandalwood, amber | Zencefil + Sedir + Sandalağacı (30/30/40) |

### Psikolojik Mekanizma — Koku Hafızası ve Pavlov Etkisi

```
  MİSAFİR ODAYA GİRER
       │
       ▼
  DİFÜZÖR: Kullanıcının imza parfümünün alt notalarını yayar
       │
       ▼
  MİSAFİRİN BEYNİ: "Bu koku tanıdık... bu kişinin kokusu"
       │
       ▼
  PAVLOV YANITI: Koku → geçmiş anılar (o kişinin yanında geçirdiği zaman)
       │
       ▼
  SONUÇ: Misafir mekanı "kullanıcının dominasyonu/aurası" altında hisseder
         → Savunma mekanizması düşer
         → Güven duygusu artar
         → "Bu onun alanı, ben burada güvendeyim" hissi
```

### Neden Bu Kritik?

| Faktör | Sıradan Koku | İmza Parfüm Alt Notaları |
|---|---|---|
| **Tanıdıklık** | "Güzel koku" (nötr) | "Bu kişinin kokusu" (kişisel) |
| **Hafıza tetikleme** | Yok | Koku → anı → güven → savunma düşer |
| **Dominasyon** | "Otel lobisi" (nötr alan) | "Onun alanı" (dominasyon) |
| **Pavlov etkisi** | Yok | Koku = o kişi = güven = rahatlama |
| **Sonuç** | Misafir "misafir" hisseder | Misafir "ev sahibinin alanında, güvende" hisseder |

> **Premium İlke:** "Bir odaya girdiğinde, koku seni karşılamalı. Ve o koku, senin kim olduğunu anlatmalı. Misafir, senin kokunu aldığı an, senin alanında olduğunu kabul eder. Bu, kelimelerle kurulamayacak bir dominasyondur."

### Uygulama

1. **Kullanıcının parfümünü belirle:** Tom Ford Oud Wood, Dior Sauvage, Creed Aventus, vb.
2. **Alt notaları analiz et:** Parfümün "dry-down" (kuruma) fazındaki notalar
3. **Difüzör esansını hazırla:** Alt notalara en yakın esans yağı karışımı
4. **Sürekli difüzör:** Bu karışım, odanın "imza kokusu" olur — her modda alt tabaka
5. **Mod bazlı ek:** Intimacy modunda Ylang-Ylang ek, barista modunda vanilya ek — ama alt notalar hep aynı

> **Kritik:** Difüzör esansı, kullanıcının parfümüyle **AYNI ALT NOTALARA** sahip olmalı. Misafir, kullanıcıyla aynı kokuyu aldığında → "bu onun alanı" → savunma düşer → güven → yakınlık.

---

## ✅ Kurulum Kontrol Listesi

- [ ] Tuya uyumlu difüzör satın alındı ve Tuya Smart app'ine eklendi
- [ ] Tuya IoT Platform'da proje oluşturuldu, API anahtarları alındı
- [ ] HA'a LocalTuya entegrasyonu kuruldu (HACS üzerinden)
- [ ] Difüzör LocalTuya'ya eklendi (switch, select, light entity'leri tanımlandı)
- [ ] Difüzör RGB ışığı kapatıldı (yazılım veya fiziksel)
- [ ] Esans yağları stoklandı: Sandalağacı, Amber, Ylang-Ylang
- [ ] Mod bazlı karışım şişeleri hazırlandı
- [ ] `tuya_local_integration.yaml` HA'a yüklendi
- [ ] `diffuser_automations.yaml` HA'a yüklendi
- [ ] GPS zone (zone.home) HA'ta tanımlı ve telefon HA Companion App ile senkronize