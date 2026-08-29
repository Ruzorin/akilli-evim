# 🍸 Modül 31: Siber Barmen — CocktailBerry Donanım ve Kablolama Rehberi

> **"Misafir gelince 'Bana Negroni yap' dersin, gerisini o halleder."**

CocktailBerry, Raspberry Pi 3/4 tabanlı, 7" dokunmatik ekranlı (Kiosk mod), 10 adet 12V pompayla çalışan tam otonom kokteyl miksoloji robotudur. Açık kaynak [CocktailBerry](https://github.com/AndreWohnsland/CocktailBerry) yazılımı üzerine kuruludur.

---

## 📦 Donanım Listesi

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Tek Kart Bilgisayar | Raspberry Pi 4 (4GB) | 1 | ~$55 | CocktailBerry + Kiosk UI çalıştırır |
| 2 | Dokunmatik Ekran | Raspberry Pi 7" Touch Display | 1 | ~$60 | Kiosk mod — kokteyl seçim arayüzü |
| 3 | Röle Kartı | 16 Kanal 5V Röle Modülü (Aktif Low) | 1 | ~$12 | 10 pompayı kontrol eder (6 kanal yedek) |
| 4 | Pompa | 12V Diyafram/Peristaltik Pompa | 10 | ~$8/adet | 10 farklı içki/mixer için |
| 5 | Silikon Hortum | Gıda Uyumlu Silikon Hortum (Ø6mm) | 15m | ~$15 | Pompa → nozül arası sıvı taşıma |
| 6 | Koruma Diyotu | 1N4007 (1000V 1A) | 10 | ~$0.10/adet | Ters akım koruması — her pompaya paralel |
| 7 | Güç Kaynağı | 12V 10A SMPS | 1 | ~$20 | 10 pompayı besler (10× 0.8A = 8A peak) |
| 8 | Voltaj Düşürücü | LM2596 Buck Converter | 1 | ~$3 | 12V → 5V (Pi'yi besler) |
| 9 | Dişi DC Jack | 5.5×2.1mm | 2 | ~$1 | Güç girişi |
| 10 | Jumper Kablo | Dişi-Erkek Dupont | 20 | ~$2 | Pi GPIO → röle kartı |
| 11 | 3D Baskı Kasa | PLA Filament 500g | 1 | ~$6 | Pompa montaj + ekran çerçeve |

**Modül 31 Toplam:** ~**$265**

---

## 🔧 Elektronik Kablolama

### Genel Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    12V 10A SMPS                              │
│  ┌──────────┐                    ┌──────────────────────┐   │
│  │ 12V Rail │◄───────────────────│  AC 220V Girişi      │   │
│  │ (10A)    │                    └──────────────────────┘   │
│  └────┬─────┘                                                │
│       │                                                      │
│       ├──► LM2596 Buck ──► 5V ──► Raspberry Pi 4 (USB-C)    │
│       │                                                      │
│       ├──► Pompa 1 (Vodka)        ──► Röle CH1              │
│       ├──► Pompa 2 (Gin)          ──► Röle CH2              │
│       ├──► Pompa 3 (Rum)          ──► Röle CH3              │
│       ├──► Pompa 4 (Tekila)       ──► Röle CH4              │
│       ├──► Pompa 5 (Viski)        ──► Röle CH5              │
│       ├──► Pompa 6 (Campari)      ──► Röle CH6              │
│       ├──► Pompa 7 (Lime Juice)   ──► Röle CH7              │
│       ├──► Pompa 8 (Cranberry)    ──► Röle CH8              │
│       ├──► Pompa 9 (Soda)         ──► Röle CH9              │
│       └──► Pompa 10 (Tonic)       ──► Röle CH10             │
│                                                              │
│  Raspberry Pi 4 GPIO ──► 16-CH Röle Kartı (10 kanal kullan) │
│  7" Touch Display ──► DSI Ribbon ──► Pi                     │
└─────────────────────────────────────────────────────────────┘
```

### GPIO → Röle Eşlemesi

| Röle Kanalı | Pi GPIO Pin | Pompa | İçki/Mixer |
|---|---|---|---|
| CH1 | GPIO 17 (Pin 11) | Pompa 1 | Vodka |
| CH2 | GPIO 27 (Pin 13) | Pompa 2 | Gin |
| CH3 | GPIO 22 (Pin 15) | Pompa 3 | Rom |
| CH4 | GPIO 23 (Pin 16) | Pompa 4 | Tekila |
| CH5 | GPIO 24 (Pin 18) | Pompa 5 | Viski |
| CH6 | GPIO 25 (Pin 22) | Pompa 6 | Campari |
| CH7 | GPIO 5 (Pin 29) | Pompa 7 | Lime Juice |
| CH8 | GPIO 6 (Pin 31) | Pompa 8 | Cranberry |
| CH9 | GPIO 12 (Pin 32) | Pompa 9 | Soda |
| CH10 | GPIO 16 (Pin 36) | Pompa 10 | Tonic |
| CH11-16 | — | Yedek | Gelecek genişletme |

> **Not:** Röle kartı "Aktif Low" ise GPIO HIGH = röle OFF, GPIO LOW = röle ON. CocktailBerry yazılımı bunu otomatik yönetir.

---

## ⚡ 1N4007 Ters Akım Koruma Diyotları — KRİTİK

### Neden Gerekli?

12V diyafram pompalar DC motor içerir. Röle açıldığında (pompa kapatıldığında) motorun sargısında ters EMF (back-EMF) spike'ı oluşur. Bu spike:
- **Röle kontaklarını eritebilir** (ark oluşumu)
- **Pi GPIO pin'lerini yakabilir** (EMI geri beslemesi)
- **Diğer pompaların yanlış tetiklenmesine** yol açabilir

### 1N4007 Diyot Lehimleme Kuralı

```
Her pompanın + ve - terminaline 1N4007 diyot PARALEL lehimlenir:

         1N4007
        ┌──────┐
  + ────┤K    A ├──── ──── Pompa +
        │       │        │
        │       │      ┌─┴─┐
        │       │      │   │ Pompa Motor
        │       │      │   │
        │       │      └─┬─┘
  - ────┤       ├──── ──── Pompa -
        └──────┘

K = Katot (çizgili taraf) → Pompa + 'ya
A = Anot                → Pompa - 'ye

Diyot TERS偏 (reverse) bağlanır:
  Katot → Pompa + (12V tarafı)
  Anot  → Pompa - (GND tarafı)

Normal çalışmada diyot iletime girmez (ters bias).
Röle açıldığında ters EMF, diyot üzerinden kısa devre olur → spike absorbe edilir.
```

### Lehimleme Adımları

```
1. Her pompanın + ve - kablosunu çıkar
2. 1N4007 diyotun katot (çizgili) ucunu → pompa + kablosuna lehimle
3. 1N4007 diyotun anot ucunu → pompa - kablosuna lehimle
4. Isı büzük boru ile izole et
5. 10 pompa için tekrarla (10 diyot)
6. Multimetre ile doğrulama: Pompa + ve - arası diyot test
   → Ters yönde yüksek direnç (iletim yok)
   → Doğru yönde 0.6V düşüm (iletim var)
```

> **⚠️ UYARI:** Diyotu yanlış yönde lehimlersen (katot → GND), pompa kısa devre olur ve SMPS korumaya geçer. Lehimlemeden önce mutlaka katot (çizgi) tarafını kontrol et.

---

## 🔌 Güç Dağılımı

### 12V Rail (Pompalar)

| Bileşen | Akım | Toplam |
|---|---|---|
| 10 pompa (her biri ~0.8A peak) | 0.8A × 10 | 8A (hepsi aynı anda — nadir) |
| Tipik kullanım (2-3 pompa aynı anda) | 0.8A × 3 | 2.4A |
| SMPS kapasitesi | — | 10A (yeterli) |

### 5V Rail (Raspberry Pi)

```
12V ──► LM2596 Buck Converter ──► 5V/3A ──► Pi 4 USB-C

LM2596 ayarı:
  1. Çıkış multimetreye bağla
  2. Trimpot'u çevir → çıkış 5.0V'a ayarla
  3. Pi'yi bağla → voltaj 4.9V altına düşmemeli
  4. Sabitle (trimpot'u yapıştır/lok-tite)
```

> **Not:** Pi 4'ün resmi güç adaptörü 5.1V/3A'dir. LM2596 3A verebilir ama Pi + 7" ekran birlikte ~2.5A çeker. 5V rail'de voltaj düşümü varsa ayrı bir 5V adaptör kullan (LM2596 yerine).

---

## 🖥️ 7" Dokunmatik Ekran Montajı

```
1. 7" Touch Display DSI ribbon kablo → Pi 4 DSI port
2. Ekran güç → Pi GPIO 5V/GND (veya ayrı 5V)
3. 3D baskı çerçeve → ekranı dik açıda tutar (~70°)
4. Kiosk mod: Ekran yatay (landscape), CocktailBerry UI tam ekran

Montaj pozisyonu:
  ┌─────────────────────────────┐
  │    7" Touch Display         │
  │  ┌───────────────────────┐  │
  │  │  CocktailBerry UI     │  │
  │  │  [Negroni] [Mojito]   │  │
  │  │  [Margarita] [Aperol] │  │
  │  └───────────────────────┘  │
  └──────────┬──────────────────┘
             │
  ┌──────────┴──────────────────┐
  │  Pompa Kovanı (10 pompa)     │
  │  ┌──┬──┬──┬──┬──┬──┬──┬──┐ │
  │  │P1│P2│P3│P4│P5│P6│P7│P8│ │
  │  └──┴──┴──┴──┴──┴──┴──┴──┘ │
  │  ┌──┬──┐                    │
  │  │P9│P10│                   │
  │  └──┴──┘                    │
  └─────────────────────────────┘
```

---

## 🧪 İlk Çalıştırma ve Kalibrasyon

### Pompa Akış Hızı Kalibrasyonu

```
1. Her pompayı ayrı ayrı test et:
   python3 -m CocktailBerry --calibrate-pump 1

2. Pompa 1'i 10 saniye çalıştır
3. Çıkan sıvıyı ölç (ml)
4. Akış hızı = ml / 10 sn = ml/sn
5. CocktailBerry config'e kaydet:
   → /config/ingredients.yaml
   → pump_1_flow_rate: X.X ml/sn

6. 10 pompa için tekrarla
7. Doğrulama: "30ml Vodka" komutu → gerçekten 30ml çıkıyor mu?
```

### Hortum Doluluk (Priming)

```
İlk kurulumda hortumlar boştur:
1. Her pompayı 30 sn çalıştır → hortum dolana kadar
2. Hortumdan sıvı gelene kadar bekle
3. CocktailBerry "prime" komutu:
   python3 -m CocktailBerry --prime-all
4. Artık hortumlar dolu → ilk komut anında sıvı gelir
```

---

## 🔒 Güvenlik

| Kural | Açıklama |
|---|---|
| **Alkol yaşı** | 18+ — CocktailBerry UI'de yaş doğrulama ekranı |
| **Maksimum içki** | Günde max 5 kokteyl (yazılımsal limit) |
| **Acil stop** | Ekran üzerinde büyük "STOP" butonu → tüm röleler OFF |
| **Sızıntı kontrolü** | Pompa kovanı altında damarlık tepsisi |
| **Güç kesme** | Ana switch → 12V ve 5V aynı anda kesilir |
| **Çocuk kilidi** | PIN kodu ile kokteyl menüsü kilitlenir |

---

*Bu dosya, CocktailBerry kokteyl robotunun donanım montajı ve elektronik kablolamasını detaylandır. 1N4007 diyot kuralları KRİTİKTİR — atlanmamalıdır.*
