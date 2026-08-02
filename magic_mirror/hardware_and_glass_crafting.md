# magic_mirror — Donanım ve Cam İşçiliği Rehberi

> **Modül 4: Magic Mirror (Akıllı Ayna)**
> Duvara asılı sıradan bir aynanın, kişi yaklaştığında içinden parlayan minimalist yazılarla gizli bir ekrana dönüşmesi. Tony Stark laboratuvarından fırlamış "Calm Technology" (Sakin Teknoloji) deneyimi.

---

## 🪞 Two-Way Mirror (İki Yönlü Ayna) Akrilik Yapımı

### Malzemeler

| # | Malzeme | Tip | Boyut | Fiyat |
|---|---|---|---|---|
| 1 | Two-way mirror akrilik | Şeffaf ayna filmli akrilik | Ayna boyutu | ~$30-50 |
| 2 | LCD panel | Çerçevesiz monitör (stripped) | Akrilik ile aynı boyut | ~$80-120 |
| 3 | Raspberry Pi Zero 2 W | Mikro bilgisayar | — | ~$15 |
| 4 | Akıllı priz | Shelly Plug S / Tapo P110 | — | ~$15 |
| 5 | Siyah bant | Görünmez ışık sızdırmazlık bandı | Çevre boyu | ~$5 |
| 6 | Ahşap kasa (opsiyonel) | İnce ahşap çerçeve | Ayna boyutu | ~$20 |

> **Two-way mirror akrilik:** Normal ayna ışığı yansıtır, içeri geçirmez. Two-way mirror (spy mirror / one-way glass) ışığın bir kısmını yansıtır, bir kısmını geçirir. LCD ekran arkadan ışık yaydığında, akrilik ışığı geçirir ve yazı görünür. LCD kapalıyken akrilik sadece ayna gibi davranır.

### Yapım Adımları

#### Adım 1: LCD Panel Hazırlama (Stripping)

LCD monitörün **çerçevesini ve plastik kasasını sök**. Sadece panel + driver board kalmalı.

```
  ┌─────────────────────────────────────┐
  │         LCD PANEL (ÇERÇEVESİZ)       │
  │  ┌───────────────────────────────┐  │
  │  │                               │  │
  │  │      Görüntü alanı            │  │
  │  │                               │  │
  │  │                               │  │
  │  └───────────────────────────────┘  │
  │                                     │
  │  [Driver Board] [HDMI] [Güç]       │
  └─────────────────────────────────────┘
```

> **Dikkat:** LCD panelin arka aydınlatma (backlight) katmanını ÇIKARMA. Backlight, ekranın ışık kaynağıdır ve two-way mirror'dan ışığın geçmesi için gereklidir.

#### Adım 2: Two-Way Akrilik Montajı

LCD panelin ön yüzüne (görüntü tarafı) two-way mirror akriliği yerleştir:

```
  ┌─────────────────────────────────────┐
  │  Two-Way Mirror Akrilik (Ön)        │  ← Ayna yüzü (ışık yansıtır/geçirir)
  │  ───────────────────────────────────│
  │  LCD Panel (Arka)                   │  ← Görüntü kaynağı
  │  ───────────────────────────────────│
  │  Backlight (Arka aydınlatma)         │  ← Işık kaynağı
  └─────────────────────────────────────┘
```

#### Adım 3: Işık Sızdırmazlık (Kritik!)

LCD panelin **kenarlarından** ışık sızar. Bu ışık, aynanın kenarlarında "parlama" yapar ve illüzyonu bozar. Kenarları **siyah bant** ile kapat:

```
  ┌─────────────────────────────────────┐
  │  ████  Siyah bant (üst)         ████│  ← Kenar ışık sızıntısı engellendi
  │  █   ┌───────────────────────┐   █  │
  │  █   │                       │   █  │  ← Sadece görüntü alanı açık
  │  █ B │   Görüntü alanı        │ B █  │
  │  █ a │                       │ a █  │
  │  █ n │                       │ n █  │
  │  █ d │                       │ d █  │
  │  █   └───────────────────────┘   █  │
  │  ████  Siyah bant (alt)         ████│
  └─────────────────────────────────────┘
```

> **Alternatif:** Ahşap/siyah çerçeve ile tüm kenarları kapat. Bu hem ışık sızıntısını engeller hem de premium görünüm katar.

#### Adım 4: Duvara Asma

Aynayı duvara as. Raspberry Pi Zero'yu aynanın arkasına gizle. Akıllı prizi aynanın arkasındaki prize tak.

---

## 🔌 Akıllı Priz Mantığı — Neden Şart?

### 🚨 KRİTİK SORUN: LCD Backlight

LCD paneller, **siyah ekran gösterse bile** arka aydınlatma (backlight) çalışmaya devam eder. Backlight, ekranın arkasından sürekli ışık yayar.

```
  ❌ LCD GÜÇLÜ (Backlight açık, siyah ekran)
  ┌─────────────────────────────────────┐
  │  Two-Way Mirror Akrilik              │
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ← Backlight ışığı sızıyor!
  │  ░░░ "Siyah ekran" ama ışık var ░░░  │     Ayna GRİ/koyu görünüyor
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │     İllüzyon BOZULDU
  └─────────────────────────────────────┘

  ✅ LCD GÜÇ KESİK (Backlight kapalı)
  ┌─────────────────────────────────────┐
  │  Two-Way Mirror Akrilik              │
  │  ████████████████████████████████████│  ← Backlight kapalı!
  │  ███ Tam ayna (ışık geçmiyor)    ███│     Ayna MÜKEMMEL
  │  ████████████████████████████████████│     İllüzyon TAMAM
  └─────────────────────────────────────┘
```

### Çözüm: Akıllı Priz ile Güç Kesme

| Durum | Akıllı Priz | LCD | Ayna Görünümü |
|---|---|---|---|
| **Kişi yakında** | ON | Güçlü, ekran aktif | Yazılar görünür (siyah arka plan + beyaz yazı) |
| **Kişi uzakta** | OFF | Güç kesik, backlight kapalı | %100 normal ayna (illüzyon tam) |

> **Mantık:** Akıllı priz, LCD'nin gücünü keser. Backlight söner → akrilik tam ayna gibi davranır. Kişi yaklaştığında priz açılır → LCD boot eder → MagicMirror² arayüzü görünür.

### Boot Süresi Optimizasyonu

LCD'nin açılıp MagicMirror²'nin yüklenmesi ~10-15 saniye sürebilir. Bu süreyi kısaltmak için:

| Optimizasyon | Detay |
|---|---|
| **Raspberry Pi Zero 2 W** | Hızlı boot (~10 sn) |
| **Hafif OS** | Raspberry Pi OS Lite (Desktop değil) |
| **MagicMirror² autostart** | Boot'ta otomatik başlatma |
| **Kiosk mode** | Tam ekran, tarayıcı çubuğu yok |
| **Gereksiz servisleri kapat** | Bluetooth, WiFi güç yönetimi vb. |

> **Sonuç:** Kişi yaklaştığında priz açılır → 10-15 saniye sonra ayna "canlanır". Bu gecikme, "teknoloji açılıyor" değil, "ayna yavaşça uyanıyor" hissi yaratır — sinematik.

---

## 🧘 Calm Technology (Sakin Teknoloji) Prensibi

### "Görünmez Teknoloji" Felsefesi

Magic Mirror, **Calm Technology** prensibinin mükemmel bir örneğidir:

| İlkke | Açıklama |
|---|---|
| **Görünmezlik** | Teknoloji kullanılmadığında tamamen görünmezdir — sadece bir ayna |
| **Zamanlı Görünürlük** | Sadece ihtiyaç duyulduğunda görünür — kişi yaklaştığında |
| **Minimalist Arayüz** | Göründüğünde bile abartısızdır — saf beyaz yazı, siyah arka plan |
| **Dikkat Dağıtmama** | Renkli ikonlar, animasyonlar, bildirimler YOK — sadece bilgi |
| **Doğal Geçiş** | Ayna → ekran geçişi kademedir, ani değil |

> **Tony Stark İlkesi:** Tony Stark'ın aynası, kullanılmadığında sadece bir aynadır. İhtiyaç duyulduğunda "canlanır" — ama asla "teknoloji" gibi görünmez. Sadece "bilgi" görünür. Bu, "Calm Technology"nin özüdür.

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | Two-way mirror akrilik | Şeffaf ayna filmli | 1 | Ayna boyutu |
| 2 | LCD panel | Çerçevesiz monitör | 1 | Akrilik ile aynı boyut |
| 3 | Mikro bilgisayar | Raspberry Pi Zero 2 W | 1 | MagicMirror² çalıştırır |
| 4 | Akıllı priz | Shelly Plug S | 1 | LCD gücünü keser/açar |
| 5 | Siyah bant | Işık sızdırmazlık | 1 rulo | Kenar ışık sızıntısını engeller |
| 6 | MicroSD | 16GB Class 10 | 1 | Raspberry Pi OS |
| 7 | HDMI adaptör | Mini HDMI → HDMI | 1 | Pi Zero → LCD |
| 8 | Güç adaptörü | 5V 2.5A USB-C | 1 | Raspberry Pi |
| 9 | PIR sensör (opsiyonel) | HC-SR501 mini | 1 | Ayna yakınında hareket algılama |

---

## ✅ Kurulum Kontrol Listesi

- [ ] Two-way mirror akrilik satın alındı
- [ ] LCD monitör çerçevesi söküldü (stripped)
- [ ] LCD panel akrilik arkasına yerleştirildi
- [ ] Kenarlar siyah bant ile ışık sızdırmazlığı yapıldı
- [ ] Raspberry Pi Zero 2 W'ya Raspberry Pi OS Lite yüklendi
- [ ] MagicMirror² kuruldu ve autostart ayarlandı
- [ ] `magicmirror_config.js` yapılandırıldı (saat, hava, Spotify)
- [ ] LCD, akıllı prize bağlandı (`switch.magic_mirror_plug`)
- [ ] Akıllı priz HA'a entegre edildi
- [ ] PIR sensör veya LD2410 radar ayna yakınına monte edildi
- [ ] `mirror_presence_automation.yaml` HA'a yüklendi
- [ ] Ayna duvara asıldı, kablolar gizlendi
- [ ] Test: Güç kesik → %100 ayna | Güç açık → MagicMirror² arayüzü