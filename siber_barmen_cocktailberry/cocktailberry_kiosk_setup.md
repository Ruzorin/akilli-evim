# 🖥️ Modül 31: CocktailBerry Kurulum ve Kiosk Modu

> **Tek satır kurulum → tam ekran kokteyl arayüzü → Jarvis sesli komutla tetiklenir.**

---

## 📦 CocktailBerry Kurulumu

### Tek Satır Install

```bash
# Raspberry Pi 4 terminalinde (Raspberry Pi OS Bookworm 64-bit)
bash <(curl -sL https://raw.githubusercontent.com/AndreWohnsland/CocktailBerry/master/install.sh)
```

Bu script otomatik olarak:
- Python 3.11+ sanal ortam oluşturur
- CocktailBerry'yi klonlar
- Gereksinimleri yükler (`pip install -r requirements.txt`)
- GPIO erişim izinlerini ayarlar
- systemd servis olarak kaydeder
- Web UI'yi `http://raspberrypi.local:5000` portunda başlatır

### Manuel Kurulum (Alternatif)

```bash
# 1. Sistemi güncelle
sudo apt update && sudo apt upgrade -y

# 2. Gereksinimler
sudo apt install -y python3 python3-pip python3-venv git

# 3. CocktailBerry klonla
cd /opt
sudo git clone https://github.com/AndreWohnsland/CocktailBerry.git
cd CocktailBerry

# 4. Sanal ortam
python3 -m venv venv
source venv/bin/activate

# 5. Gereksinimler
pip install -r requirements.txt

# 6. GPIO izinleri
sudo usermod -aG gpio pi

# 7. Config dosyasını düzenle
nano config/ingredients.yaml
# → 10 pompanın içki adlarını ve akış hızlarını gir

# 8. Test çalıştır
python3 -m CocktailBerry

# 9. Web UI: http://raspberrypi.local:5000
```

### systemd Servis (Otomatik Başlatma)

```bash
sudo tee /etc/systemd/system/cocktailberry.service > /dev/null << 'EOF'
[Unit]
Description=CocktailBerry Cocktail Robot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/CocktailBerry
ExecStart=/opt/CocktailBerry/venv/bin/python3 -m CocktailBerry
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cocktailberry
sudo systemctl start cocktailberry
```

---

## 🖥️ Kiosk Modu — Tam Ekran UI

### Chromium Kiosk (Otomatik Tam Ekran Başlatma)

```bash
# 1. Chromium yükle (yoksa)
sudo apt install -y chromium-browser xserver-xorg xinit

# 2. Kiosk servis oluştur
sudo tee /etc/systemd/system/cocktailberry-kiosk.service > /dev/null << 'EOF'
[Unit]
Description=CocktailBerry Kiosk Mode
After=cocktailberry.service
Requires=cocktailberry.service

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-translate \
  --disable-features=TranslateUI \
  --disable-session-crashed-bubble \
  --disable-infobars \
  --autoplay-policy=no-user-gesture-required \
  --check-for-update-interval=31536000 \
  --simulate-critical-update-not-available \
  --app=http://localhost:5000
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cocktailberry-kiosk
sudo systemctl start cocktailberry-kiosk
```

### Otomatik Login (Boot'ta Grafik Ortam)

```bash
# 1. raspi-config
sudo raspi-config
# → System Options → Boot / Auto Login → Desktop Autologin

# 2. veya manuel:
sudo systemctl set-default graphical.target
```

### Ekran Oryantasyonu (Landscape)

```bash
# /boot/config.txt'e ekle
echo "display_rotate=0" | sudo tee -a /boot/config.txt
# 0 = landscape (yatay), 1 = 90°, 2 = 180°, 3 = 270°

# Reboot
sudo reboot
```

### Dokunmatik Kalibrasyon (Gerekirse)

```bash
# xinput ile dokunmatik aygıtı bul
DISPLAY=:0 xinput list

# Kalibrasyon aracı
sudo apt install -y xinput-calibrator
DISPLAY=:0 xinput_calibrator

# Çıktıyı /etc/X11/xorg.conf.d/99-calibration.conf'a kaydet
```

---

## 🔗 Jarvis MQTT Entegrasyonu

### CocktailBerry MQTT Bridge

CocktailBerry varsayılan olarak REST API sunar. MQTT entegrasyonu için basit bir bridge script:

```python
#!/usr/bin/env python3
"""CocktailBerry MQTT Bridge — Jarvis sesli komut → REST API → MQTT durum"""

import json
import subprocess
import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = "gl-mt3000.local"
MQTT_PORT = 1883
CB_API = "http://localhost:5000/api"

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected: {rc}")
    client.subscribe("jarvis/barmen/command")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    recipe = payload.get("recipe", "")
    
    if recipe:
        # CocktailBerry REST API'ye istek
        try:
            resp = requests.post(f"{CB_API}/make", json={"recipe": recipe}, timeout=120)
            if resp.status_code == 200:
                client.publish("jarvis/barmen/recipe_done", json.dumps({
                    "recipe": recipe,
                    "status": "success"
                }))
            else:
                client.publish("jarvis/barmen/error", json.dumps({
                    "message": f"CocktailBerry API hatası: {resp.status_code}"
                }))
        except Exception as e:
            client.publish("jarvis/barmen/error", json.dumps({
                "message": str(e)
            }))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="cocktailberry_bridge")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
```

### Bridge Servis

```bash
sudo tee /etc/systemd/system/cocktailberry-mqtt.service > /dev/null << 'EOF'
[Unit]
Description=CocktailBerry MQTT Bridge
After=cocktailberry.service
Requires=cocktailberry.service

[Service]
Type=simple
User=pi
ExecStart=/opt/CocktailBerry/venv/bin/python3 /opt/CocktailBerry/mqtt_bridge.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cocktailberry-mqtt
sudo systemctl start cocktailberry-mqtt
```

---

## 🧪 Test Senaryosu

```
1. Pi'yi boot et → CocktailBerry otomatik başlar (systemd)
2. 7" ekranda Chromium Kiosk → CocktailBerry UI tam ekran
3. Ekrandan "Negroni" seç → pompalar çalışır → kokteyl hazır
4. Jarvis'e "Bana Negroni yap" de:
   → MQTT "jarvis/barmen/command" {"recipe":"negroni"}
   → Bridge script REST API'ye iletir
   → CocktailBerry pompaları çalıştırır
   → Bitti → MQTT "jarvis/barmen/recipe_done"
   → Jarvis "Kokteyliniz hazır" der
   → Lamba (Modül 29) yeşil yanar + başını sallar
5. Acil stop: Ekrandaki "STOP" butonu → tüm röleler OFF
```

---

*Bu dosya, CocktailBerry kurulumunu, Kiosk modunu ve Jarvis MQTT entegrasyonunu detaylandır. Tek satır install.sh ile başlar, systemd + Chromium kiosk ile otonom çalışır.*
