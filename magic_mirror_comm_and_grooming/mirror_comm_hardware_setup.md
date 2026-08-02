# magic_mirror_comm_and_grooming — Ayna Donanım Köprüsü

> **Modül 20: Akıllı Ayna İletişim Konsolu ve Dijital Stil Koçu**
> Akıllı aynayı WhatsApp/Telegram görüntülü arama ve GPT-5.6 Vision tabanlı stil koçu ile entegre etmek.

---

## 📹 USB Web Kamera + Mikrofon + Hoparlör Montajı

### Donanım Listesi

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | USB Web Kamera | Logitech C270 / 720p mini | 1 | ~$25 | Ayna çerçevesine gizli |
| 2 | USB Mikrofon | Mini USB mic (veya INMP441 I2S) | 1 | ~$10 | Ayna arkasında gizli |
| 3 | Hoparlör | Mini piezo / 3W speaker | 1 | ~$5 | Ayna arkasında (TTS) |
| 4 | USB Hub | Mini 4-port USB hub | 1 | ~$5 | Pi Zero'nun tek USB portuna hub |

> **Not:** Raspberry Pi Zero 2 W'nin tek micro-USB portu var. USB hub ile kamera + mikrofon + güç aynı porttan beslenir.

### Kamera Gizleme — Two-Way Mirror Akrilik Üzerinde Şeffaf Alan

```
  ┌─────────────────────────────────────────────┐
  │                  AYNA ÖN GÖRÜNÜM               │
  │                                             │
  │  ┌───────────────────────────────────────┐ │
  │  │         Two-Way Mirror Akrilik         │ │
  │  │                                       │ │
  │  │         ┌─────┐                       │ │  ← Kamera lensi
  │  │         │ ◉   │  (şeffaf alan)        │ │     akrilik arkasında
  │  │         └─────┘                       │ │     "gizli nokta"
  │  │                                       │ │
  │  │  (Görünür bir şey YOK —               │ │
  │  │   sadece ayna yüzeyi)                 │ │
  │  │                                       │ │
  │  └───────────────────────────────────────┘ │
  │                                             │
  ───────────────────────────────────────────────  ← Ayna alt çerçeve
  │  ┌───────────┐                              │
  │  │ USB Cam   │ ← Ayna arkasında,            │
  │  │ (Logitech)│   akriliğe yapışık           │
  │  └───────────┘                              │
  │  ┌───────────┐                              │
  │  │ USB Mic   │ ← Ayna arkasında              │
  │  └───────────┘                              │
  │  ┌───────────┐                              │
  │  │ Hoparlör   │ ← Ayna arkasında (TTS)      │
  │  └───────────┘                              │
  │  ┌───────────┐                              │
  │  │ Pi Zero 2W│ ← Ayna arkasında              │
  │  └───────────┘                              │
  └─────────────────────────────────────────────┘
```

### Kamera Gizleme Taktikleri

| Yöntem | Detay |
|---|---|
| **Şeffaf delik** | Two-way mirror akrilik üzerinde 5mm çapında şeffaf delik aç → kamera lensi arkaya yapışık → lens delikten görür |
| **Akrilik kenarı** | Akrilik kenarında 1cm şeffaf bant bırak → kamera oraya yapışık → "kenar süsü" gibi görünür |
| **Çerçeve içine gizleme** | Ahşap/siyah çerçeve içine kamera yerleştir → çerçeve "süsü" gibi görünür |
| **Karanlık nokta** | Ayna yüzeyinde siyah nokta (1cm) → kamera arkasında → "düğme" gibi görünür |

> **En iyi yöntem:** Akrilik kenarında şeffaf alan bırak + kamera arkaya yapışık. Misafir "kamera" değil "ayna kenarı" görür.

### Pi Zero 2 W Bağlantı

```
  Pi Zero 2 W
  ┌──────────────┐
  │  micro-USB    ├──► USB Hub (4-port)
  │  (güç + veri) │     ├──► USB Web Kamera (Logitech C270)
  │              │     ├──► USB Mikrofon
  │  HDMI        │     └──► (opsiyonel) USB güç
  │  (LCD'ye)    │
  │  micro-SD    │
  │  (OS)        │
  └──────────────┘
  
  Hoparlör → Pi Zero GPIO (PWM) veya USB ses kartı
```

---

## 📋 Kurulum Kontrol Listesi

- [ ] USB web kamera ayna çerçevesine gizlendi (şeffaf alan)
- [ ] USB mikrofon ayna arkasına monte edildi
- [ ] Hoparlör ayna arkasına monte edildi (TTS için)
- [ ] USB Hub Pi Zero'ya bağlandı (kamera + mikrofon)
- [ ] Pi Zero'da `lsusb` ile kamera + mikrofon görünüyor mu
- [ ] `fswebcam` ile test fotoğraf alındı
- [ ] `arecord` ile mikrofon testi yapıldı
- [ ] Hoparlör testi (TTS sesi duyuluyor)
- [ ] `whatsapp_video_integration_module.py` çalışıyor
- [ ] `digital_grooming_coach_vision.yaml` HA'a yüklendi
- [ ] `grooming_checklist_mirror_ui.js` MagicMirror'a eklendi