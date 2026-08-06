# car_knight_rider_core — Araç Donanımı ve OBD2 Mimarisi

> **Modül 21: Car Knight Rider Core (Mobil Komuta Merkezi)**
> 2005+ bir araca Android Multimedya Ekranı entegre etmek, Home Assistant ile aracı tek bir ekosistem yapmak, OBD2 portu üzerinden arabanın beynine bağlanmak.

---

## 📱 Android Multimedya Ekranı → Home Assistant

### Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Android Multimedya | 9-10" Android Head Unit (2GB RAM) | 1 | ~$150-250 | 2005+ araçlar için universal fit |
| 2 | OBD2 Adaptör | ELM327 Bluetooth/WiFi | 1 | ~$15-25 | Direksiyon altı OBD2 portuna tak |
| 3 | (Opsiyonel) | ESP32 + CAN Bus shield | 1 | ~$20 | Gelişmiş OBD2 okuma için |

### Mimari: Araç ↔ Ev Ekosistemi

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    ARAÇ (Mobil Komuta Merkezi)                │
  │                                                             │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Android Multimedya Ekranı (9-10")                    │  │
  │  │  - HA Companion App (PWA)                             │  │
  │  │  - Tailscale Client (VPS'e tünel)                    │  │
  │  │  - Lovelace Dashboard (Tesla tarzı)                   │  │
  │  │  - Jarvis sesli komut (mikrofon)                     │  │
  │  └──────────────────────┬───────────────────────────────┘  │
  │                         │ Bluetooth/WiFi                    │
  │  ┌──────────────────────┴───────────────────────────────┐  │
  │  │  ELM327 OBD2 Adaptör                                 │  │
  │  │  - Direksiyon altı OBD2 portu                        │  │
  │  │  - Bluetooth → Android ekran                         │  │
  │  │  - Motor RPM, hız, yakıt, sıcaklık, DTC kodları      │  │
  │  └──────────────────────────────────────────────────────┘  │
  │                                                             │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Elektrikli Koltuk + Direksiyon + Dikiz Aynaları     │  │
  │  │  - Koltuk hafıza pozisyonu (CAN Bus / analog)         │  │
  │  │  - "The Giant's Throne" — sürücüye özel ayar          │  │
  │  └──────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
          │ Tailscale VPN (Mobil internet)
          │
  ┌───────┼─────────────────────────────────────────────────────┐
  │       ▼            VPS (Bulut)                               │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Home Assistant (Docker) + jarvis_core 3.0            │  │
  │  │  - Araç sensörleri (OBD2 → MQTT → HA)                 │  │
  │  │  - Ev durumu (oda sıcaklığı, kilitler)                │  │
  │  │  - Jarvis AGI (MiniMax Speech 2.8 Turbo + DeepSeek V4-Pro)                    │  │
  │  └──────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
```

### Android Multimedya → HA Companion App Kurulumu

```
1. Android Multimedya Ekranı'nı araca tak (universal fit, ISO harness)
2. Google Play Store'dan HA Companion App indir
3. HA URL: http://VPS_TAILSCALE_IP:8123 (Tailscale VPN üzerinden)
4. Tailscale Client kur (Android ekranında):
   - Play Store → Tailscale → Login
   - Ev ağı ile aynı Tailscale hesabı
5. HA Companion App → Tailscale IP → HA'a bağlan
6. Araç içi sensörler:
   - sensor.phone_battery (ekran bataryası)
   - sensor.phone_charging (şarj durumu)
   - sensor.bluetooth_connection (aracın BT ağına bağlandı mı)
7. Jarvis sesli komut:
   - Android mikrofon → HA Conversation → MiniMax Speech 2.8 Turbo
   - "Jarvis, evdeki ışıkları kapat" → araçtan evi kontrol
```

### OBD2 → Home Assistant Haberleşmesi

```
1. ELM327 OBD2 adaptörünü direksiyon altı OBD2 portuna tak
2. Android Multimedya → Bluetooth → ELM327 eşleştir
3. Android'de "Torque" veya "Car Scanner" app kur:
   - OBD2 verilerini oku: RPM, hız, yakıt, motor sıcaklığı, DTC
   - Webhook ile HA'a gönder: http://VPS_TAILSCALE_IP:8123/api/webhook/obd2_data
4. HA'da webhook trigger ile sensörler oluştur:
   - sensor.car_rpm → motor devri
   - sensor.car_speed → hız
   - sensor.car_fuel_level → yakıt seviyesi
   - sensor.car_engine_temp → motor sıcaklığı
   - sensor.car_dtc_codes → arıza kodları
5. Alternatif: ESP32 + CAN Bus shield → MQTT → HA (daha gelişmiş)
```

### OBD2 Veri Akışı

```
  ELM327 (OBD2 portu)
       │ Bluetooth
       ▼
  Android Multimedya (Torque/Car Scanner app)
       │ Webhook (Tailscale VPN)
       ▼
  Home Assistant (VPS)
       │
       ├── sensor.car_rpm
       ├── sensor.car_speed
       ├── sensor.car_fuel_level
       ├── sensor.car_engine_temp
       └── sensor.car_dtc_codes
```

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Android Multimedya | 9-10" Head Unit (2GB RAM, Android 10+) | 1 | ~$150-250 | Universal fit, 2005+ araçlar |
| 2 | OBD2 Adaptör | ELM327 Bluetooth | 1 | ~$15-25 | OBD2 portu → Bluetooth |
| 3 | (Opsiyonel) | ESP32 + CAN Bus shield | 1 | ~$20 | Gelişmiş OBD2 (CAN Bus direkt) |
| 4 | (Yazılım) | Torque Pro / Car Scanner | 1 | ~$5 | OBD2 okuma app'i |
| 5 | (Yazılım) | Tailscale (Android) | — | $0 | VPN tüneli |

> **Toplam maliyet: ~$170-275** (Android ekran + OBD2 adaptör)

---

## ✅ Kurulum Kontrol Listesi

- [ ] Android Multimedya Ekranı araca takıldı (ISO harness)
- [ ] Tailscale Client Android'da kurulu → VPS'e bağlanıyor
- [ ] HA Companion App → Tailscale IP → HA'a bağlanıyor
- [ ] ELM327 OBD2 adaptörü takıldı → Bluetooth eşleştirme
- [ ] Torque/Car Scanner app → OBD2 verileri okunuyor
- [ ] Webhook → HA → sensörler oluşturuldu (RPM, hız, yakıt, sıcaklık)
- [ ] `giants_throne_automation.yaml` HA'a yüklendi
- [ ] `car_android_dashboard_config.yaml` HA'a yüklendi
- [ ] Test: Araç BT → koltuk/direksiyon/ayna otomatik ayar
- [ ] Test: Araç içi sıcaklık → klima otomatik
- [ ] Test: Android ekranda ev durumu + araç verileri + Jarvis