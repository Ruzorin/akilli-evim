# invisible_remote — Donanım ve IR Hacking Rehberi

> **Modül 8: Invisible Remote (Görünmez Kumanda)**
> Yurt odasındaki standart klima (AC) ve televizyon/monitör gibi sadece kızılötesi (IR) ile çalışan cihazları Home Assistant'a entegre eder. Plastik kumandalardan kurtulup, sesli komut, NFC ve otomasyon tetiklemesiyle ortamı kontrol eder.

---

## 🎮 Sensory Design: Neden Plastik Kumandalardan Kurtulmalıyız?

### "Görünmez Kumanda" İlkesi

Premium bir odada hiçbir plastik kumanda yoktur. Her şey sesle, jestle veya otomatik olarak çalışır. Bir misafir odaya girdiğinde:

```
  ❌ STANDART ODA (Plastik Kumandalar)        ✅ PREMIUM ODA (Görünmez Kumanda)
  ┌──────────────────────────────┐           ┌──────────────────────────────┐
  │  ┌──────┐  ┌──────┐         │           │                              │
  │  │Klima │  │ TV   │         │           │  "Jarvis, klimayı 22 yap"   │
  │  │Kum.  │  │Kum.  │         │           │                              │
  │  └──────┘  └──────┘         │           │  → Klima sessizce 22°C'ye    │
  │  Masada dağınık plastik     │           │    ayarlanır                 │
  │  kumandalar...              │           │                              │
  │  "Otel odası" değil,        │           │  "Premium teknoloji odası"   │
  │  "öğrenci yurdu" hissi      │           │  "Premium lounge" hissi       │
  └──────────────────────────────┘           └──────────────────────────────┘
```

### Psikolojik Etki

| Faktör | Plastik Kumanda | Görünmez Kumanda |
|---|---|---|
| **Dikkat Dağıtma** | Kumanda aramak = odak kırılması | Sesli komut = akıcı deneyim |
| **Estetik** | Plastik = "ucuz", "öğrenci" | Görünmez = "premium", "otomatik" |
| **Kontrol Hissi** | "Kumandayı bul, tuşa bas" | "Söyle, oluyor" → güç hissi |
| **Misafir Algısı** | "Bir yurt odası" | "Bir otel süiti" |

> **Sensory Design Prensibi:** Bir ortamın "premium" hissettirmesi için, kontrol mekanizmalarının **görünmez** olması gerekir. Misafir, teknolojinin nasıl çalıştığını düşünmemeli; sadece "çalıştığını" deneyimlemelidir.

---

## 📡 Broadlink RM4 Mini — Kurulum ve Konumlandırma

### Neden Broadlink RM4 Mini?

| Özellik | Detay |
|---|---|
| **Tip** | WiFi'li IR blaster (433MHz + 38kHz IR) |
| **Menzil** | 360° IR, ~8 metre menzil |
| **Protokol** | WiFi 2.4GHz (GL-MT3000 ağına bağlanır) |
| **HA Entegrasyonu** | Broadlink resmi entegrasyon + SmartIR custom component |
| **Fiyat** | ~$20 |
| **Avantaj** | Hazır ürün, kablo gerekmez, 360° görüş |

### Konumlandırma

Broadlink RM4 Mini, 360° IR yayıcıya sahiptir. Ancak IR sinyali **cisimler tarafından engellenir** (duvar, mobilya). Doğru konumlandırma:

```
  ┌─────────────────────────────────────────────┐
  │                  ODA ÜST GÖRÜNÜM              │
  │                                              │
  │   ┌──────┐                          ┌──────┐│
  │   │ TV / │                          │Klima ││
  │   │Monitör│                         │(AC)  ││
  │   └──┬───┘                          └──┬───┘│
  │      │                                 │     │
  │      │         ┌─────────┐            │     │
  │      │         │Broadlink│            │     │
  │      │         │RM4 Mini │            │     │
  │      │         │  (IR)   │            │     │
  │      │         └────┬────┘            │     │
  │      │              │                 │     │
  │      └──────────────┴─────────────────┘     │
  │                                              │
  │  RM4 Mini, TV ve Klima arasında,            │
  │  her ikisini de gören bir noktada           │
  └─────────────────────────────────────────────┘
```

### Montaj İpuçları

| Konum | Açıklama |
|---|---|
| **TV altı / üstü** | TV'yi doğrudan görür; klima duvarda yüksekse sinyal ulaşır |
| **Tavan ortası** | En iyi 360° kapsama; ama kablo çekmek gerekir |
| **Kitaplık rafı** | Estetik saklama; TV ve klimayı görecek açıda |
| **Asla kapalı dolap** | IR sinyali kapıdan geçemez! Açık alanda olmalı |

> **Gizlilik:** RM4 Mini siyah ve küçüktür. Kitaplık rafında veya TV arkasında gizlenebilir. Misafir fark etmez.

### Broadlink HA'ya Ekleme

1. Broadlink app'ini telefona yükle
2. RM4 Mini'yi WiFi ağına (GL-MT3000) bağla
3. HA → Settings → Devices → Add → Broadlink
4. Cihaz otomatik keşfedilir
5. `remote.broadlink_rm4_mini` entity'si oluşur

---

## 🔧 Alternatif: ESP32 + IR Verici (ESPHome)

Broadlink yerine ESP32 + IR LED kullanmak isterseniz:

### Donanım

| Bileşen | Model | Pin |
|---|---|---|
| ESP32 | DevKit V1 | — |
| IR LED | 940nm, 5mm, yüksek güç | GPIO 4 (IR LED + 220Ω direnç) |
| IR Alıcı (öğrenme için) | VS1838B | GPIO 14 (opsiyonel) |

### Pin Bağlantısı

```
  ESP32                    IR LED
  ┌──────────┐             ┌──────┐
  │ GPIO 4   ├─[220Ω]─────►│ Anot │  (+)
  │          │             │      │
  │ GND      ├────────────►│ Katot│  (-)
  └──────────┘             └──────┘
```

### ESPHome YAML Özeti

```yaml
esphome:
  name: invisible-remote
  platform: ESP32
  board: esp32dev

wifi:
  ssid: "GL-MT3000"
  password: "YOUR_WIFI_PASSWORD"

mqtt:
  broker: "gl-mt3000.local"
  port: 1883

# IR Transmitter
remote_transmitter:
  pin: GPIO 4
  carrier_duty_percent: 50%

# IR kodlarını MQTT üzerinden çağırma
switch:
  - platform: template
    name: "TV Power"
    turn_on_action:
      - remote_transmitter.transmit_nec:
          transmitter_id: ir_transmitter
          address: 0x20DF
          command: 0x10EF
```

> **Broadlink vs ESP32:** Broadlink hazır ürün, kurulum kolay. ESP32 daha ucuz (~$5) ve daha esnek (özel IR protokolleri için), ama lehim ve ESPHome bilgisi gerektirir. Bu projede Broadlink önerilir.

---

## 📋 IR Kod Öğrenme

Broadlink veya ESP32, cihazların IR kodlarını "öğrenmek" için kullanılır:

1. **Broadlink app:** "Learn" modunda orijinal kumandanın tuşuna bas → Broadlink kodu kaydeder
2. **SmartIR:** Klimanın marka/model kodu hazır veritabanında aranır (öğrenmeye gerek yok)
3. **ESP32:** VS1838B IR alıcı ile orijinal kumandanın kodları okunur

### Klimanın IR Kodları (SmartIR Veritabanı)

SmartIR, 100+ klima markası için hazır IR kod veritabanı içerir:
- Daikin, Mitsubishi, LG, Samsung, Gree, Midea, vb.
- Marka/model seçilerek kodlar otomatik yüklenir
- Sıcaklık, fan hızı, mod (cool/heat/fan) kontrolü sağlanır

### TV/Monitör IR Kodları (Manuel Öğrenme)

TV'ler için IR kodları manuel öğrenilir:
- Power (Aç/Kapa)
- Input/HDMI (Giriş seç)
- Volume Up/Down (Ses)
- Mute (Sessize al)

---

## ✅ Kurulum Kontrol Listesi

- [ ] Broadlink RM4 Mini satın alındı ve WiFi'a (GL-MT3000) bağlandı
- [ ] RM4 Mini, TV ve klimayı görecek konumda monte edildi
- [ ] HA'a Broadlink entegrasyonu eklendi (`remote.broadlink_rm4_mini`)
- [ ] SmartIR custom component HA'a kuruldu (HACS → SmartIR)
- [ ] Klima marka/model kodu SmartIR veritabanından bulundu ve yüklendi
- [ ] `climate.ac_room` entity'si HA'da görünüyor (sıcaklık/fan/mod kontrolü)
- [ ] TV IR kodları Broadlink ile öğrenildi (Power, HDMI, Volume)
- [ ] TV IR kodları HA script'leri olarak kaydedildi
- [ ] `smartir_climate_media.yaml` HA'a yüklendi
- [ ] `stealth_automations.yaml` HA'a yüklendi
- [ ] Plastik kumandalar çekmeceye kaldırıldı (görünmez!)