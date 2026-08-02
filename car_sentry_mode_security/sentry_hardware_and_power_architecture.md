# car_sentry_mode_security — Sentry Mode Donanım ve Güç Mimarisi

> **Modül 25: Car Sentry Mode Security (Otopark Güvenliği ve Anlık Bildirimler)**
> Araç park halindeyken Jetson Nano'nun düşük güç tüketimli uyku moduna geçmesi, PIR/şok sensör ile hareket algıladığında kameraları uyandırması ve Telegram/WhatsApp üzerinden anlık fotoğraf göndermesi.

---

## 🔋 Akıllı Güç Yönetimi — Aküyü Bitirmeme

### Sorun

Jetson Nano, tam performans modunda ~10W çeker. Araç park halinde 8-12 saat → 80-120W → araç aküsünü bitirebilir.

### Çözüm: Deep Sleep + PIR Wake

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    ARAÇ PARK HALİNDE                          │
  │                                                             │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Jetson Nano — DEEP SLEEP MODE (~0.5W)                │  │
  │  │  - GPU kapalı, CPU minimum, RAM tutulur               │  │
  │  │  - Sadece GPIO interrupt aktif (PIR dinliyor)         │  │
  │  │  - Kamera kapalı, Wi-Fi kapalı, ekran kapalı           │  │
  │  └──────────────────────┬───────────────────────────────┘  │
  │                         │ GPIO interrupt                       │
  │  ┌──────────────────────┴───────────────────────────────┐  │
  │  │  PIR Sensör (HC-SR501 mini) — ~0.05W                  │  │
  │  │  - Araç çevresinde hareket → GPIO HIGH                 │  │
  │  │  - Jetson Nano'yu milisaniyeler içinde uyandırır       │  │
  │  └──────────────────────────────────────────────────────┘  │
  │                                                             │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Şok/İvme Sensör (MPU6050) — ~0.01W                   │  │
  │  │  - Darbe/sarsıntı → interrupt → Jetson uyanır         │  │
  │  └──────────────────────────────────────────────────────┘  │
  │                                                             │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  Akıllı Röle — Araç aküsü koruma                      │  │
  │  │  - Akü voltajı <11.5V → sistem tamamen kapanır        │  │
  │  │  - Akü >12.5V → sistem aktif kalır                    │  │
  │  └──────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
```

### Güç Tüketim Tablosu

| Mod | Güç | Süre (60Ah akü) | Açıklama |
|---|---|---|---|
| **Tam performans** | ~10W | ~6 saat | Sürüş sırasında (ADAS aktif) |
| **Idle (ekran açık)** | ~5W | ~12 saat | Park, ekran açık |
| **Deep Sleep** | ~0.5W | ~120 saat (5 gün) | Park, sadece PIR dinliyor |
| **Tamamen kapalı** | 0W | ∞ | Akü <11.5V → röle keser |

> **Deep Sleep ile 5 gün park:** Jetson Nano Deep Sleep'te ~0.5W çeker. 60Ah akü → 120W saat → 240 saat (~10 gün). Pratikte 5 gün güvenli (akü yaşlanması marjı).

---

## 🔌 PIR Sensör → Jetson Nano GPIO Bağlantı

### Pin Şeması

| PIR Pin (HC-SR501) | Jetson Nano Pin | İşlev |
|---|---|---|
| **VCC** | **3.3V** (Pin 1) | Güç (PIR 3.3-5V çalışır) |
| **GND** | **GND** (Pin 6) | Toprak |
| **OUT** | **GPIO 7** (Pin 26) | Hareket → HIGH → GPIO interrupt |

### Şok/İvme Sensör (MPU6050) → Jetson I2C

| MPU6050 Pin | Jetson Nano Pin | İşlev |
|---|---|---|
| **VCC** | **3.3V** | Güç |
| **GND** | **GND** | Toprak |
| **SDA** | **I2C SDA** (Pin 3) | I2C veri |
| **SCL** | **I2C SCL** (Pin 5) | I2C saat |
| **INT** | **GPIO 8** (Pin 24) | Darbe → interrupt → Jetson uyanır |

### Akıllı Röle (Akü Koruması)

```
  Araç Aküsü (12V)
       │
       ▼
  ┌──────────────┐
  │  Akıllı Röle  │ ← Voltaj sensörü (ADC)
  │  (12V → 5V)   │
  │  Akü <11.5V   │ → Röle AÇIK → Jetson tamamen kapanır
  │  Akü >12.5V   │ → Röle KAPALI → Jetson aktif
  └──────┬───────┘
         │ 5V USB-C
         ▼
  ┌──────────────┐
  │  Jetson Nano  │
  │  (Deep Sleep) │
  └──────────────┘
```

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | PIR Sensör | HC-SR501 mini (12V uyumlu) | 1 | ~$2 | Araç içi, düşük güç |
| 2 | Şok Sensör | MPU6050 (Modül 12 ile paylaşımlı) | — | $0 | Darbe/sarsıntı algılama |
| 3 | Akıllı Röle | 12V→5V DC-DC + voltaj sensörü | 1 | ~$10 | Akü koruma |
| 4 | (Opsiyonel) | Arka kamera (USB webcam) | 1 | ~$15 | Ön + arka kayıt |
| 5 | (Yazılım) | Telegram Bot API | — | $0 | Anlık bildirim |

> **Toplam ekstra maliyet: ~$12-27** (PIR + röle + opsiyonel arka kamera)

---

## ✅ Kurulum Kontrol Listesi

- [ ] PIR sensör (HC-SR501) Jetson Nano GPIO 7'ye bağlandı
- [ ] MPU6050 I2C + INT → Jetson'a bağlandı (darbe interrupt)
- [ ] Akıllı röle (12V→5V + voltaj sensör) kuruldu
- [ ] Jetson Nano Deep Sleep modu yapılandırıldı (~0.5W)
- [ ] `sentry_motion_trigger_daemon.py` systemd service olarak çalışıyor
- [ ] `telegram_whatsapp_alert_bridge.py` Telegram Bot token ayarlandı
- [ ] `car_security_home_assistant_integration.yaml` HA'a yüklendi
- [ ] Test: Park et → Deep Sleep → PIR tetikle → kamera uyandır + fotoğraf
- [ ] Test: Darbe → MPU6050 interrupt → kamera + Telegram bildirim
- [ ] Test: Akü <11.5V → röle keser → Jetson tamamen kapanır
- [ ] Test: HA SuperApp → Sentry Mode ON/OFF + ihlal fotoğrafları