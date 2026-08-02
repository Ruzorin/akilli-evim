# underbed_lighting — Donanım ve Radar Teknolojisi Rehberi

> **Modül 6: Underbed Lighting (Yatak Altı Akıllı Aydınlatma)**
> Gece uyanıp yataktan çıkıldığında göz almayan yumuşak bir ışıkla zemini aydınlatmak ve odaya "Floating Bed" (Uçan Yatak) illüzyonu vermek. PIR sensörler yerine milimetrik dalga radarı (HLK-LD2410) ile kusursuz varlık algılama.

---

## 🚮 PIR Sensörler Neden Çöpe Atılmalı?

### PIR (Passive Infrared) Sensörlerin Sorunları

PIR sensörler, hareket eden ısı kaynaklarını (insan vücudu) algılar. Teoride basit ve ucuzdur, ama yatak altı aydınlatma için **tamamen yanlış** bir teknolojidir.

| Sorun | Açıklama |
|---|---|
| **Hareketsizken kapanır** | PIR sensör, sürekli hareket gerektirir. Kişi yatağın yanında durduğunda (ayakta, hareketsiz) sensör "hareket yok" diye ışığı kapatır → kişi karanlıkta kalır |
| **Yatakta dönmeyi algılar** | PIR sensör yatak içindeki hareketi (dönme, nefes) algılayabilir → gece yatakta döndüğünüzde yatak altı ışık yanar → uykuyu böler |
| **Sıcaklık bağımlı** | Yazın oda sıcakken (vücut sıcaklığı ile ortam arasındaki fark azalınca) PIR sensör hassasiyeti düşer → algılamaz |
| **Ölü bölge** | PIR sensörün görüş açısı dışındaki bölgelerde algılama yapmaz → yatağın köşesindeki sensör diğer köşeyi göremez |
| **Gecikmeli** | PIR sensörün tepki süresi 1-3 saniye → kişi yataktan çıkar, 2 saniye karanlıkta kalır, sonra ışık yanar |

### HLK-LD2410 mmWave Radar: Neden Kusursuz?

HLK-LD2410, **milimetrik dalga (24GHz) radar** sensörüdür. Isı değil, **micromotion** (mikro hareket) ve **varlık (presence)** algılar.

| Özellik | PIR Sensör | HLK-LD2410 mmWave |
|---|---|---|
| **Algılama Tipi** | Isı değişimi (infrared) | Radar dalgası (24GHz) |
| **Hareketsiz Varlık** | ❌ Algılamaz | ✅ Algılar (nefes, kalp atışı) |
| **Mesafe Algılama** | ❌ Yok (sadece var/yok) | ✅ 0-6 metre, Gate bazında |
| **Sıcaklık Etkisi** | ❌ Yazın hassasiyet düşer | ✅ Sıcaklıktan etkilenmez |
| **Tepki Süresi** | 1-3 saniye | <100ms |
| **Duvar/Şilte Geçişi** | ❌ Görüş hattı gerekir | ✅ İnce duvar/şilte geçer |
| **Fiyat** | ~$2 | ~$5 |

> **Kritik Fark:** LD2410, **mesafe bazlı (Gate) algılama** yapar. Bu, "1 metrede hareket var" veya "3 metrede hareket var" gibi bölgesel tespit sağlar. Bu özellik, yatak içini (uzak) görmezden gelip sadece yatak yanını (yakın) algılamamızı sağlar — bu modülün temel mantığı.

---

## 💡 COB LED vs WS2812B: Estetik ve Psikolojik Önem

### Sorun: Noktasal WS2812B LED'ler

WS2812B LED'ler **noktasal ışık kaynaklarıdır**. Her LED ayrı ayrı görülür. Yatak altında kullanıldığında:

```
  ❌ WS2812B (Noktasal LED)
  ┌──────────────────────────────────┐
  │  ●  ●  ●  ●  ●  ●  ●  ●  ●  ●  │  ← Her LED ayrı görülür
  │  ●  ●  ●  ●  ●  ●  ●  ●  ●  ●  │     "Disco" / "oyuncu" hissi
  └──────────────────────────────────┘     Zeminde nokta nokta ışık
                                           Premium değil, ucuz
```

### Çözüm: COB (Chip-on-Board) LED

COB LED'ler, birden fazla LED çipini tek bir yüzeyde birleştirir ve **sürekli, pürüzsüz bir ışık çizgisi** yayar.

```
  ✅ COB LED (Pürüzsüz Işık)
  ┌──────────────────────────────────┐
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ← Tek sürekli ışık çizgisi
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │     "Floating bed" hissi
  └──────────────────────────────────┘     Zeminde homojen ışık
                                           Premium, lüks otel hissi
```

### "Floating Bed" (Uçan Yatak) İllüzyonu

COB LED'ler yatak altına, yatak kenarına paralel monte edilirse, ışık zemine **homojen olarak** yansır. Yatağın altı aydınlanır ama yatak kenarı gölgede kalır → yatak **havada duruyormuş** gibi görünür.

```
  ┌─────────────────────────────────────┐
  │              YATAK                   │
  │  ╔═══════════════════════════════╗   │
  │  ║         MATTRESS (Şilte)       ║   │
  │  ╚═══════════════════════════════╝   │
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ← COB LED (yatak altı)
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
  │                                       │
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ← Zemine yansıyan ışık
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │     (homojen, pürüzsüz)
  │  ─────────────────────────────────  │  ← Zemin
  └─────────────────────────────────────┘

  Yatak kenarı gölgede → yatak "havada duruyor" gibi görünür
  = "Floating Bed" illüzyonu = Premium otel hissi
```

### COB LED Seçimi

| Özellik | Detay |
|---|---|
| **Tip** | COB LED şerit (12V veya 24V) |
| **Renk** | Sıcak beyaz (2700K-3000K) — gece için ideal, melatonin bozmaz |
| **Uzunluk** | Yatak çevresi ölçüsü (genelde 2-3 metre) |
| **Güç** | ~10W/metre |
| **Difüzör** | Silikon difüzör tüp içinde — LED çipleri görünmesin |
| **Montaj** | Yatak tabanının altına, kenara paralel, silikon difüzör içinde |

> **Alternatif:** WS2812B kullanılacaksa, **alüminyum difüzör profil + mat akrilik** ile noktalar gizlenir. Ama COB LED bu iş için doğal olarak daha uygundur.

---

## 🔌 HLK-LD2410 → ESP32 Pin Bağlantı Şeması

LD2410, ESP32 ile **UART (Serial)** üzerinden haberleşir.

### Pin Bağlantı Tablosu

| LD2410 Pin | ESP32 Pin | İşlev | Açıklama |
|---|---|---|---|
| **VCC** | **5V** | Güç | ⚠️ LD2410 5V ile çalışır (3.3V değil!) |
| **GND** | **GND** | Toprak | Ortak referans |
| **TX** | **GPIO 16 (RX2)** | LD2410 → ESP32 | Radar verisi → ESP32 (UART2 RX) |
| **RX** | **GPIO 17 (TX2)** | ESP32 → LD2410 | ESP32 → Radar (konfigürasyon komutları) |

### Bağlantı Diyagramı

```
  ESP32 DevKit V1              HLK-LD2410 Modülü
  ┌──────────────┐             ┌──────────────┐
  │              │             │              │
  │  5V          ├────────────►│  VCC         │  (Güç — 5V!)
  │              │             │              │
  │  GND         ├────────────►│  GND         │  (Toprak)
  │              │             │              │
  │  GPIO 16     ├◄────────────┤  TX          │  (Radar → ESP32)
  │  (UART2 RX) │             │              │
  │              │             │              │
  │  GPIO 17     ├────────────►│  RX          │  (ESP32 → Radar)
  │  (UART2 TX) │             │              │
  │              │             │              │
  └──────────────┘             └──────────────┘
```

### ⚠️ Önemli Uyarılar

- **VCC = 5V:** LD2410 modülü 5V gerektirir. ESP32'nin 5V pin'i (VIN) kullanılır. 3.3V verilirse sensör çalışmaz.
- **UART2:** ESP32'nin UART2 pin'leri GPIO 16 (RX) ve GPIO 17 (TX)'dir. UART0 (GPIO 1/3) USB log için kullanılır, UART1 ise bazı ESP32 board'larda flash ile çakışır. UART2 en güvenli seçim.
- **Anten Yönü:** LD2410'un anteni modülün bir yüzündedir. Anten yüzü **algılamak istenen yöne** bakmalıdır. Yatak altına monte edilirken anten yere (zemin yönüne) bakmalı.

### Montaj Konumu

```
  ┌─────────────────────────────────────────────┐
  │                  YATAK ÜST GÖRÜNÜM           │
  │                                             │
  │  ┌───────────────────────────────────────┐ │
  │  │           Yatak (Mattress)             │ │
  │  │                                        │ │
  │  │         ┌──────────────┐              │ │
  │  │         │  LD2410       │              │ │  ← Yatak altı, kenara
  │  │         │  (Anten ↓)    │              │ │     yakın, anten zemine
  │  │         └──────────────┘              │ │     bakar
  │  │                                        │ │
  │  └───────────────────────────────────────┘ │
  │                                             │
  │  Sensör yatak kenarına yakın, zemine bakar │
  │  → Yatak yanında (0-1m) hareket algılar    │
  │  → Yatak içi (1.5-3m) hareketi görmezden   │
  └─────────────────────────────────────────────┘
```

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | UART2 desteği |
| 2 | Radar Sensör | HLK-LD2410B | 1 | 24GHz mmWave, mesafe algılama |
| 3 | LED Şerit | COB LED (12V, sıcak beyaz) | 2-3m | Pürüzsüz ışık için |
| 4 | LED Sürücü | MOSFET modülü (IRLZ44N) | 1 | ESP32 PWM → COB LED sürme |
| 5 | Güç Kaynağı | 12V 2A | 1 | COB LED için |
| 6 | Difüzör | Silikon tüp | LED boyu | LED çiplerini gizle |
| 7 | Jumper Wire | Dişi-Dişi | 4 | LD2410 → ESP32 |

---

## ✅ Kurulum Kontrol Listesi

- [ ] HLK-LD2410B radar sensörü satın alındı
- [ ] LD2410 ESP32'ye bağlandı (VCC→5V, GND→GND, TX→GPIO16, RX→GPIO17)
- [ ] Anten yönü zemine bakacak şekilde monte edildi
- [ ] COB LED şerit (sıcak beyaz, 2700K) satın alındı
- [ ] COB LED silikon difüzör tüp içine yerleştirildi
- [ ] COB LED yatak altına, kenara paralel monte edildi
- [ ] MOSFET modülü ESP32'ye bağlandı (PWM pin → MOSFET gate)
- [ ] `ld2410_bed_radar_esphome.yaml` ESP32'ye yüklendi
- [ ] LD2410 Gate ayarları kalibre edildi (Gate 0-2 = yatak yanı, Gate 3+ = yatak içi)
- [ ] HA'da `binary_sensor.bed_feet_presence` sensörü görünüyor
- [ ] `night_routing_automations.yaml` HA'a yüklendi