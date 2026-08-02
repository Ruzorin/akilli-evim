# life_os_superapp — UI ve PWA Mimarisi

> **Modül 18: Life OS SuperApp (PWA SuperApp ve Çağrı Yönlendirme)**
> Home Assistant'ı sıkıcı bir kontrol paneli olmaktan çıkarıp; sağlık, takvim, medya ve AGI chat arayüzünü tek bir yerde toplayan şık bir "SuperApp" (PWA) haline getirmek.

---

## 📱 PWA (Progressive Web App) — Home Assistant'ı Telefona Uygulama Olarak Ekle

### PWA Nedir?

PWA, bir web sitesini "native uygulama gibi" çalıştıran teknolojidir. Home Assistant, PWA desteği ile tarayıcıdan açıldığında tam ekran, kendi ikonuyla, app drawer'da görünerek çalışır.

```
  ❌ Tarayıcı sekmesi (sıkıcı)          ✅ PWA (kendi uygulaması gibi)
  ┌──────────────────────┐              ┌──────────────────────┐
  │ [sekme] [sekme] HA   │              │                      │
  │ ┌──────────────────┐ │              │  Tam ekran           │
  │ │  HA arayüzü       │ │              │  Adres çubuğu YOK    │
  │ │  (adres çubuğu    │ │              │  Kendi ikonu         │
  │ │   var, sekme var) │ │              │  App drawer'da       │
  │ └──────────────────┘ │              │  Offline destek      │
  └──────────────────────┘              └──────────────────────┘
```

### PWA Kurulumu

**iOS (iPhone):**
```
1. Safari'de HA URL'ini aç: http://VPS_IP:8123
2. Alt çubukta "Paylaş" ikonuna bas
3. "Ana Ekrana Ekle" seç
4. İsim: "Jarvis" (veya istediğin isim)
5. "Ekle" → Ana ekranda Jarvis ikonu oluşur
6. İkona tıkla → tam ekran PWA açılır
```

**Android:**
```
1. Chrome'da HA URL'ini aç
2. Sağ üst menü → "Ana ekrana ekle"
3. İsim: "Jarvis"
4. "Ekle" → App drawer'da Jarvis ikonu oluşur
5. İkona tıkla → tam ekran PWA açılır
```

> **Sonuç:** Kullanıcı telefonda "Jarvis" ikonuna tıklar → tam ekran, adres çubuğu olmayan, native uygulama hissi veren bir SuperApp açılır.

---

## 🎨 Neden Mushroom Cards ve Bubble Card?

### Geleneksel HA Kartları vs Modern Kartlar

```
  ❌ GELENEKSEL HA KARTLARI              ✅ MUSHROOM + BUBBLE CARD
  ┌──────────────────────┐              ┌──────────────────────┐
  │  [Işık]  [Priz]      │              │  ╭─────────╮         │
  │  [Sensör] [Switch]   │              │  │ ☀ 80%   │         │
  │  [Klima] [Perde]     │              │  ╰─────────╯         │
  │  (Kalabalık, düz,    │              │  ╭─────────╮         │
  │   sıkıcı, "kontrol   │              │  │ 🌡 22°C  │         │
  │   paneli" hissi)     │              │  ╰─────────╯         │
  └──────────────────────┘              │  (Minimal, yuvarlak, │
                                        │   Apple/Tesla tarzı) │
                                        └──────────────────────┘
```

| Faktör | Geleneksel | Mushroom + Bubble |
|---|---|---|
| **Tasarım** | Kare, düz, kalabalık | Yuvarlak, minimalist, boşluklu |
| **Hissi** | "Kontrol paneli" (endüstriyel) | "Premium app" (Apple/Tesla) |
| **Dokunma** | Küçük butonlar | Büyük, yuvarlak, kolay dokunma |
| **Renk** | HA varsayılan (mavi) | Özelleştirilebilir (sıcak tonlar) |
| **Animasyon** | Yok | Yumuşak geçişler, hover efektleri |
| **Mobil uyum** | Zorunlu kaydırma | Tek ekranda sığar |

### Mushroom Cards

- **Mushroom:** Yuvarlak, minimalist kartlar. Işık, sensör, switch için büyük dokunma alanları.
- **Apple tarzı:** Temiz, boşluklu, ikon odaklı. "Kontrol paneli" değil "yaşam alanı" hissi.
- **Kurulum:** HACS → Frontend → Mushroom → Install

### Bubble Card

- **Bubble Card:** Swipeable (kaydırılabilir) sekmeler, pop-up kartlar, yatay kaydırma.
- **Tesla tarzı:** Sekmeler arası sağa-sola kaydırma, pop-up ile detay gizleme.
- **Kurulum:** HACS → Frontend → Bubble Card → Install

> **UX Prensibi:** "Karmaşık verileri (sağlık, ev kontrolü, sohbet) tek bir ekranda kullanıcıyı YORMADAN sun." Mushroom + Bubble ile her veri kendi yuvarlak kartında, sekmeler arası kaydırma ile bölümler ayrılır. Kalabalık yok, boğulma yok.

---

## 📞 Bluetooth Proxy — Telefon Çağrılarını Odaya Aktarma

### Mimari

```
  Telefon (çağrı)                        Oda
  ┌──────────────┐                      ┌──────────────┐
  │  Gelen arama  │                      │  Hoparlörler  │
  │  (ringing)    │                      │  (Echo Dot ×2)│
  └──────┬───────┘                      └──────▲───────┘
         │                                     │
         │ Bluetooth                           │ I2S / Spotify Connect
         ▼                                     │
  ┌──────────────┐    ┌──────────────┐  ┌─────┴───────┐
  │  ESP32-S3    │───►│  HA Companion│─►│  MQTT → HA  │
  │  (BT Proxy)  │    │  App (call   │  │  → Audio    │
  │              │    │   state)     │  │  routing    │
  └──────────────┘    └──────────────┘  └─────────────┘
```

### ESP32-S3 Bluetooth Proxy Kurulumu

```
1. Modül 1'deki ESP32-S3 (Audio Hub) zaten kurulu
2. ESPHome'a Bluetooth Proxy bileşeni ekle:
   bluetooth_proxy:
     active: true
3. ESP32-S3, telefonun Bluetooth bağlantısını "proxy" olarak alır
4. Telefon çağrısı → ESP32-S3 → I2S mikrofon (senin sesin)
                    → Hoparlör (karşı tarafın sesi)
5. Hands-free calling: Odaya konuş, oda duyur
```

### HA Companion App — Çağrı Durumu Sensörü

```
1. HA Companion App → Settings → Sensors → Phone State
2. sensor.phone_state sensörü oluşur:
   - "idle" (çağrı yok)
   - "ringing" (çağrı geliyor)
   - "offhook" (çağrı cevaplandı)
3. HA, bu sensörü dinler → çağrı geldiğinde otomasyon tetiklenir
```

---

## 📋 Gerekli Ek Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | Mushroom Cards (HACS) | — | $0 | Modern yuvarlak kartlar |
| 2 | (Yazılım) | Bubble Card (HACS) | — | $0 | Swipeable sekmeler |
| 3 | (Yazılım) | HA Companion App | — | $0 | PWA + çağrı sensörü |
| 4 | (Donanım) | ESP32-S3 Bluetooth Proxy | — | $0 | Modül 1 ile paylaşımlı |

> **Toplam ekstra maliyet: ~$0** — tüm altyapı mevcut, sadece yazılım.

---

## ✅ Kurulum Kontrol Listesi

- [ ] HA PWA olarak telefona eklendi (tam ekran, kendi ikonu)
- [ ] HACS → Mushroom Cards kuruldu
- [ ] HACS → Bubble Card kuruldu
- [ ] `superapp_lovelace_dashboard.yaml` HA'a yüklendi
- [ ] Karşılama kartı (günaydın + takvim) çalışıyor
- [ ] Swipeable sekmeler (Ev kontrolü + Sağlık) çalışıyor
- [ ] Alt medya kontrolcüsü (Spotify/Hyperion) çalışıyor
- [ ] `agi_chat_interface.yaml` HA'a yüklendi (floating chat)
- [ ] AGI chat'ten GPT-5.6'ya yazılı komut gönderilebiliyor
- [ ] `call_routing_automation.yaml` HA'a yüklendi
- [ ] ESP32-S3 Bluetooth Proxy aktif
- [ ] HA Companion App → phone_state sensörü çalışıyor
- [ ] Test: Telefon çağrısı → müzik durakla + WLED mavi yanıp sön + çağrı odaya aktar