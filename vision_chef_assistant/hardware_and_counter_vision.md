# vision_chef_assistant — Donanım ve Tezgah Görüşü Rehberi

> **Modül 13: Vision Chef Assistant (Multimodal Aşçı ve Mutfak Gözü)**
> Mutfak tezgahını tepeden gören IP kamera ile OpenAI Vision kullanarak anlık tarif, teknik uyarılar ve iğneleyici şef eleştirileri.

---

## 📹 IP Kamera — Mutfak Dolabı Altına Gizleme

### Kamera Seçimi

| Özellik | Detay |
|---|---|
| **Model** | TP-Link Tapo C200 / C100 (veya benzeri ucuz Wi-Fi kamera) |
| **Bağlantı** | Wi-Fi 2.4GHz (GL-MT3000 ağına bağlanır) |
| **Protokol** | RTSP (Real-Time Streaming Protocol) — HA ve OpenCV erişimi için |
| **Çözünürlük** | 720p (1280×720) — tezgah analizi için yeterli, bant genişliği düşük |
| **FPS** | 15 FPS (kamera) → biz 1 FPS ile analiz ederiz |
| **Fiyat** | ~$20-25 |

### Konumlandırma: Sadece Tezgahı Görecek

```
  ┌─────────────────────────────────────────────┐
  │                  MUTFAK YAN GÖRÜNÜM            │
  │                                             │
  │  ┌─────────────────────────────────────┐    │
  │  │           Mutfak Dolabı              │    │
  │  │                                      │    │
  │  │     ┌──────────┐                    │    │
  │  │     │  Kamera   │ ← Dolap altına     │    │
  │  │     │  (Tapo)   │   gizlenmiş        │    │
  │  │     └─────┬─────┘                    │    │
  │  │           │ (Aşağı bakar)             │    │
  │  └───────────┼──────────────────────────┘    │
  │              │                               │
  │              ▼ Görüş açısı                   │
  │  ┌─────────────────────────────────────┐    │
  │  │         TEZGAH / KESME TAHTASI        │    │
  │  │  🍅  🧅  🥩  🍳                      │    │  ← Sadece tezgah görünür
  │  │  (Malzemeler, ocak, kesme tahtası)   │    │     Oda görünmez
  │  └─────────────────────────────────────┘    │
  │                                             │
  └─────────────────────────────────────────────┘
```

### Gizleme Yöntemi

| Yöntem | Detay |
|---|---|
| **Dolap altı montaj** | Kamera, üst dolabın alt yüzeyine çift taraflı bant (3M VHB) ile yapıştırılır |
| **Açı** | Kamera 45° aşağı bakar — tezgahın tamamını görür ama duvarları/odayı görmez |
| **Kablo yönetimi** | USB güç kablosu dolap arkasından gizlenir |
| **Görünmezlik** | Kamera siyah, dolap altı gölgede → göz çapmaz |

---

## 🔒 Privacy (Gizlilik) — Neden Sadece Tezgah?

### "Çalışma Alanı" İlkesi

Kamera **odanın tamamını değil, SADECE tezgahı** görür. Bu, hem teknik hem psikolojik açıdan kritiktir:

```
  ❌ ODAYI GÖREN KAMERA (Gizlilik İhlali)      ✅ SADECE TEZGAHI GÖREN KAMERA (Güvenli)
  ┌──────────────────────────────┐             ┌──────────────────────────────┐
  │  Kamera → Tüm mutfak + salon  │             │  Kamera → Sadece tezgah      │
  │  Kişiler sürekli görüntülenir │             │  Kişiler DEĞİL, sadece yemek │
  │  "İzleniyorum" hissi          │             │  "Güvende" hissi             │
  │  Gizlilik endişesi             │             │  Rahat kullanım              │
  │  Misafir rahatsız              │             │  Misafir rahat               │
  └──────────────────────────────┘             └──────────────────────────────┘
```

### Psikolojik Güvenlik

| Faktör | Odayı Gören Kamera | Sadece Tezgahı Gören Kamera |
|---|---|---|
| **"İzlenme" hissi** | Yüksek — sürekli kamera var | Düşük — sadece yemek yaparken |
| **Misafir rahatsızlığı** | "Neden kamera bana bakıyor?" | "Kamera yemeğe bakıyor, bana değil" |
| **Günlük kullanım** | "Her an kayıt altındayım" | "Sadece tezgahı görüyor, sorun yok" |
| **Güven hissi** | Düşük | Yüksek — "çalışma alanı" sınırlı |

> **Altın Kural:** Kamera SADECE tezgahı (kesme tahtası + ocak) görmelidir. Kişileri, oturma alanını veya diğer odaları GÖRMEMELİDİR. Bu, hem gizlilik hem de misafir rahatlığı için şarttır.

### Teknik Gizlilik Önlemleri

| Önlem | Detay |
|---|---|
| **Görüş açısı sınırlama** | Kamera lensi sadece tezgaha odaklı (geniş açı lens değil) |
| **On-Demand analiz** | Kamera sürekli analiz etmez — sadece komut geldiğinde veya tetiklendiğinde |
| **Görüntü saklama** | Görüntüler diske YAZILMAZ — RAM'de işlenir, silinir |
| **Buluta görüntü** | Görüntü OpenAI Vision API'ye gönderilir ama saklanmaz (API'de tutulmaz) |
| **RTSP şifre** | Kamera RTSP yayını şifreli (kullanıcı adı + şifre) |

---

## 📋 Gerekli Donanım Listesi

| # | Bileşen | Model | Adet | Not |
|---|---|---|---|---|
| 1 | IP Kamera | TP-Link Tapo C200 | 1 | RTSP desteği, 720p, Wi-Fi |
| 2 | USB Güç Adaptörü | 5V 1A | 1 | Kamera beslemesi |
| 3 | Çift Taraflı Bant | 3M VHB | 1 | Dolap altı montaj |

---

## ✅ Kurulum Kontrol Listesi

- [ ] TP-Link Tapo kamera satın alındı ve Wi-Fi'ya (GL-MT3000) bağlandı
- [ ] RTSP yayını etkinleştirildi (Tapo app → Settings → RTSP)
- [ ] Kamera dolap altına, 45° aşağı bakacak şekilde monte edildi
- [ ] Kamera SADECE tezgahı görüyor (oda/duvar görünmüyor) — kontrol edildi
- [ ] RTSP URL test edildi (VLC player ile)
- [ ] `vision_frame_analyzer.py` çalıştırıldı ve görüntü alınıyor
- [ ] OpenAI GPT-4o-mini Vision API anahtarı ayarlandı
- [ ] `chef_persona_system_prompt.yaml` HA'a yüklendi
- [ ] `kitchen_automations.yaml` HA'a yüklendi