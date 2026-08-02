# car_edge_ai_vision — Jetson Nano Donanım ve SDK Kurulumu

> **Modül 24: Car Edge-AI Vision (Nvidia Jetson Nano + OpenADAS + YOLO)**
> Ön cama yerleştirilen Jetson Nano + Sony IMX219 kamera ile canlı şerit takibi, nesne algılama ve trafik tabelası okuma.

---

## 🖥️ Nvidia Jetson Nano Developer Kit (4GB)

### Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | Edge-AI Bilgisayar | Nvidia Jetson Nano 4GB Dev Kit | 1 | ~$150 | 128 CUDA core, GPU |
| 2 | Kamera | Sony IMX219 CSI-2 (8MP) | 1 | ~$25 | Ön cam → dikiz aynası arkası |
| 3 | MicroSD | 64GB UHS-I U3 (A2) | 1 | ~$15 | JetPack imajı için |
| 4 | Güç | 5V 4A USB-C adaptör | 1 | ~$10 | Jetson Nano beslemesi |
| 5 | (Opsiyonel) | 5/7" IPS dokunmatik LCD | 1 | ~$35-50 | HMI ekranı |
| 6 | (Opsiyonel) | USB Wi-Fi dongle | 1 | ~$10 | Tailscale için (yerleşik Wi-Fi zayıf) |

> **Toplam maliyet: ~$200-250** (Jetson + kamera + SD + güç + opsiyonel LCD)

---

## 🔧 JetPack SDK Kurulumu (Adım Adım)

### Adım 1: JetPack İmajını İndir

```
1. Nvidia Developer hesabı oluştur (ücretsiz): https://developer.nvidia.com
2. JetPack SDK indir: https://developer.nvidia.com/embedded/jetpack
3. En son JetPack imajını seç (JetPack 4.6.x veya 5.x):
   - Ubuntu 18.04 (JetPack 4.6) veya Ubuntu 20.04 (JetPack 5.x)
   - İçerir: CUDA, cuDNN, TensorRT, OpenCV (GPU destekli)
4. İmaj dosyasını indir (.zip → .img)
```

### Adım 2: MicroSD'ye İmaj Yaz (BalenaEtcher)

```
1. BalenaEtcher indir: https://etcher.balena.io
2. 64GB MicroSD'yi bilgisayara tak
3. BalenaEtcher → "Flash from file" → JetPack .img dosyasını seç
4. "Select target" → MicroSD kartı seç
5. "Flash!" → yazma tamamla (~10-15 dk)
6. MicroSD'yi Jetson Nano'ya tak
```

### Adım 3: Jetson Nano İlk Açılış

```
1. HDMI monitör + USB klavye/mouse bağla
2. USB-C güç adaptörünü tak → Jetson açılır
3. Ubuntu kurulum sihirbazı:
   - Dil: English
   - Kullanıcı adı: jarvis
   - Şifre: belirle
4. NVIDIA License Agreement → Accept
5. NVIDIA L4T init → tamamla (~5 dk)
6. Masaüstü açılır
```

### Adım 4: CUDA ve TensorRT Doğrulama

```bash
# CUDA sürümünü kontrol et
nvcc --version
# Beklenen: CUDA 10.2 (JetPack 4.6) veya CUDA 11.4 (JetPack 5.x)

# TensorRT sürümünü kontrol et
dpkg -l | grep tensorrt
# Beklenen: libnvinfer6 / libnvonnxparsers6

# OpenCV (GPU destekli) sürümünü kontrol et
python3 -c "import cv2; print(cv2.__version__)"
# Beklenen: 4.1.1 (JetPack 4.6) veya 4.5+ (JetPack 5.x)

# GPU durumunu kontrol et
tegrastats
# Beklenen: GR3D_FREQ → GPU frekans, RAM → bellek kullanımı
```

### Adım 5: Performans Modu Ayarı

```bash
# Maksimum performans modu (10W, tüm CUDA core aktif)
sudo nvpmodel -m 0

# Doğrula
sudo nvpmodel -q
# Beklenen: NV Power Mode: MAXN

# Jetson saat hızını sabitle (throttle önleme)
sudo jetson_clocks

# Soğutma fanını maksimuma al
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm'
```

---

## 📷 Sony IMX219 CSI-2 Kamera Montajı

### Montaj Konumu

```
  ┌─────────────────────────────────────────────┐
  │                  ÖN CAM                       │
  │                                             │
  │  ┌───────────────────────────────────────┐ │
  │  │           Dikiz Aynası                 │ │
  │  │  ┌─────┐                              │ │
  │  │  │ 📷  │ ← IMX219 kamera              │ │
  │  │  │     │   dikiz aynası arkasına       │ │
  │  │  └─────┘   gizlenmiş                  │ │
  │  └───────────────────────────────────────┘ │
  │                                             │
  │  Kamera açısı: yola bakar (önde)            │
  │  FOV: 70° (geniş açı — şeritleri yakala)    │
  └─────────────────────────────────────────────┘
```

### Montaj Adımları

```
1. IMX219 kamera modülünü Jetson Nano'nun CSI-2 portuna bağla:
   - CSI kablo (15-pin flex) → Jetson Nano CSI camera port
   - Kablo yönü: metal kontaklar Jetson'a bakar
2. Kamerayı dikiz aynası arkasına monte et:
   - 3M VHB bant ile ayna arkasına yapıştır
   - Açı: yola bakar (önde, hafif aşağı ~10°)
   - FOV: 70° → iki şeridi de yakalar
3. Kablo yönetimi:
   - CSI kablo → A sütunu → torpido → Jetson Nano (eldivenlik altı)
4. Test:
   # Kamerayı test et
   nvgstcapture-1.0 --prev-res=3
   # Beklenen: ön cam görüntüsü ekranda
```

### Kamera Kalibrasyonu

```bash
# OpenCV kamera kalibrasyonu (distortion düzeltme)
python3 camera_calibration.py --input /dev/video0 --output calibration.yml

# Kalibrasyon parametreleri:
# - Camera matrix (fx, fy, cx, cy)
# - Distortion coefficients (k1, k2, p1, p2, k3)
# - Bu parametreler YOLO/OpenADAS'a yüklenir → görüntü düzeltme

# Test: düzeltme sonrası şeritler düz çizgi olmalı
python3 undistort_test.py --calibration calibration.yml
```

---

## 🌐 Tailscale VPN Kurulumu (Jetson → VPS)

```bash
# Tailscale kur
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# HA'a erişim
curl http://VPS_TAILSCALE_IP:8123/api/

# MQTT broker (GL-MT3000)
sudo apt install mosquitto-clients
mosquitto_pub -h gl-mt3000.local -t test -m "hello"
```

---

## ✅ Kurulum Kontrol Listesi

- [ ] JetPack SDK imajı 64GB MicroSD'ye yazıldı (BalenaEtcher)
- [ ] Jetson Nano ilk açılış tamamlandı (Ubuntu, kullanıcı, şifre)
- [ ] `nvcc --version` → CUDA sürümü görünüyor
- [ ] `dpkg -l | grep tensorrt` → TensorRT yüklü
- [ ] `python3 -c "import cv2"` → OpenCV (GPU) çalışıyor
- [ ] `sudo nvpmodel -m 0` → MAXN performans modu
- [ ] `sudo jetson_clocks` → saat hızları sabitlendi
- [ ] IMX219 kamera CSI-2 portuna bağlandı
- [ ] Kamera dikiz aynası arkasına monte edildi (yola bakar)
- [ ] `nvgstcapture-1.0` → kamera görüntüsü ekranda
- [ ] Kamera kalibrasyonu tamamlandı (distortion düzeltme)
- [ ] Tailscale kurulu → VPS'e bağlanıyor
- [ ] MQTT broker (GL-MT3000) ile haberleşiyor
- [ ] `open_adas_installation_script.sh` çalıştırıldı
- [ ] `adas_hmi_display_config.py` çalışıyor (30 FPS)
- [ ] `adas_home_assistant_bridge.py` MQTT gönderiyor
- [ ] Test: Şerit takibi → neon mavi/yeşil çizgiler ekranda
- [ ] Test: Ön araç → Bounding Box + FCW uyarısı
- [ ] Test: Tehlike → MQTT → WLED kırmızı strobe + sesli uyarı