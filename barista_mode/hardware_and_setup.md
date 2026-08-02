# barista_mode — Donanım ve Kurulum Rehberi

> **Modül 11: Barista Mode**
> Odaya misafirle girildiğinde veya ertesi sabah uyandığında, masanın altına gizlenmiş NFC etiketine telefon dokundurularak kahve makinesinin otomatik ısınmaya başlaması, ortamın "Lounge/Cafe" konseptine geçmesi ve makine hazır olduğunda sesli bildirim alınması.

---

## ☕ Kahve Makinesi Seçimi: Fiziksel Anahtarlı vs. Dijital

### Senaryo A: Fiziksel Anahtarlı Makineler (Önerilen)

Çoğu giriş-orta seviye espresso/kapsül makinesi (DeLonghi, Krups, Wacaco vb.) **fiziksel bir güç anahtarına** sahiptir. Makine fişe takılı olsa bile, anahtar "OFF" konumundayken ısınmaz.

| Özellik | Detay |
|---|---|
| **Çözüm** | Akıllı priz (smart plug) + makinenin güç anahtarı sürekli "ON" konumunda bırakılır |
| **Avantaj** | En basit ve güvenilir yöntem. Akıllı priz açıldığında makine doğrudan ısınmaya başlar |
| **Dezavantaj** | Makinenin güç düğmesi her zaman açık bırakılmalı; bazı makinelerde bu güvenlik riski (kuru ısınma) |
| **Uygun Makineler** | DeLonghi Dedica, Krups Essenza, Wacaco Picopresso (ısıtıcı modülü harici) |

### Senaryo B: Dijital / Dokunmatik Anahtarlı Makineler

Bazı modern makineler (Sage, Breville, Gaggia Classic Pro) **dokunmatik veya elektronik güç düğmesi** kullanır. Gücü kesip geri verdiğinizde makine otomatik açılmaz — düğmeye fiziksel basmak gerekir.

| Özellik | Detay |
|---|---|
| **Çözüm** | SwitchBot Fingerbot (veya benzeri mekanik parmak) — akıllı priz yerine/farkında makinenin güç düğmesine monte edilir |
| **Avantaj** | Makine güvenli şekilde kapanır; Fingerbot sadece gerektiğinde düğmeye basar |
| **Dezavantaj** | Ek donanım (Fingerbot ~$15), montaj hassasiyeti gerektirir |
| **Uygun Makineler** | Sage Barista Express, Breville Bambino, Gaggia Classic Pro |

### Senaryo C: Hibrit Yaklaşım (Premium)

Hem akıllı priz hem Fingerbot birlikte kullanılır:
- Akıllı priz: Güç izleme (Watt ölçümü) için
- Fingerbot: Dijital düğmeye basmak için
- Makine her zaman fişe takılı, güç anahtarı OFF, Fingerbot düğmeye basar, priz gücü kesmez

---

## 🔌 Neden Güç Ölçüm (Power Monitoring) Özellikli Akıllı Priz?

Bu modülün en kritik bileşeni, **güç tüketimini Watt cinsinden ölçebilen** bir akıllı prizdir. Standart akıllı prizler sadece ON/OFF yapabilir; güç ölçüm özelliği olmayan prizler bu modülde işe yaramaz.

### Güç Ölçümün Önemi

```
  Kahve Makinesi Güç Profili (Tipik Espresso Makinesi)
  ─────────────────────────────────────────────────────
  │
  │  1400W ┤      ╭───╮  ← Su ısınıyor (rezistans aktif)
  │        │     ╭╯   ╰╮
  │  1000W ┤    ╭╯     ╰╮
  │        │   ╭╯       ╰─── ← Termostat döngüsü (aç/kapa)
  │   500W ┤  ╭╯
  │        │ ╭╯
  │    10W ┤─╯  ← Bekleme (standby) — su hazır, rezistans kapalı
  │        │
  └────────┴──────────────────────────────────────────► Zaman
           Açma   Isınma    Hazır!   Bekleme
```

| Aşama | Güç Tüketimi | Anlamı |
|---|---|---|
| **Açılış** | 0W → 1000W+ | Priz açıldı, makine ısınmaya başladı |
| **Isınma** | 1000W-1400W | Rezistans suyu ısıtıyor (thermostat açık) |
| **Hazır** | 5W-20W | Su kaynadı, termostat kapandı, bekleme moduna geçti |
| **Brew** | 1000W+ (kısa) | Kahve yapımında pompa + rezistans çalışır |

**Güç ölçüm olmadan:** Prizi açarız ama suyun ne zaman kaynadığını bilemeyiz. Kullanıcı soğuk suyla kahve yapmaya çalışır.

**Güç ölçüm ile:** Watt değerini izleyerek suyun kaynadığı anı tespit ederiz ve Jarvis "kahveniz hazır" der.

### Önerilen Akıllı Prizler (Güç Ölçümlü)

| Model | Protokol | Güç Ölçüm | Fiyat Aralığı |
|---|---|---|---|
| **Shelly Plug S** | WiFi (MQTT) | ✅ (0.1W hassasiyet) | ~$15 |
| **Tapo TP-Link P110** | WiFi (HA entegrasyon) | ✅ | ~$15 |
| **Sonoff S31** | WiFi (Tasmota) | ✅ | ~$12 |
| **Zigbee akıllı priz** | Zigbee (Z2M) | ✅ (model bağımlı) | ~$20 |

> **Öneri:** Shelly Plug S — doğrudan MQTT yayınlar, HA'a ek entegrasyon gerektirmez, 0.1W hassasiyetle güç ölçer.

---

## 🏺 Premium Materyal Tavsiyeleri (Hospitality Atmosferi)

Bu modül sadece kahve ısıtmakla kalmaz, **misafirde premium bir otel/cafe deneyimi** yaratır. Sunum ve materyal kalitesi bu hissi belirler.

### Çift Cidarlı Estetik Fincanlar

| Özellik | Detay |
|---|---|
| **Neden Çift Cidarlı?** | İç cidar sıcaklığı korur, dış cidar ele sıcak gelmez. Misafir fincanı tuttuğunda konfor hisseder |
| **Malzeme** | Porselen (seramik değil — porselen daha ince ve ısıyı daha iyi izole eder) |
| **Tasarım** | Mat dış yüzey (premium his), parlak iç yüzey (kolay temizlik) |
| **Öneri** | IKEA FÄRGRIK (ekonomik) veya Villeroy & Boch (premium) |
| **Renk** | Krem/Beyaz — kahve rengini ön plana çıkarır |

### Şuruplar ve Tatlandırıcılar

| Şurup | Marka Önerisi | Kullanım |
|---|---|---|
| **Vanilya** | Monin Vanilla Syrup | 1-2 pompalık doz — tatlı ve kremamsı |
| **Karamel** | Monin Caramel Syrup | 1 pompa — kahve ile zengin tat |
| **Tarçın** | Toz tarçın (şurup değil) | Fincan üstüne serpme — aromatik |

> **Neden Monin?** Monin, dünya çapında barista ve barlarda kullanılan profesyonel şurup markasıdır. Misafir, şişeyi gördüğünde "bu bir otel odası değil, bir cafe" hisseder.

### Kahve Seçimi

| Tip | Öneri | Neden |
|---|---|---|
| **Kapsül** | Nespresso Original (Arpeggio, Ristretto) | Hızlı, tutarlı, temiz — misafir için ideal |
| **Çekirdek** | Illy Classico (orta kavrum) | Premium marka, dengeli tat; öğütücü gerektirir |
| **Hazır Öğütülmüş** | Lavazza Qualita Oro | Öğütücü yoksa en iyi alternatif |

> **Hospitality İpucu:** Kapsül kahve makineleri misafir odaları için en pratiktir — öğütme, ayar, temizlik gerektirmez. Misafir tek dokunuşla kahve alır.

### Sunum Tepsisi

- **Malzeme:** Bambu veya ceviz ahşap (plastik değil!)
- **İçerik:** Fincan, şurup şişesi, küçük tarçın tüpü, kaşık, peçete
- **Konum:** Kahve masasının üstünde, NFC etiketinin yanında

---

## 📱 NFC Etiketi Kurulumu (NTAG215)

### Neden NTAG215?

| Özellik | Detay |
|---|---|
| **Tip** | NTAG215 — 504 byte hafıza |
| **Uyumluluk** | iOS ve Android'de NFC okuma desteği |
| **Amiibo Uyumu** | NTAG215, Amiibo etiketleri için kullanılan tiptir — geniş uyumluluk |
| **Fiyat** | ~$0.30/etiket (10'lu paket ~$3) |
| **Alternatif** | NTAG213 (144 byte — daha küçük, daha ucuz, bizim için yeterli) |

> **Not:** NTAG213 de iş görür; biz sadece bir URL yazacağız, 144 byte fazlasıyla yeterli. NTAG215 daha geniş uyumluluk için tercih edilir.

### Adım Adım Kurulum

#### Adım 1: NFC Etiketini Yazma

**Yöntem A: HA Companion App (Önerilen — iOS/Android)**

1. **Home Assistant Companion App**'i telefona yükle
2. App'te **Settings → NFC Tags** menüsüne gir
3. **"Write NFC Tag"** butonuna bas
4. Etiketin bir adı ver: `nfc_coffee_table`
5. Etiketi telefonun arkasına temas ettir
6. Yazma tamamlandığında "Tag written" mesajı görünür

**Yöntem B: NFC Tools App (Alternatif)**

1. **NFC Tools** (iOS/Android) app'ini yükle
2. **Write** sekmesine geç
3. **Custom URL/URI** seçeneğini seç
4. URL gir: `homeassistant://nfc/1d4a7b8c-coffee-table` (benzersiz ID)
5. Etiketi telefona temas ettir ve yaz

#### Adım 2: Home Assistant'ta NFC Etiketini Tanıma

1. HA Companion App'te **Settings → NFC Tags → Read** 
2. Etiketi telefona okut
3. HA otomatik olarak etiketi tanır ve bir **tag ID** atar
4. Etiket adını `nfc_coffee_table` olarak ayarla
5. Bu etiket artık HA otomasyonlarında trigger olarak kullanılabilir

#### Adım 3: Etiketin Fiziksel Yerleştirilmesi

```
  ┌─────────────────────────────────────────┐
  │              KAHVE MASASI                │
  │                                         │
  │   ┌─────────┐    ┌─────────────────┐    │
  │   │ Fincan  │    │ Şurup & Tarçın  │    │
  │   └─────────┘    └─────────────────┘    │
  │                                         │
  │         ┌───────────────────┐          │
  │         │   NFC ETİKETİ     │          │  ← Masanın alt yüzeyine
  │         │   (NTAG215)       │          │     yapıştırılmış
  │         └───────────────────┘          │
  │  ─────────────────────────────────────  │  ← Masa altı
  │         ▲                               │
  │         │ Telefon buraya dokundurulur   │
  └─────────────────────────────────────────┘
```

- **Konum:** Masanın **alt yüzeyine**, ortada, erişilebilir bir noktaya
- **Neden alt yüzey?** Etiket görünmez kalır — masanın üstünde yapışkan bir etiket premium hissi bozar. Misafir telefonu masanın altına dokundurur → "sihirli" bir deneyim
- **Montaj:** Çift taraflı bant (3M VHB) veya epoksi
- **İşaretleme:** Masanın üst yüzeyine küçük, estetik bir NFC sembolü (📱 veya kahve fincanı ikonu) yerleştir — misafirin nereye dokunduracağını bilmesi için

#### Adım 4: Test

1. Telefonu masanın altına dokundur
2. HA Companion App NFC okuma bildirimi gösterir
3. `barista_automation.yaml` otomasyonu tetiklenir
4. Kahve makinesi ısınmaya başlar, ışıklar değişir, müzik başlar

---

## ✅ Kurulum Kontrol Listesi

- [ ] Kahve makinesi seçildi (fiziksel anahtarlı veya Fingerbot gerektiren)
- [ ] Güç ölçümlü akıllı priz (Shelly Plug S önerilen) kuruldu ve HA'a entegre edildi
- [ ] `sensor.coffee_machine_power` sensörü HA'da görünüyor ve Watt değerini okuyor
- [ ] Kahve makinesinin güç anahtarı ON konumunda (veya Fingerbot monte edildi)
- [ ] NTAG215 NFC etiketi HA Companion App ile yazıldı (`nfc_coffee_table`)
- [ ] NFC etiketi masanın altına yapıştırıldı
- [ ] Çift cidarlı fincanlar, şuruplar ve kahve stoklandı
- [ ] Sunum tepsisi hazırlandı
- [ ] Spotify'da "Lo-Fi Coffee Shop" veya "Acoustic Jazz" çalma listesi oluşturuldu
- [ ] `barista_automation.yaml` ve `smart_readiness_sensor.yaml` HA'a yüklendi