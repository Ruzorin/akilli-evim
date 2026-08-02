# spatial_audio — Donanım ve Akustik Tasarım Rehberi

> **Modül 5: Spatial Audio (Sesin Konumlandırılması ve Medya Otomasyonları)**
> Tek ve gürültülü bir ses kaynağı yerine, odanın iki zıt köşesine gizlenmiş akıllı hoparlörlerle stereo/spatial bir ses alanı yaratmak. Düşük ses seviyelerinde bile (%15-20) odanın her yerini dolduran "Cocoon Effect" (Ses Kozası) deneyimi.

---

## 🎵 Neden Tek Hoparlör Değil, Stereo Pair?

### "Cocoon Effect" (Ses Kozası) Kavramı

Tek bir güçlü hoparlör, sesi **tek bir noktadan** yayar. Oda içinde yürüdükçe sesin kaynağı bellidir — "hoparlör orada, ben burada" hissi. Bu, "odada müzik çalıyor" hissidir.

Stereo pair (iki hoparlör), sesi **iki zıt noktadan** yayar. Beyin, iki kaynaktan gelen sesi birleştirir ve odanın **her yerinden** ses geldiğini algılar — sesin kaynağı belirsizleşir. Bu, "odanın içinde müzik var" hissidir.

```
  ❌ TEK HOPARLÖR (Noktasal Ses)              ✅ STEREO PAIR (Cocoon Effect)
  ┌──────────────────────────────┐           ┌──────────────────────────────┐
  │                              │           │  🔊                          │
  │                              │           │  (Sol)                       │
  │                              │           │    ╲                        │
  │         🔊                   │           │     ╲   Ses kozası          │
  │      (Tek kaynak)            │           │      ╲  (Cocoon)             │
  │         ↓                    │           │       ╲                     │
  │  "Müzik oradan geliyor"      │           │        ●  (Kişi)            │
  │                              │           │       ╱                     │
  │                              │           │      ╱                      │
  │                              │           │     ╱                       │
  │                              │           │  🔊                          │
  │                              │           │  (Sağ)                       │
  └──────────────────────────────┘           └──────────────────────────────┘
  "Odada müzik çalıyor"                      "Müzik odanın içinde"
  Kaynak bellidir                            Kaynak belirsizdir → "Cocoon"
```

### Akustik ve Psikolojik Karşılaştırma

| Faktör | Tek Hoparlör | Stereo Pair (Cocoon) |
|---|---|---|
| **Ses Kaynağı** | Belli, lokalize edilebilir | Belirsiz, "her yerden" geliyor |
| **Düşük Ses Algısı** | Düşük seste "uzak" hissi | Düşük seste bile "sarıcı" hissi |
| **Stereo Genişlik** | Yok (mono) | Geniş, derinlik hissi |
| **Psikolojik Etki** | "Hoparlör var" | "Ses var" → daha az dikkat dağıtıcı |
| **Premium Hissi** | "Bluetooth hoparlör" | "Otel lobisi / sinema salonu" |
| **Maliyet** | 1x güçlü hoparlör (~$100) | 2x ucuz akıllı hoparlör (~$50) |

> **Sonuç:** İki ucuz Echo Dot / Nest Mini, tek bir pahalı hoparlörden çok daha premium bir deneyim yaratır. Çünkü önemli olan sesin **gücü** değil, sesin **yayılımı**dır.

---

## 🔊 İdeal Hoparlör Yerleşimi

### Çapraz Konumlandırma (Diagonal Placement)

İki hoparlör, odanın **zıt köşelerine** yerleştirilir. Bu, sesin odanın en geniş diagonal boyunca yayılmasını sağlar.

```
  ┌─────────────────────────────────────────────┐
  │                  ODA ÜST GÖRÜNÜM              │
  │                                             │
  │  🔊                                    🔊   │
  │  (Sol)                                (Sağ) │
  │   ↓                                    ↓    │
  │  Kulak hizasının                        Kulak hizasının  │
  │  altında, gizli                         altında, gizli    │
  │                                             │
  │              ┌──────────┐                   │
  │              │  YATAK   │                   │
  │              └──────────┘                   │
  │                                             │
  │  Hoparlörler çapraz köşelerde,              │
  │  birbirine bakar şekilde                    │
  └─────────────────────────────────────────────┘
```

### Yerleşim Kuralları

| Kural | Açıklama |
|---|---|
| **Çapraz köşe** | İki hoparlör odanın zıt köşelerinde → maksimum stereo genişlik |
| **Kulak hizasının altı** | Hoparlörler yatak/koltuk seviyesinden biraz aşağıda → ses "yukarıdan" değil "çevreden" gelir |
| **Gizli yerleşim** | Hoparlörler görünmemeli — kitaplık arkası, komodin altı, bitki saksısı arkası |
| **Duvara yakın** | Hoparlörler duvara yaklaştır → duvar yansıması sesi güçlendirir (boundary gain) |
| **Simetrik mesafe** | İki hoparlörün dinleme noktasına (yatak) mesafesi eşit olmalı → stereo dengesi |

### Neden Kulak Hizasının Altında?

| Yükseklik | Etki |
|---|---|
| **Kulak hizasında** | Ses "doğrudan" gelir → kaynak bellidir |
| **Kulak hizasının altı** | Ses "yukarıdan yükselir" → kaynak belirsizleşir → cocoon etkisi |
| **Tavanda** | Ses "gökten iner" → sinematik his, ama kurulum zor |
| **Zeminde** | Ses "yerden yükselir" → sıcak his, ama bas yoğunlaşır |

> **Öneri:** Komodin üstü veya kitaplık rafı, yatak seviyesinden 20-30cm aşağıda. Hoparlör bir kitap veya bitki arkasına gizlenir.

---

## 🎧 Önerilen Hoparlörler

| Model | Tip | Fiyat | Stereo Pair | HA Entegrasyonu |
|---|---|---|---|---|
| **Echo Dot (5. Gen)** | Alexa | ~$25 | ✅ (Alexa app) | ✅ (Alexa Media Player) |
| **Nest Mini (2. Gen)** | Google | ~$30 | ✅ (Google Home) | ✅ (Google Cast) |
| **Sonos One** | Sonos | ~$200 | ✅ (Sonos app) | ✅ (Sonos entegrasyon) |

> **Öneri:** Echo Dot (5. Gen) — ucuz, stereo pair desteği var, HA "Alexa Media Player" custom component ile tam kontrol. İki adet ~$50.

---

## 📱 Home Assistant Spotify Entegrasyonu

### Yöntem 1: Dahili Spotify Entegrasyonu (Önerilen)

HA'ın yerleşik Spotify entegrasyonu, Spotify Connect üzerinden çalma kontrolü sağlar.

1. **HA → Settings → Devices → Add → Spotify**
2. Spotify hesabınla giriş yap
3. `media_player.spotify` entity'si oluşur
4. Çalma listesi, parça, ses kontrolü yapılabilir

> **Not:** Spotify Connect, hoparlörleri "çalma hedefi" olarak seçmeni sağlar. Echo Dot / Nest Mini, Spotify Connect cihazı olarak görünür.

### Yöntem 2: Spotcast (Custom Component)

Spotcast, Spotify Web API üzerinden çalma listesi başlatmak için kullanılır. Dahili entegrasyondan daha güçlüdür.

1. **HACS → Integrations → Spotcast → Install**
2. Spotify OAuth bilgilerini gir
3. `media_player.spotify` üzerinden çalma listesi URI'si ile başlatma yapılabilir

### Yöntem 3: Alexa Media Player (Echo Dot için)

Echo Dot'ları HA'tan kontrol etmek için:

1. **HACS → Integrations → Alexa Media Player → Install**
2. Amazon hesabınla giriş yap
3. `media_player.echo_dot_sol` ve `media_player.echo_dot_sag` entity'leri oluşur
4. Ses, çalma, duraklatma kontrolü yapılabilir

### Stereo Pair Oluşturma

| Platform | Yöntem |
|---|---|
| **Alexa (Echo Dot)** | Alexa app → Devices → Create Stereo Pair → Sol + Sağ seç |
| **Google (Nest Mini)** | Google Home app → Create Stereo Pair |
| **Sonos** | Sonos app → Create Room → Stereo Pair |

> Stereo pair oluşturulduktan sonra HA'ta **tek bir** `media_player.room_spatial_audio` entity'si olarak görünür.

---

## ✅ Kurulum Kontrol Listesi

- [ ] İki adet Echo Dot (veya Nest Mini) satın alındı
- [ ] Hoparlörler odanın çapraz köşelerine, kulak hizasının altına yerleştirildi
- [ ] Hoparlörler gizlendi (kitap/bitki arkası)
- [ ] Alexa/Google app'inde stereo pair oluşturuldu
- [ ] HA'a Spotify entegrasyonu eklendi (`media_player.spotify`)
- [ ] HA'a Alexa Media Player (veya Google Cast) eklendi
- [ ] `media_player.room_spatial_audio` entity'si HA'da görünüyor
- [ ] Spotify çalma listeleri (lofi_focus, deep_rnb_date, acoustic_morning) oluşturuldu
- [ ] `media_player_integration.yaml` HA'a yüklendi
- [ ] `dynamic_volume_automations.yaml` HA'a yüklendi