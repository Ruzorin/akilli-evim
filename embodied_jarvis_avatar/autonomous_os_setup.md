# embodied_jarvis_avatar — Autonomous OS Kurulum ve Edge Yapılandırma Rehberi

> Raspberry Pi 4'e Autonomous OS kurulumu — "beyin" Cloud VPS'te, Pi sadece "gövde"

---

## 🏗️ Mimari: Beyin (Cloud) ↔ Gövde (Edge)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD VPS (Beyin)                         │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Home Assist. │  │ OpenClaw     │  │ DeepSeek V4-Pro   │  │
│  │ (Otomasyon)  │  │ (Agentic RT) │  │ + MiniMax Speech  │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────┬───────┴────────────────────┘            │
│                   │ MQTT Broker (1883)                       │
│                   │ Tailscale VPN (100.x.x.x)                │
└───────────────────┼─────────────────────────────────────────┘
                    │
              ══════╪══════ Tailscale şifreli tünel
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              RASPBERRY PI 4 (Gövde — Edge)                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Autonomous OS (HAL)                      │   │
│  │                                                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐   │   │
│  │  │ motion  │ │ vision  │ │  audio  │ │  light   │   │   │
│  │  │ (servo) │ │ (cam)   │ │ (mic)   │ │ (WS2812) │   │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └─────┬────┘   │   │
│  │       │           │           │            │         │   │
│  │  ┌────▼───────────▼───────────▼────────────▼────┐   │   │
│  │  │           MQTT Bridge (system/network)        │   │   │
│  │  │     Pi sensör verisi → Cloud VPS              │   │   │
│  │  │     Cloud VPS komutları → Pi aktüatör         │   │   │
│  │  └───────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │ PCA9685 │ │ Pi Cam  │ │ INMP441 │ │ WS2812  │         │
│  │ (I2C)   │ │ (CSI-2) │ │ (I2S)   │ │ (SPI)   │         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Mantık:**
- Pi KENDİ karar vermez — sadece sensör verisi toplar ve motor komutları uygular
- Beyin (Cloud VPS) tüm AI kararlarını verir (DeepSeek, MiniMax, HA otomasyonları)
- MQTT + Tailscale ile düşük gecikmeli, şifreli haberleşme

---

## 📦 Adım 1: Raspberry Pi OS Kurulumu

```bash
# 1. Raspberry Pi Imager ile 64-bit Raspberry Pi OS Lite (Bookworm) yaz
#    → Headless (desktop yok — sadece terminal)

# 2. SSH ve I2C/I2S/SPI aktif et
sudo raspi-config
# Interface Options → SSH → Enable
# Interface Options → I2C → Enable
# Interface Options → SPI → Enable
# Interface Options → Camera → Enable

# 3. Sistem güncelle
sudo apt update && sudo apt upgrade -y

# 4. Python ve gerekli paketler
sudo apt install -y python3-pip python3-venv git i2c-tools v4l-utils

# 5. I2C cihazlarını doğrula
sudo i2cdetect -y 1
# PCA9685 adresi 0x40 görünmeli
```

---

## 📦 Adım 2: Tailscale VPN Kurulumu

```bash
# Tailscale kur (Pi ↔ Cloud VPS şifreli tünel)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Pi'nin Tailscale IP'sini not et (100.x.x.x formatı)
tailscale ip -4

# Cloud VPS'ten Pi'ye ping at
# (VPS terminalinde): ping 100.x.x.x (Pi IP)
```

---

## 📦 Adım 3: Autonomous OS Kurulumu

```bash
# Autonomous OS repo'sunu klonla
cd /opt
sudo git clone https://github.com/autonomous-ai/autonomous-os.git
cd autonomous-os

# Python bağımlılıkları (HAL katmanı)
python3 -m venv .venv
source .venv/bin/activate
pip install -r hal/requirements.txt

# Go sistem servisleri (cross-compile gerekirse Cloud VPS'te derle)
# Pi üzerinde direkt derleme yavaş olabilir
go build -o system-server ./system/

# HAL Python servisini başlat
cd hal
uvicorn main:app --host 0.0.0.0 --port 5001 --reload
```

---

## 📦 Adım 4: Özel DEVICE.md Oluşturma

Autonomous OS'in "declaration-driven mounting" prensibi:
Cihaz `DEVICE.md` dosyası hangi capability'leri olduğunu bildirir,
OS boot'ta sadece o capability'leri mount eder.

**Bizim DIY lambamız için:** `embodied_jarvis_avatar/DEVICE.md` dosyası
Autonomous OS'in `devices/` klasörüne kopyalanır:

```bash
# DIY lamba cihazını Autonomous OS'e tanıt
cp /opt/akilli-evim/embodied_jarvis_avatar/DEVICE.md \
   /opt/autonomous-os/devices/jarvis-lamp/DEVICE.md
cp /opt/akilli-evim/embodied_jarvis_avatar/SOUL.md \
   /opt/autonomous-os/devices/jarvis-lamp/SOUL.md
cp /opt/akilli-evim/embodied_jarvis_avatar/SAFETY.md \
   /opt/autonomous-os/devices/jarvis-lamp/SAFETY.md
```

---

## 📦 Adım 5: Özel Motion Driver (MG996R + PCA9685)

Autonomous OS'in HAL motion driver'ı pluggable:
`DEVICE.md`'deki `driver:` field'ı motion backend'i seçer.

Orijinal Lamp Feetech bus servo kullanır. Biz MG996R + PCA9685 kullanıyoruz
→ özel driver yazmalıyız.

```bash
# Özel driver'ı Autonomous OS HAL'a ekle
cp /opt/akilli-evim/embodied_jarvis_avatar/embodied_lamp_driver.py \
   /opt/autonomous-os/hal/drivers/motors/pca9685_driver.py

# MotionService protocol'üne uyduğundan emin ol
# (hal/drivers/motors/base.py'deki MotionService protocol'ünü implement et)
```

**Driver factory'ye kaydet:**
`/opt/autonomous-os/hal/drivers/motors/factory.py` dosyasına:
```python
from .pca9685_driver import PCA9685MotionService

def get_motion_service(driver_name: str):
    if driver_name == "pca9685":
        return PCA9685MotionService()
    elif driver_name == "feetech":
        return FeetechMotionService()
    # ...
```

---

## 📦 Adım 6: MQTT Bridge Yapılandırması

Pi (gövde) ↔ Cloud VPS (beyin) haberleşmesi MQTT ile:

```bash
# Mosquitto MQTT client kur (Pi üzerinde)
sudo apt install -y mosquitto-clients

# Autonomous OS system/network manager config
# /opt/autonomous-os/system/network/config.yaml
```

```yaml
# MQTT Bridge Konfigürasyonu
mqtt:
  broker: "100.x.x.x"  # Cloud VPS Tailscale IP
  port: 1883
  client_id: "jarvis-lamp-edge"

  # Pi → Cloud (sensör verisi)
  publish_topics:
    - "jarvis/lamp/camera/frame"      # Kamera karesi (base64)
    - "jarvis/lamp/audio/input"       # Mikrofon sesi (PCM chunks)
    - "jarvis/lamp/posture/angle"     # Postür açısı (MediaPipe)
    - "jarvis/lamp/presence"          # Varlık algılama
    - "jarvis/lamp/status"            # Cihaz durumu (heartbeat)

  # Cloud → Pi (komutlar)
  subscribe_topics:
    - "jarvis/lamp/motion/command"    # Servo hareket komutu
    - "jarvis/lamp/light/command"     # LED halkası komutu
    - "jarvis/lamp/audio/output"      # Hoparlör sesi (PCM)
    - "jarvis/lamp/safety/estop"      # Acil durdurma
```

---

## 📦 Adım 7: "Beyinsiz Gövde" Modu — Edge Configuration

Pi'nin "sadece gövde" olarak çalışması için Agentic Runtime DISABLE edilir:

```bash
# Autonomous OS config — runtime OFF, HAL ON
# /opt/autonomous-os/system/config.yaml
```

```yaml
# Edge Mode — Beyin Cloud'da, Pi sadece gövde
mode: "edge_body_only"

# Agentic Runtime DISABLE (beyin Cloud VPS'te)
runtime:
  enabled: false
  # Cloud VPS'teki OpenClaw runtime MQTT üzerinden komut gönderir

# HAL ENABLE (sensör/motor yerel)
hal:
  enabled: true
  port: 5001

# System Managers — sadece network ve sensing
system:
  intent: false      # Yerel intent yok (Cloud karar verir)
  network: true      # MQTT bridge aktif
  sensing: true      # Sensör routing aktif
  monitor: true      # Flow event bus
  healthwatch: true  # Sistem sağlığı
  ambient: false     # Ortam (Cloud kontrolünde)
  device: true       # Cihaz yönetimi

# Safety gate HER ZAMAN aktif (beyin kapansa bile)
safety:
  enabled: true
  # SAFETY.md sınırları deterministic olarak uygulanır
  # LLM üzerinden GEÇMEZ — doğrudan HAL'da enforce edilir
```

---

## 📦 Adım 8: Postür Analizi — Edge'de MediaPipe

Postür analizi Pi üzerinde YEREL olarak yapılır (bant genişliği tasarrufu):
Kamera karesi → MediaPipe Pose → servikal açı → MQTT → Cloud VPS

```bash
# MediaPipe kur (Pi üzerinde)
pip install mediapipe opencv-python

# Postür analizi daemon'ını başlat
python3 /opt/akilli-evim/embodied_jarvis_avatar/posture_shield_daemon.py
```

**Neden Pi'de (Cloud'da değil)?**
- Kamera karesi 1080p = ~6MB/kare → Tailscale üzerinden göndermek yavaş
- MediaPipe Pose Pi 4'te 15-20 FPS çalışır → yeterli
- Sadece AÇI değeri (float) MQTT ile gönderilir → ~20 byte/kare

---

## 📦 Adım 9: Sistem Servisleri (systemd)

```bash
# Autonomous OS HAL servisi
sudo tee /etc/systemd/system/autonomous-hal.service << 'EOF'
[Unit]
Description=Autonomous OS HAL (Jarvis Lamp)
After=network.target

[Service]
ExecStart=/opt/autonomous-os/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 5001
WorkingDirectory=/opt/autonomous-os/hal
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Postür analizi daemon
sudo tee /etc/systemd/system/posture-shield.service << 'EOF'
[Unit]
Description=Posture Shield Daemon (MediaPipe)
After=autonomous-hal.service

[Service]
ExecStart=/opt/autonomous-os/.venv/bin/python3 /opt/akilli-evim/embodied_jarvis_avatar/posture_shield_daemon.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable autonomous-hal posture-shield
sudo systemctl start autonomous-hal posture-shield
```

---

## 🔄 Veri Akışı Özeti

### Sensör → Beyin (Pi → Cloud)
```
Kamera → MediaPipe Pose → servikal açı → MQTT
  "jarvis/lamp/posture/angle": {"angle": 18.5, "severity": "tech_neck"}

Mikrofon → I2S → PCM chunks → MQTT
  "jarvis/lamp/audio/input": <base64 PCM 20ms chunk>

Kamera → base64 JPEG → MQTT (on-demand)
  "jarvis/lamp/camera/frame": {"image": "<base64>", "mode": "posture"}
```

### Beyin → Aktüatör (Cloud → Pi)
```
Cloud VPS (DeepSeek kararı) → MQTT
  "jarvis/lamp/motion/command": {"skill": "aim", "x": 0.3, "y": 0.5, "z": 0.4}

Cloud VPS (MiniMax ses) → MQTT
  "jarvis/lamp/audio/output": <base64 PCM 20ms chunk>

Cloud VPS (LED komutu) → MQTT
  "jarvis/lamp/light/command": {"effect": "amber_pulse", "brightness": 80}
```

### HAL Capability → Driver → Hardware
```
motion.move(θ₁, θ₂, θ₃, θ₄, θ₅)
  → PCA9685MotionService.move()
    → PCA9685.set_pwm(channel, on, off)
      → MG996R/SG90 servo pozisyon
```

---

## 🔗 İlgili Dosyalar

- [`hardware_and_kinematics.md`](hardware_and_kinematics.md) — BOM ve pin bağlantıları
- [`embodied_lamp_driver.py`](embodied_lamp_driver.py) — PCA9685 servo sürücü
- [`DEVICE.md`](DEVICE.md) — Autonomous OS cihaz tanımı
- [`SAFETY.md`](SAFETY.md) — Güvenlik sınırları
- [`config.yaml`](config.yaml) — Modül konfigürasyonu