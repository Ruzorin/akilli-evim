# hyperion_media_sync — Donanım ve Hyperion Kurulum Rehberi

> **Modül 17: Hyperion Media Sync (Ekran Senkronizasyonu ve Dinamik Medya Atmosferi)**
> Bilgisayar/TV ekranındaki görüntüleri Hyperion.ng ile anlık olarak WLED sistemine yansıtmak; YouTube, Netflix veya canlı maç yayınlarına göre odanın aydınlatmasını, ses profilini ve koku difüzörünü otonom olarak senkronize etmek.

---

## 🎬 Hyperion.ng Nedir?

Hyperion.ng, ekranın kenar piksellerini anlık olarak okuyup LED şeritlere yansıtan açık kaynaklı bir yazılımdır. "Ambilight" teknolojisinin açık kaynak versiyonudur.

```
  EKRAN (TV/Monitör)                    ODA
  ┌──────────────────────┐              ┌──────────────────────┐
  │                      │              │  ░░░░░░░░░░░░░░░░░░  │ ← WLED şerit
  │    Film / Maç        │              │  ░░░░░░░░░░░░░░░░░░  │    ekran kenarı
  │    (Netflix/YouTube)  │              │  ░░░░░░░░░░░░░░░░░░  │    rengini yansır
  │                      │              │                      │
  └──────────────────────┘              └──────────────────────┘
         │                                       ▲
         │ Hyperion.ng (piksel yakalama)          │ UDP sync
         └───────────────────────────────────────┘
              Sıfır gecikme (<16ms = 1 frame)
```

### Sinematik ve Psikolojik Etki

| Faktör | Etki |
|---|---|
| **Ekran sınırları kaybolur** | WLED şerit, ekranın kenar rengini yansıtır → ekran "büyür" → "duvarlar kayboluyor" hissi |
| **İmersif deneyim** | Oda, ekrandaki sahnenin bir parçası olur → "sinema salonu" değil "filmin içinde" |
| **Duyusal genişletme** | Kırmızı sahne → oda kırmızı; mavi sahne → oda mavi → beyin "sahnenin içinde" algılar |
| **Göz yorgunluğu azalır** | Ekran-parlak duvar kontrastı düşer → göz daha az yorulur → uzun izleme konforu |

> **"Ekranın sınırlarının kaybolması"**: Normalde ekran bir "kutu"dur — etrafı karanlık, içerisi parlak. Hyperion ile ekranın kenar rengi odaya yansır → ekran "kutu" olmaktan çıkar → "pencere" olur. Bu, sinematik immersif deneyimin temelidir.

---

## 🔧 Hyperion.ng Kurulumu

### Yöntem 1: Raspberry Pi Üzerinde (Önerilen)

```
1. Raspberry Pi OS Lite (64-bit) MicroSD'ye yaz
2. Pi'yi başlat, SSH ile bağlan
3. Hyperion.ng kur:
   curl -sSL https://apt.hyperion-project.org/hyperion.pub.key | gpg --dearmor | sudo tee /usr/share/keyrings/hyperion.pub.gpg >/dev/null
   echo "deb [signed-by=/usr/share/keyrings/hyperion.pub.gpg] https://apt.hyperion-project.org/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hyperion.list
   sudo apt update && sudo apt install hyperion -y
4. Hyperion web arayüzüne eriş: http://PI_IP:8090
5. USB Capture cihazı bağla (HDMI → USB grabber):
   - UCV007 veya MS2109 chip'li HDMI grabber (~$10)
   - HDMI splitter: kaynak → splitter → TV + grabber
6. Hyperion → Input → USB Capture seç
7. Frame rate: 30 FPS (düşük gecikme için yeterli)
```

### Yöntem 2: Bilgisayar Üzerinde (Windows/Mac)

```
1. Hyperion.ng Desktop indir: https://github.com/hyperion-project/hyperion.ng/releases
2. Kur ve çalıştır
3. Screen Capture: "DirectX11 Grabber" (Windows) veya "AVF Grabber" (Mac)
4. Ekranın kenar piksellerini yakala → WLED'e gönder
```

---

## 🔗 WLED ile UDP Senkronizasyonu (Sıfır Gecikme)

### Neden UDP?

| Protokol | Gecikme | Güvenilirlik | Kullanım |
|---|---|---|---|
| **UDP** | <16ms (1 frame) | "Best effort" (paket kaybı olabilir) | ✅ Hyperion → WLED |
| TCP | 50-100ms | Garanti teslim | ❌ Çok yavaş |

> **UDP seçimi KRİTİKTİR:** Hyperion, saniyede 30-60 kare gönderir. Her kare <16ms içinde WLED'e ulaşmalıdır. TCP'nin ACK bekleme mekanizması 50-100ms gecikme yaratır → ışık ekrandan "geride kalır" → illüzyon bozulur. UDP'de paket kaybı olsa bile bir sonraki kare hemen gelir → gecikme yok.

### Hyperion → WLED UDP Konfigürasyonu

```
1. Hyperion web arayüzü → LED Hardware → LED Controller
2. Controller type: "WLED"
3. WLED IP: 192.168.1.104 (WLED ESP32 IP'si)
4. UDP port: 19446 (WLED UDP sync port)
5. Protocol: "WLED" (DRGB mode)
6. LED sayısı: WLED şeridindeki LED sayısı (örn: 60)
7. LED düzeni: Ekran kenarına göre (top, bottom, left, right sırası)

WLED tarafında:
1. WLED web arayüzü → Sync Settings
2. UDP Port: 19446
3. Receive: ON (Hyperion'dan gelen UDP paketleri al)
4. Receive Brightness: ON (Hyperion parlaklığı kullan)
5. Realtime: ON (Hyperion kontrolü aktif)
```

### Sıfır Gecikme Optimizasyonu

```
1. Hyperion → Smoothing: OFF (smoothing gecikme yaratır)
2. Hyperion → Blackborder: ON (siyah çubukları yok say)
3. Hyperion → Frame rate: 30 FPS (60 FPS CPU yorar, 30 yeterli)
4. WLED → Realtime Max: 255 (maksimum parlaklık)
5. WLED → Realtime Dither: ON (renk geçişleri pürüzsüz)
6. Ağ: Kablolu Ethernet (WiFi gecikme değişken)
7. HDMI grabber: Düşük gecikme chip (UCV007 < 50ms)
```

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Hyperion Sunucu | Raspberry Pi 4 (2GB) | 1 | ~$45 | Hyperion.ng çalıştırır (Modül 1 Pi 4'ten ayrı) |
| 2 | HDMI Grabber | UCV007 / MS2109 USB | 1 | ~$10 | HDMI → USB, düşük gecikme |
| 3 | HDMI Splitter | 1x2 HDMI splitter | 1 | ~$10 | Kaynak → TV + grabber |
| 4 | HDMI Kablo | 1.5m | 2 | ~$3/adet | Kaynak → splitter → TV/grabber |

> **Not:** WLED sistemi (Modül 10) zaten kurulu. Bu modül sadece Hyperion yazılımı + HDMI grabber ekler.

---

## ✅ Kurulum Kontrol Listesi

- [ ] Hyperion.ng kuruldu (Raspberry Pi veya bilgisayar)
- [ ] HDMI grabber bağlandı (USB → Pi/bilgisayar)
- [ ] HDMI splitter: kaynak → splitter → TV + grabber
- [ ] Hyperion web arayüzüne erişildi (http://PI_IP:8090)
- [ ] USB Capture / Screen Capture aktif
- [ ] WLED controller yapılandırıldı (IP, UDP port 19446)
- [ ] WLED → Sync Settings → Receive: ON
- [ ] Smoothing: OFF (gecikme yok)
- [ ] Test: Ekranda kırmızı sahne → WLED kırmızı (<16ms)
- [ ] Test: Ekranda mavi sahne → WLED mavi
- [ ] Test: Netflix film → oda ekranın rengini yansıtıyor
- [ ] `dynamic_stadium_atmosphere.yaml` HA'a yüklendi
- [ ] `agentic_media_orchestrator.py` Pi 4'te çalışıyor
- [ ] `media_companion_prompt.md` Jarvis system prompt'a eklendi