# intimacy_sync_mode — Donanım ve Kurulum Rehberi

> **Modül 12: Sensory Rhythm**
> Yatak iskeletine gizlenmiş MPU6050 ivmeölçer ile fiziksel ritim algılama ve duyusal ortam senkronizasyonu.

---

## 🧰 Gerekli Donanım Listesi

| # | Bileşen | Model / Tip | Adet | Açıklama |
|---|---|---|---|---|
| 1 | Mikrodenetleyici | ESP32 DevKit V1 | 1 | Ritim algılama beyni; I2C ile MPU6050'ye bağlanır, WiFi üzerinden MQTT/HA ile haberleşir |
| 2 | İvmeölçer / Jiroskop | MPU6050 (6-DoF) | 1 | Yatağın mekanik titreşimlerini 3 eksende (X, Y, Z) algılar |
| 3 | Ambiyans LED | WS2812B LED Şerit | 1 | (Opsiyonel yerel gösterge) Modül çalıştığında durum göstergesi; ana aydınlatma WLED üzerinden ayrı cihazda |
| 4 | Koku Difüzörü | Tuya / Zigbee Akıllı Difüzör | 1 | Esans yağını ultrasonik olarak yayar; HA üzerinden akıllı priz veya doğrudan entegrasyonla kontrol edilir |
| 5 | Esans Yağları | Sandalağacı (Sandalwood) / Ylang-Ylang | 2 | Psikolojik olarak afrodizyak ve rahatlatıcı etki sağlayan koku profilleri |
| 6 | Klima | IR Kontrollü Split Klima | 1 | ESP32 IR blaster (`invisible_remote` modülü) üzerinden kontrol edilir |
| 7 | Hoparlör Sistemi | 2x Bluetooth/WiFi Hoparlör | 1 set | Spotify Connect üzerinden uzamsal ses (stereo ayrım) sağlar |
| 8 | WLED Cihazı | ESP32 + WS2812B (ayrı cihaz) | 1 | Odanın ambiyans aydınlatması; `audio_reactive_wled` modülü ile yönetilir |
| 9 | Güç Kaynağı | 5V 2A USB Adaptör | 1 | ESP32 + MPU6050 beslemesi |
| 10 | Kablo | Jumper Wire (Dişi-Dişi) | 4 | I2C bağlantısı için |

---

## 🔌 Pin Bağlantı Şeması: ESP32 ↔ MPU6050

MPU6050, I2C protokolü üzerinden ESP32 ile haberleşir. Bağlantı son derece basittir — sadece 4 kablo:

```
  ESP32 DevKit V1              MPU6050 Modülü
  ┌──────────────┐             ┌──────────────┐
  │              │             │              │
  │  GPIO 21     ├────────────►│  SDA         │  (I2C Veri Hattı)
  │  (I2C SDA)   │             │              │
  │              │             │              │
  │  GPIO 22     ├────────────►│  SCL         │  (I2C Saat Hattı)
  │  (I2C SCL)   │             │              │
  │              │             │              │
  │  3.3V        ├────────────►│  VCC         │  (Güç — 3.3V!)
  │              │             │              │
  │  GND         ├────────────►│  GND         │  (Toprak)
  │              │             │              │
  └──────────────┘             └──────────────┘
```

### Pin Detayları

| ESP32 Pin | MPU6050 Pin | İşlev | Not |
|---|---|---|---|
| **GPIO 21** | **SDA** | I2C Veri | ESP32'nin varsayılan I2C SDA pin'i |
| **GPIO 22** | **SCL** | I2C Saat | ESP32'nin varsayılan I2C SCL pin'i |
| **3.3V** | **VCC** | Güç | ⚠️ MPU6050 3.3V ile çalışır; 5V verme! |
| **GND** | **GND** | Toprak | Ortak referans noktası |

### ⚠️ Önemli Uyarılar

- **VCC = 3.3V:** Bazı MPU6050 modülleri 5V toleranslı olsa da, ESP32'nin GPIO pinleri 3.3V mantık seviyesindedir. Güvenli taraf için 3.3V kullanın.
- **I2C Adresi:** MPU6050'nin varsayılan I2C adresi `0x68`'dir. ADO pini HIGH yapılırsa `0x69` olur. Biz varsayılan `0x68` kullanıyoruz.
- **Pull-up Dirençleri:** Çoğu MPU6050 breakout board'unda yerleşik 4.7kΩ pull-up dirençleri vardır. Ekstra direnç gerekmez.

---

## 🛏️ Sensör Montajı: Nereye ve Nasıl?

### Yatak Mekaniği ve Titreşim İletimi

Yatak, bir **yaylı sistem**dir. Hareket enerjisi, yatak iskeleti (kirişler) üzerinden matrise iletilir. Sensörün konumu, hangi titreşim frekanslarını en iyi yakalayacağımızı belirler.

### Önerilen Konum: Orta Kiriş (Merkezi Titreşim Noktası)

```
  ┌─────────────────────────────────────────────┐
  │                  YATAK ÜSTÜ                   │
  │  ┌─────────┐         ┌─────────┐             │
  │  │ Yastık  │         │ Yastık  │             │
  │  └─────────┘         └─────────┘             │
  │                                               │
  │              ╔═══════════════╗                │
  │              ║   MATTRESS     ║                │
  │              ║   (Yatak)      ║                │
  │              ╚═══════════════╝                │
  │                                               │
  │  ─────────────────────────────────────────    │  ← Yatak Tabanı
  │         │           │           │             │
  │         │       ┌───┴───┐       │             │
  │         │       │MPU6050│       │             │  ← ORTA KİRİŞ
  │         │       │ESP32  │       │             │     (Önerilen Konum)
  │         │       └───────┘       │             │
  │         │           │           │             │
  │  ─────────────────────────────────────────    │  ← Zemin
  └─────────────────────────────────────────────┘
```

### Neden Orta Kiriş?

| Faktör | Açıklama |
|---|---|
| **Mekanik** | Orta kiriş, yatağın her iki tarafından gelen titreşimlerin doğal olarak birleştiği **nodal nokta**'dır. Bu noktada sinyal/gürültü oranı (SNR) en yüksektir. |
| **Simetri** | İki kişi yatakta olsa bile, orta kiriş her iki kaynaktan da dengeli sinyal alır. Kenara monte edilirse sadece bir taraftaki hareket baskın olur. |
| **Gürültü Filtreleme** | Başlık altı monte edilirse, yastık hareketleri ve nefes alma sinyali ritmik hareketi boğar. Orta kiriş, bu yüksek frekanslı gürültüleri doğal olarak zayıflatır. |
| **Gizlilik** | Orta kiriş, çarşaf altında ve yatak kenarı ile zemin arasındaki boşlukta kaldığı için **görünmez** kalır. Misafirler sensörün varlığını fark etmez. |

### Alternatif Konum: Başlık Altı (Daha Az Önerilen)

- **Avantaj:** Nefes alma ve kalp atışı gibi ince titreşimler algılanabilir.
- **Dezavantaj:** Yastık hareketleri (dönme, yastığı düzeltme) yanlış pozitif tetikler. Ritmik hareket sinyali zayıf iletilir.
- **Kullanım:** Sadece "uyku takibi" yapılacaksa tercih edilmeli; bu modülün amacı (ritmik aktivite) için orta kiriş daha uygundur.

### Montaj Yöntemi

1. **Çift Taraflı Bant (3M VHB):** Sensörü ve ESP32'yi orta kirişin **yan yüzeyine** (yatay değil, dikey) yapıştırın. Dikey montaj, yerçekimi etkisini minimize eder.
2. **Kablo Yönetimi:** I2C kablolarını kiriş boyunca kablo kanalı ile gizleyin. Sallanan kablolar titreşim gürültüsü yaratır.
3. **İzolasyon:** Sensör ile kiriş arasına 1-2mm köpük şerit koyun. Bu, yüksek frekanslı mekanik gürültüyü (yatak yayı tıkırtısı vb.) filtreler ama düşük frekanslı ritmik titreşimi geçirir.
4. **Yön:** MPU6050'nin Z ekseni yukarı bakacak şekilde monte edilmelidir. Bu, yerçekimi vektörünün Z ekseninde sabit kalmasını sağlar ve X/Y eksenindeki ivme değişimleri daha temiz okunur.

---

## 🧪 Psikolojik Etki ve Esans Seçimi

### Sandalağacı (Sandalwood)

- **Etki:** Topraklayıcı (grounding), sakinleştirici, meditatif.
- **Neden:** Sandalağacı kokusu, amigdala üzerinde sakinleştirici etki yapar; kalp atış hızını düşürür. Bu modülde, ritmik aktivite sırasında kullanıcının "aşırı uyarılma" yerine "derin odaklanma" yaşaması hedeflenir.
- **Koku Profili:** Sıcak, odunsu, hafif tatlı.

### Ylang-Ylang

- **Etki:** Afrodizyak, duygusal açılım, romantik atmosfer.
- **Neden:** Ylang-Ylang, endokrin sistemi uyararak serotonin ve dopamin salınımını artırır. Romantik/intim ortamlarda psikolojik bariyerleri azaltır.
- **Koku Profili:** Çiçeksi, tatlı, egzotik.

### Önerilen Karışım

Modül aktif olduğunda difüzör **%60 Sandalağacı + %40 Ylang-Ylang** karışımı çalıştırmalıdır. Bu oran, sakinleştirici ve afrodizyak etkiyi dengeler.

---

## 🔧 Sistem Beslemesi ve Güvenlik

| Konu | Detay |
|---|---|
| **Güç** | ESP32 + MPU6050 toplam çekimi ~50mA'dir. 5V/2A adaptör fazlasıyla yeterli. |
| **Isı** | ESP32 uzun süreli çalıştırmada ısınır. Kirişe monte ederken havalandırma boşluğu bırakın. |
| **Güvenlik** | Sensör yatak altında olduğu için fiziksel darbe almaz. Yine de köpük izolasyon ile mekanik koruma sağlayın. |
| **WiFi Sinyali** | Yatak metal iskeleti WiFi sinyalini zayıflatabilir. ESP32'nin antenini kirişin dışına doğru yönlendirin. |

---

## ✅ Kurulum Kontrol Listesi

- [ ] ESP32'ye ESPHome yüklendi ve WiFi bağlantısı doğrulandı
- [ ] MPU6050 I2C bağlantısı yapıldı (SDA→GPIO21, SCL→GPIO22, VCC→3.3V, GND→GND)
- [ ] Sensör orta kirişe dikey monte edildi (Z ekseni yukarı)
- [ ] Köpük izolasyon uygulandı
- [ ] Kablolar kiriş boyunca sabitlendi (sallanmıyor)
- [ ] Home Assistant'ta ESP32 cihazı göründü ve `activity_level` sensörü oluşturuldu
- [ ] Difüzöre Sandalağacı + Ylang-Ylang esansı dolduruldu
- [ ] WLED cihazı HA'ya entegre edildi
- [ ] Klima IR blaster (`invisible_remote`) çalışır durumda
- [ ] Spotify Connect hoparlörleri HA medya oynatıcı olarak eklendi