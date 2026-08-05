# 🔧 INSTALLATION.md — Eksiksiz Kurulum Rehberi

> Bu dosya, tüm parçalar alındıktan sonra her modülün sırasıyla nasıl kurulacağını adım adım anlatır. Modüller bağımlılık sırasına göre dizilmiştir: önce altyapı, sonra sensörler, sonra atmosfer, en son yapay zeka.

---

## 📋 Kurulum Öncesi Hazırlık

### 0.0 Akım Koruması ve Güvenlik (Kıb-Tek Dalgalanmalarına Karşı)

> **⚠️ KRİTİK GÜVENLİK ADIMI — Bunu atlamayın!**
>
> Kıbrıs'ın elektrik şebekesi (Kıb-Tek) bazen çok dalgalı olabilir ve yurtların
> sigortaları eski olabilir. Hassas ESP32'ler, Raspberry Pi ve pahalı LCD monitör
> tek bir voltaj dalgalanmasında veya şimşek çakmasında yanabilir.
>
> **Tüm sistemin kalbini (GL-MT3000, Pi 4, Pi Zero, LCD monitör) kaliteli bir
> Akım Korumalı Priz'e (Surge Protector) bağlamalısın. Tüm o emeğin tek bir
> şimşek çakmasıyla çöp olmasın.**

```
1. Akım Korumalı Priz (Surge Protector) satın al:
   - APC SurgeArrest (6 çıkışli) — ~$25
   - Brennenstuhl (6 çıkışli) — ~$30
   - Tunçmatik (Türkiye/Kıbrıs uyumlu) — ~$35

2. (Opsiyonel ama önerilen) UPS (Kesintisiz Güç Kaynağı):
   - APC Back-UPS 600VA — ~$50-70
   - Şebeke kesintisinde GL-MT3000 + Pi 4'ü 10-15 dk çalıştırır
   - HA çökmesini, MQTT bağlantısının kopmasını engeller
   - Kıb-Tek kesintileri sık olduğundan önerilen

3. Kurulum:
   - Akım korumalı prizi duvar prizine tak
   - GL-MT3000 güç adaptörünü → Akım korumalı priz (Çıkış 1)
   - Raspberry Pi 4 güç adaptörünü → Akım korumalı priz (Çıkış 2)
   - Raspberry Pi Zero güç adaptörünü → Akım korumalı priz (Çıkış 3)
   - LCD monitör (Magic Mirror) güç → Akım korumalı priz (Çıkış 4)
   - Broadlink RM4 Mini güç → Akım korumalı priz (Çıkış 5)
   - (Opsiyonel) ESP32 USB güç → Akım korumalı priz (Çıkış 6)

4. (UPS kullanılıyorsa):
   - UPS'i duvar prizine tak
   - Akım korumalı prizi UPS çıkışına tak
   - GL-MT3000 + Pi 4 + Pi Zero → Akım korumalı priz (UPS üzerinden)

5. Test:
   - Akım korumalı prizin "Protected" LED'i yanıyor mu? Kontrol et
   - Eğer LED yanmıyorsa → priz hasar görmüş, değiştir
   - UPS test: Test butonuna bas → UPS moduna geçiyor mu?

6. Önemli:
   - ESP32'ler (sensör modülleri) ayrı USB adaptörleri ile çalışır
   - Bu adaptörleri de akım korumalı priz üzerinden besle
   - 220V güç kablolarını veri kablolarından ayrı tut (EMI)
   - Akım korumalı prizi mobilya arkasına gizle (kablo sleeve ile)
```

### 0.1 VPS Kurulumu (Home Assistant + Tailscale)

```
1. DigitalOcean/Hetzner'da Ubuntu 22.04 VPS oluştur (2 vCPU, 4GB RAM)
2. SSH ile bağlan:
   ssh root@VPS_IP
3. Docker kur:
   curl -fsSL https://get.docker.com | sh
4. Docker Compose kur:
   apt install docker-compose -y
5. Home Assistant Docker olarak başlat:
   mkdir -p /home/ha/config
   docker run -d \
     --name homeassistant \
     --restart=unless-stopped \
     -v /home/ha/config:/config \
     -e TZ=Europe/Istanbul \
     -p 8123:8123 \
     homeassistant/home-assistant:latest
6. Tailscale kur:
   curl -fsSL https://tailscale.com/install.sh | sh
   tailscale up
7. HA'a tarayıcıdan eriş: http://VPS_IP:8123
8. HA hesabı oluştur, temel ayarları yap
```

### 0.2 GL-MT3000 (Beryl AX) Kurulumu

```
1. GL-MT3000'ü prize tak, güç LED yanana kadar bekle
2. Telefonda WiFi ağına bağlan: GL-MT3000-xxx (şifre kutuda yazar)
3. Tarayıcıdan yönlendirici arayüzüne gir: http://192.168.8.1
4. Admin şifresi belirle
5. WiFi adı ve şifresi ayarla (örn: "JarvisNet")
6. Tailscale kur (GL-MT3000 arayüzünden):
   - More Settings → Tailscale → Login
   - VPS ile aynı Tailscale hesabına bağlan
7. MQTT Broker kur (GL-MT3000 arayüzünden):
   - More Settings → Advanced → Plugin → Mosquitto MQTT
   - Port: 1883
   - VPS'teki HA'tan GL-MT3000.local:1883 ile erişilebilir
```

### 0.3 Zigbee2MQTT Kurulumu

```
1. CC2652R Zigbee dongle'ı GL-MT3000'in USB portuna tak
2. VPS'te Zigbee2MQTT Docker olarak kur:
   docker run -d \
     --name zigbee2mqtt \
     --restart=unless-stopped \
     -v /home/z2m:/app/data \
     --device=/dev/ttyACM0 \
     -e TZ=Europe/Istanbul \
     koenkk/zigbee2mqtt:latest
3. Zigbee2MQTT ayarlarını yap (/home/z2m/configuration.yaml):
   mqtt:
     server: mqtt://GL-MT3000.local:1883
   serial:
     port: /dev/ttyACM0
4. HA'a Zigbee2MQTT entegrasyonu ekle:
   Settings → Devices → Add → Zigbee2MQTT
```

### 0.4 HACS (Home Assistant Community Store) Kurulumu

```
1. VPS'te HA terminal aç:
   docker exec -it homeassistant bash
2. HACS kur:
   wget -O - https://get.hacs.xyz | bash -
3. HA'ı yeniden başlat:
   docker restart homeassistant
4. HA → Settings → Devices → Add → HACS
5. GitHub hesabınla giriş yap
6. Aşağıdaki custom component'leri HACS'ten kur:
   - SmartIR (Modül 8)
   - Extended OpenAI Conversation (Modül 1)
   - ElevenLabs TTS (Modül 1)
   - LocalTuya (Modül 3, 9)
   - Alexa Media Player (Modül 5)
```

---

## 🧠 Modül 1: jarvis_core — Kurulum

### 1.1 Ses Hub (ESP32-S3 + INMP441)

```
1. INMP441'i ESP32-S3'e bağla:
   VDD  → 3.3V
   GND  → GND
   SD   → GPIO 4
   WS   → GPIO 5
   SCK  → GPIO 6
   L/R  → GND (sol kanal)
2. VDD hattına 100nF kondansatör paralel bağla
3. ESP32-S3'ü bilgisayara USB ile bağlan
4. ESPHome web arayüzünden (https://web.esphome.io) firmware yükle
5. WiFi'a (JarvisNet) bağla
6. MQTT'yi (GL-MT3000:1883) yapılandır
7. Komodin içine gizle (mikrofon dışarı bakar)
```

### 1.2 Raspberry Pi 4 (jarvis_core Python)

```
1. Raspberry Pi OS Lite (64-bit) MicroSD'ye yaz (Raspberry Pi Imager)
2. Pi 4'ü başlat, SSH ile bağlan
3. Python 3.13+ kurulu kontrol et: python3 --version (2026 standartı)
4. Gerekli kütüphaneleri kur (2026):
   pip install websockets asyncio httpx
   pip install opencv-python face-recognition chromadb numpy pillow pypdf2 mediapipe
5. jarvis_core dosyalarını Pi'ye kopyala:
   scp -r jarvis_core/ pi@PI_IP:~/
6. API anahtarlarını config'e gir:
   - MiniMax (Speech 2.8 Turbo — sesten-sese, voice cloning)
   - DeepSeek (V4-Pro — ağır zeka, özet)
   - Qwen-VL (Max — görüntü analizi)
7. Voice Cloning referans ses dosyası hazırla:
   - 10 sn WAV/MP3 (Jarvis tonu — Paul Bettany veya Türkçe dublaj)
   - assets/jarvis_voice_reference.wav olarak kaydet
8. System prompt'u yükle (advanced_system_prompt_v2.md — karakter anayasası)
9. minimax_realtime_orchestrator.py'yi başlat (Core — sesten-sese):
   cd ~/jarvis_core
   python3 minimax_realtime_orchestrator.py
10. hybrid_brain_and_memory_manager.py'yi başlat (ayrı terminal — hafıza):
    python3 hybrid_brain_and_memory_manager.py
11. facial_memory_and_vector_db.py'yi başlat (ayrı terminal — yüz tanıma):
    python3 facial_memory_and_vector_db.py
10. systemd service oluştur (otomatik başlatma):
    sudo nano /etc/systemd/system/jarvis-core.service
    [Unit]
    Description=Jarvis Core 2.0
    After=network.target
    [Service]
    ExecStart=/usr/bin/python3 /home/pi/jarvis_core/zero_latency_voice_pipeline.py
    Restart=always
    User=pi
    [Install]
    WantedBy=multi-user.target
    sudo systemctl enable jarvis-core
    sudo systemctl start jarvis-core
```

### 1.3 HA Entegrasyonu

```
1. HA → Settings → Devices → Add → Extended OpenAI Conversation
2. OpenAI API key gir
3. openai_conversation_agent.yaml'ı configuration.yaml'a import et:
   openai_conversation: !include jarvis_core/openai_conversation_agent.yaml
4. ElevenLabs TTS yapılandır:
   tts:
     - platform: elevenlabs
       api_key: "YOUR_KEY"
       voice: "Adam"
5. master_orchestration_intents.yaml'ı HA'a yükle
6. autonomous_conversation_trigger.yaml'ı HA'a yükle
7. Test: "Jarvis" de → "Anlaşıldı efendim" cevabı gelmeli
```

---

## 🔘 Modül 2: hidden_triggers — Kurulum

### 2.1 Zigbee Mini Butonlar

```
1. Sonoff ZBMINI butonun pilini (CR2032) tak
2. Zigbee2MQTT arayüzüne gir (HA → Zigbee2MQTT)
3. "Permit Join" tıkla
4. Butonun eşleştirme tuşuna 5 sn bas → Zigbee2MQTT keşfeder
5. Butona "bedside_button" ve "desk_button" adı ver
6. Buton 1'i komodin arkasına 3M VHB bant ile yapıştır
7. Buton 2'yi masa altına yapıştır
8. invisible_orchestration_automations.yaml'ı HA'a yükle
9. Test: Tek tık → Lounge modu, Çift tık → Sinema, Basılı tut → Kapat
```

### 2.2 TTP223 Kapasitif Dokunmatik

```
1. TTP223'ü ESP32'ye bağla:
   VCC  → 3.3V
   GND  → GND
   I/O  → GPIO 4
2. TTP223'ü ahşap masa altına yapıştır (sensör pad'i ahşaba bakar)
3. (Kalın ahşap >10mm) Bakır folyo şerit lehimle → alan genişlet
4. ESP32'ye stealth_button_esphome.yaml'i yükle (ESPHome web)
5. WiFi + MQTT yapılandır
6. Kalibrasyon:
   - ESPHome log'larını izle (USB)
   - Ahşaba dokun → "Desk Hidden Touch: ON" gelmeli
   - Gelmiyorsa → ahşap çok kalın, bakır folyo ekle
   - Titreşimli → debounce artır (100ms → 200ms)
7. HA'da binary_sensor.desk_hidden_touch görünüyor mu kontrol et
8. invisible_orchestration_automations.yaml'daki Senaryo 2'yi test et:
   - Ahşaba 2 sn bas → Intimacy modu başlamalı
```

### 2.3 NFC Bardak Altlığı

```
1. NTAG215 etiketi bardak altlığı altına yapıştır
2. HA Companion App → Settings → NFC Tags → Write
3. Etiket adı: "nfc_coaster"
4. Telefona okut → HA tag ID oluşur
5. invisible_orchestration_automations.yaml'daki Senaryo 3'ü test et:
   - Telefonu bardak altına koy → müzik %15'e kısılmalı
```

---

## 🌌 Modül 3: space_projection — Kurulum

```
1. Tuya galaksi projeksiyon cihazını Tuya Smart app'ine ekle
2. WiFi'a (JarvisNet) bağla
3. Cihazı yatak başucuna, doğrudan yukarı bakacak şekilde yerleştir
4. Kitap/bitki arkasına gizle
5. Tuya IoT Platform'da (iot.tuya.com) proje oluştur, API key al
6. HA'a LocalTuya entegrasyonu ekle (HACS'ten)
7. LocalTuya'ya cihazı ekle (device_id, local_key)
8. tuya_projector_config.yaml'ı HA'a yükle
9. Yeşil lazeri KAPAT (switch.galaxy_projector_laser → OFF)
10. Motor hızını "slow" (%10) ayarla
11. Renk paletini "deep_blue" ayarla
12. Parlaklığı %30 ayarla
13. celestial_automations.yaml'ı HA'a yükle
14. Test: script.scene_deep_space çağır → yavaş nebula, derin mavi
```

---

## 🪞 Modül 4: magic_mirror — Kurulum

### 4.1 Donanım Montajı

```
1. LCD monitörün çerçevesini ve plastik kasasını sök (stripped)
2. Two-way mirror akriliği LCD'nin ön yüzüne yerleştir
3. LCD kenarlarını siyah bant ile kapat (ışık sızıntısı)
4. (Opsiyonel) Ahşap/siyah çerçeve ile kenarları kapat
5. Raspberry Pi Zero 2 W'yu aynanın arkasına gizle
6. LCD'yi akıllı prize tak, prizi ayna arkasındaki prize bağla
7. Aynayı duvara as, kabloları gizle
```

### 4.2 MagicMirror² Kurulumu

```
1. Raspberry Pi OS Lite'i MicroSD'ye yaz
2. Pi Zero'yu başlat, SSH ile bağlan
3. MagicMirror² kur:
   bash -c "$(curl -sL https://raw.githubusercontent.com/MichMich/MagicMirror/master/installers/raspberry.sh)"
4. MMM-Spotify modülünü kur:
   cd ~/MagicMirror/modules
   git clone https://github.com/skuethe/MMM-Spotify.git
   cd MMM-Spotify && npm install
5. MMM-MQTT modülünü kur:
   cd ~/MagicMirror/modules
   git clone https://github.com/shbatm/MMM-MQTT.git
   cd MMM-MQTT && npm install
6. magicmirror_config.js'yi ~/MagicMirror/config/config.js olarak kopyala
7. Spotify API bilgilerini ve MQTT broker adresini gir
8. custom.css'e "Calm Technology" stillerini ekle (beyaz yazı, siyah arka plan)
9. PM2 ile autostart:
   npm install pm2 -g
   pm2 start mm.sh
   pm2 startup && pm2 save
```

### 4.3 HA Otomasyonu

```
1. Akıllı prizi HA'a ekle (switch.magic_mirror_plug)
2. PIR sensörü (HC-SR501) ayna yakınına monte et → ESPHome ile HA'a ekle
3. mirror_presence_automation.yaml'ı HA'a yükle
4. Test: Aynaya yaklaş → priz açılır → 10-15sn sonra MagicMirror² görünür
5. Test: Uzaklaş → 1dk sonra priz kapanır → %100 ayna
```

---

## 🔊 Modül 5: spatial_audio — Kurulum

```
1. İki Echo Dot'u WiFi'a (JarvisNet) bağla (Alexa app)
2. Alexa app → Devices → Create Stereo Pair → Sol + Sağ seç
3. Hoparlörleri odanın çapraz köşelerine yerleştir (kulak hizasının altı)
4. Kitap/bitki arkasına gizle
5. HA → Settings → Devices → Add → Spotify
6. Spotify hesabınla giriş yap → media_player.spotify oluşur
7. HACS → Alexa Media Player kur → media_player.echo_dot_sol/sag oluşur
8. media_player_integration.yaml'ı HA'a yükle (media_player group)
9. dynamic_volume_automations.yaml'ı HA'a yükle
10. Spotify çalma listeleri oluştur (Deep R&B, Acoustic Morning, Lo-Fi vb.)
11. Playlist URI'lerini media_player_integration.yaml'daki template'e gir
12. Test: "Jarvis, modumuzu değiştir" → Spotify Deep R&B %20 fade-in
```

---

## 🛏️ Modül 6: underbed_lighting — Kurulum

### 6.1 Donanım

```
1. HLK-LD2410B'yi ESP32'ye bağla:
   VCC  → 5V (VIN)
   GND  → GND
   TX   → GPIO 16 (UART2 RX)
   RX   → GPIO 17 (UART2 TX)
2. COB LED'i MOSFET üzerinden ESP32'ye bağla:
   MOSFET Gate → GPIO 25 (PWM)
   MOSFET Drain → COB LED (-)
   MOSFET Source → GND
   COB LED (+) → 12V güç kaynağı (+)
3. COB LED'i silikon difüzör tüp içine yerleştir
4. LED şeridi yatak altına, kenara paralel monte et
5. LD2410'yu yatak kenarına, anten zemine bakacak şekilde monte et
```

### 6.2 ESPHome + HA

```
1. ld2410_bed_radar_esphome.yaml'i ESP32'ye yükle (ESPHome web)
2. WiFi + MQTT yapılandır
3. HA'da binary_sensor.bed_feet_presence görünüyor mu kontrol et
4. Gate kalibrasyonu:
   - ESPHome log'larını izle
   - Yatak yanında dur → moving_distance < 2.25m olmalı
   - Yatak içine uzan → moving_distance > 2.25m olmalı (tetiklenmemeli)
   - Eşik yanlışsa → FEET_THRESHOLD değerini ayarla
5. night_routing_automations.yaml'ı HA'a yükle
6. Test: Gece yataktan kalk → COB LED %15 aç (3sn transition)
7. Test: Yatağa dön → 2dk sonra fade-out
```

---

## 🌅 Modül 7: morning_after — Kurulum

```
1. SwitchBot Curtain'i perde rayına tak (kornişe vidalama gerekmez)
2. SwitchBot app → WiFi'ya bağla → HA'a ekle (cover.smart_curtain)
3. Perdeyi kalibre et (tam açık / tam kapalı pozisyon)
4. sunrise_simulation.yaml'ı HA'a yükle (script.sunrise_simulation)
5. morning_orchestration_automation.yaml'ı HA'a yükle
6. input_datetime.morning_wake_time'ı HA'ta tanımla
7. Hava durumu sensörü ekle (weather.home)
8. Test: "Jarvis, sabah 9'da uyandır" → input_datetime ayarlanır
9. Test: 9:00'dan 10 dk önce WLED gündoğumu + perde %20 başlamalı
10. Test: 9:00'da perde %100 + barista_mode tetiklenmeli
```

---

## 📡 Modül 8: invisible_remote — Kurulum

### 8.1 Broadlink RM4 Mini

```
1. Broadlink RM4 Mini'yi WiFi'a bağla (Broadlink app)
2. HA → Settings → Devices → Add → Broadlink
3. remote.broadlink_rm4_mini entity'si oluşur
4. Broadlink app → "Learn" modu:
   - TV Power tuşuna bas → kod kaydet
   - HDMI 1, Volume Up/Down, Mute → her birini kaydet
5. Öğrenilen kodları smartir_climate_media.yaml'daki script'lere kopyala
```

### 8.2 SmartIR (Klima)

```
1. HACS → SmartIR kur
2. Klima marka/model kodu bul:
   https://github.com/smartHomeHub/SmartIR → codes/climate/
3. Kodu indir → /config/custom_components/smartir/codes/climate/ koy
4. smartir_climate_media.yaml'daki device_code değerini güncelle
5. climate.room_ac entity'si HA'ta oluşur
6. Akıllı prizi klimaya tak (power_sensor için)
7. stealth_automations.yaml'ı HA'a yükle
8. Test: "Jarvis, sıcak" → klima 20°C quiet
9. Test: Film modu → TV aç + HDMI + ışıklar lacivert
```

---

## 🌿 Modül 9: smart_diffuser — Kurulum

```
1. Tuya difüzörü Tuya Smart app'ine ekle → WiFi'a bağla
2. Tuya IoT Platform'da API key al (Modül 3 ile aynı)
3. LocalTuya'ya difüzörü ekle (device_id, local_key)
4. Entity'leri tanımla:
   - switch.smart_diffuser_power (DP 1)
   - select.diffuser_mist_level (DP 2)
   - light.diffuser_led (DP 4 — HER ZAMAN KAPALI)
   - select.diffuser_timer (DP 6)
5. tuya_local_integration.yaml'ı HA'a yükle
6. Difüzör RGB ışığını KAPAT (light.diffuser_led → OFF)
7. Esans yağlarını hazırla:
   - Sandalağacı + Amber karışımı (60/40) → Pre-Arrival
   - Sandalağacı + Ylang-Ylang (60/40) → Date/Lounge
   - Ylang-Ylang + Sandalağacı (50/50) → Intimacy
8. diffuser_automations.yaml'ı HA'a yükle
9. GPS zone (zone.home) HA'ta tanımla → HA Companion App GPS izin ver
10. Test: Eve 100m yaklaş → difüzör "high" aç + RGB kapat
11. Test: Intimacy modu → difüzör "low" aç
```

---

## 💡 Modül 10: audio_reactive_wled — Kurulum

### 10.1 Donanım

```
1. INMP441'i ESP32'ye bağla:
   VDD  → 3.3V
   GND  → GND
   SD   → GPIO 32
   WS   → GPIO 15
   SCK  → GPIO 14
   L/R  → GND
2. VDD'ye 100nF kondansatör paralel bağla
3. WS2812B LED şeridi bağla:
   5V   → Harici 5V 4A güç kaynağı (+)
   GND  → Ortak GND
   DIN  → GPIO 2 (330Ω direnç seri)
4. LED şeridi alüminyum + mat akrilik difüzör profile yerleştir
5. Difüzör profilini tavan pervazına veya yatak başı arkasına monte et
```

### 10.2 WLED Firmware

```
1. https://install.wled.me/ → Audio Reactive sürümü seç
2. ESP32'ye flash et
3. WLED web arayüzüne gir (http://wled-ambient.local)
4. WiFi yapılandır (JarvisNet)
5. User Settings → Audio → I2S mikrofon pin'leri:
   SD: GPIO 32, WS: GPIO 15, SCK: GPIO 14
6. wled_api_presets.json'daki 4 preset'i WLED'e yükle:
   - WLED arayüzü → Presets → Import JSON
7. HA'a WLED entegrasyonu ekle → light.wled_ambient oluşur
8. audio_wled_automation.yaml'ı HA'a yükle
9. RESTful command'leri (wled_date_lounge, vb.) HA'a tanımla
10. Test: Spotify çal → WLED "Date Lounge" preset (amber/kırmızı, bas odaklı)
11. Test: Müzik dur → WLED "Rest Idle" (loş amber)
```

---

## ☕ Modül 11: barista_mode — Kurulum

```
1. Kahve makinesini akıllı prize tak (Shelly Plug s)
2. Shelly'yi WiFi'a bağla → HA'a ekle (switch.coffee_machine_plug)
3. sensor.coffee_machine_power entity'si HA'ta görünüyor mu kontrol et
4. Kahve makinesinin güç anahtarını ON konumunda bırak
5. NTAG215 NFC etiketi masanın altına yapıştır
6. HA Companion App → NFC Tags → Write → "nfc_coffee_table"
7. Spotify'da "Lo-Fi Coffee Shop" çalma listesi oluştur → URI'yi al
8. barista_automation.yaml'daki playlist URI'sini güncelle
9. barista_automation.yaml'ı HA'a yükle
10. smart_readiness_sensor.yaml'ı HA'a yükle
11. Çift cidarlı fincanları, şurupları ve kahveyi hazırla
12. Test: NFC'ye telefon dokundur → priz aç + ışıklar %30 amber + müzik %15
13. Test: Güç 1000W'a çıkıp 20W'a düşerse → "Espresso ready" anonsu
```

---

## ❤️‍🔥 Modül 12: intimacy_sync_mode — Kurulum

### 12.1 Donanım

```
1. MPU6050'yi ESP32'ye bağla:
   VCC  → 3.3V
   GND  → GND
   SDA  → GPIO 21
   SCL  → GPIO 22
2. Sensörü yatak orta kirişine, dikey (Z ekseni yukarı) monte et
3. Sensör ile kiriş arasına 1-2mm köpük şerit koy (izolasyon)
4. Kabloları kiriş boyunca sabitle (sallanmasın)
5. ESP32'yi kirişe gizle, anteni dışarı yönlendir
```

### 12.2 ESPHome + HA

```
1. bed_sensor_esphome.yaml'i ESP32'ye yükle (ESPHome web)
2. WiFi + MQTT yapılandır
3. HA'da sensor.bed_activity_level görünüyor mu kontrol et
4. Gate kalibrasyonu:
   - Yatakta otur → activity_level düşük olmalı
   - Ritmik hareket → activity_level 50+ olmalı
   - Tek seferlik dönme → activity_level 0'a dönmeli (ritmik değil)
5. intimacy_automation.yaml'ı HA'a yükle
6. Test: "Jarvis, romantik mod" → WLED kırmızı + müzik R&B + klima 20°C
7. Test: Ritmik hareket → WLED nabız hızı artmalı
8. Test: Hareket dur → WLED sabit kırmızıya dönmeli
```

---

## 🧑‍🍳 Modül 13: vision_chef_assistant — Kurulum

### 13.1 Kamera Montajı

```
1. TP-Link Tapo C200'ü WiFi'a bağla (Tapo app)
2. Tapo app → Settings → RTSP → etkinleştir (kullanıcı/şifre belirle)
3. Kamerayı mutfak dolabı altına, 45° aşağı bakacak şekilde yapıştır
4. SADECE tezgahı gördüğünü kontrol et (oda görünmemeli)
5. USB güç kablosunu dolap arkasından gizle
6. RTSP URL'yi test et (VLC player):
   rtsp://admin:password@192.168.1.107:554/stream1
```

### 13.2 Python Script

```
1. Raspberry Pi 4'te (Modül 1 ile aynı) gerekli kütüphaneleri kur:
   pip install opencv-python openai asyncio httpx
2. vision_frame_analyzer.py'yi Pi'ye kopyala:
   scp vision_chef_assistant/vision_frame_analyzer.py pi@PI_IP:~/
3. RTSP URL ve OpenAI API key'i config'e gir
4. chef_persona_system_prompt.yaml'deki system_prompt'u yükle
5. Script'i başlat:
   python3 vision_frame_analyzer.py
6. systemd service oluştur (otomatik başlatma)
7. Ocak prizini akıllı prize tak (sensor.stove_power)
```

### 13.3 HA Otomasyonu

```
1. kitchen_automations.yaml'ı HA'a yükle
2. RESTful command'leri (chef_analyze_recipe, vb.) HA'a tanımla
3. Mutfak Zigbee butonunu Zigbee2MQTT'e ekle (sensor.kitchen_button_action)
4. Test: "Jarvis, bunlardan ne çıkar?" → kamera kare al → GPT-4o Vision → tarif
5. Test: Ocak açık + oda boş 10dk → güvenlik analizi → uyarı
6. Test: Mutfak butonu çift tık → komik durum güncellemesi
```

---

## 📚 Modül 15: immersive_language_tutor — Kurulum

> **Ekstra donanım GEREKMEZ!** Bu modül tamamen yazılım tabanlıdır.
> Mevcut Jarvis Core (Modül 1), WLED (Modül 10), Spatial Audio (Modül 5),
> Magic Mirror (Modül 4) ve klima (Modül 8) altyapısını kullanır.

### 15.1 HA Otomasyonu

```
1. study_environment_automation.yaml'ı HA'a yükle
2. input_select.language_tutor_target ve input_boolean.language_tutor_active
   HA'ta tanımlandı mı kontrol et
3. NFC "Study Book" etiketi oluştur:
   - HA Companion App → NFC Tags → Write → "nfc_study_book"
   - Etiketi masadaki NFC okuyucuya yapıştır
4. (Opsiyonel) Difüzöre odaklanma esansı (biberiye/limon) doldur
   - select.diffuser_scene → "focus" sahnesi tanımla
```

### 15.2 Jarvis Dil Eğitmeni Kişiliği

```
1. tutor_persona_prompt.yaml'deki system_prompt'u jarvis_core Python'a tanımla
2. MQTT "jarvis/persona/switch" topic'ini dinleyen kod ekle:
   - "language_tutor" → Dil eğitmeni system prompt'u yükle
   - "default" → Varsayılan Jarvis system prompt'a dön
3. zero_latency_voice_pipeline.py'de persona switching desteği ekle
4. Test: "Jarvis, Fransızca çalışmaya başlayalım" →
   - WLED soğuk beyaz (5000K)
   - Klima 21°C
   - Lo-Fi %10
   - Jarvis: "Bienvenue. Aujourd'hui, nous parlons en français..."
```

### 15.3 Magic Mirror Kelime Modülü

```
1. Pi Zero'da MagicMirror modules dizinine MMM-Vocabulary klasörü oluştur:
   mkdir ~/MagicMirror/modules/MMM-Vocabulary
2. mirror_vocabulary_integration.js'yi MMM-Vocabulary.js olarak kopyala
3. vocabulary.json dosyası oluştur (100+ İngilizce-Fransızca kelime çifti)
4. magicmirror_config.js (Modül 4) modules dizisine MMM-Vocabulary ekle:
   {
     module: "MMM-Vocabulary",
     position: "bottom_bar",
     config: {
       updateInterval: 4 * 60 * 60 * 1000,
       wordsPerDay: 5,
       vocabularyFile: "modules/MMM-Vocabulary/vocabulary.json"
     }
   }
5. MMM-Vocabulary.css dosyasını oluştur (Calm Technology stilleri)
6. MagicMirror'ı yeniden başlat:
   pm2 restart mm
7. MQTT "jarvis/mirror/vocabulary" → "ON" gönder → kelime listesi görünür
8. Test: Aynaya bak → 5 İngilizce-Fransızca kelime çifti görünmeli
```

### 15.4 Test

```
1. "Jarvis, Fransızca çalışmaya başlayalım" →
   - WLED soğuk beyaz, klima 21°C, Lo-Fi %10, difüzör (odaklanma/kapalı)
   - Jarvis: "Bienvenue. Aujourd'hui, nous parlons en français."
   - Magic Mirror'da kelime listesi belirir
2. Türkçe konuşmayı dene → Jarvis "Let's stay in French, shall we?" der
3. Hata yap → doğal akış içinde düzeltme (sert değil, hissettirmeden)
4. "Çalışma modunu kapat" → ortam normale döner, Jarvis varsayılan kişiliğe döner
5. 2 saat otomatik kapatma testi → "Good session. Rest your mind."
```

---

---

## 🧬 Modül 16: holistic_life_os — Kurulum

> **Ekstra donanım GEREKMEZ!** Mevcut akıllı saat, yatak radarı (Modül 6),
> kamera (Modül 13) ve HA altyapısını kullanır.

### 16.1 Takvim Entegrasyonu

```
1. HA → Settings → Devices → Add → CalDAV (veya Google Calendar)
2. Takvim hesabını yetkilendir (iCloud/Google/Nextcloud)
3. calendar.personal entity'si oluştu mu kontrol et
4. Test: sensor.calendar_personal_event_1 → sonraki etkinlik
```

### 16.2 Akıllı Saat Entegrasyonu

```
1. iPhone Shortcuts / Android Automation oluştur:
   - Her sabah 07:00'de çalış
   - Apple Health / Google Fit'ten veri al:
     * Uyku süresi, derin uyku, uyanma sayısı
     * Adım sayısı, dinlenme nabzı, aktif kalori
   - HA webhook'a POST gönder: http://HA_URL/api/webhook/health_data
2. HA'da webhook trigger ile sensor'lar oluştur:
   - sensor.sleep_hours, sensor.deep_sleep_hours
   - sensor.daily_steps, sensor.resting_hr
   - sensor.active_calories
3. Test: Saatten veri geldi mi kontrol et
```

### 16.3 Kan Tahlili PDF Analizi

```
1. Raspberry Pi 4'te PyPDF2 kur:
   pip install pypdf2
2. HA → File upload → PDF → /config/uploads/blood_test.pdf
3. Python script: PDF → metin çıkar → Gemini 3.5'e gönder
4. Gemini 3.5: değerleri referanslarla karşılaştır → öneriler
5. Sonuç MQTT'ye publish: jarvis/health/blood_analysis
6. ChromaDB'ye kaydet (geçmiş takip)
7. Test: PDF yükle → Jarvis "D vitamini düşük, demir eksik" der
```

### 16.4 Biometric Fusion Engine

```
1. biometric_fusion_engine.py'yi Raspberry Pi 4'e kopyala:
   scp holistic_life_os/biometric_fusion_engine.py pi@PI_IP:~/
2. Gerekli kütüphaneleri kur:
   pip install httpx asyncio
3. HA_URL, HA_TOKEN, Google OAuth bilgilerini config'e gir
4. systemd service oluştur (otomatik başlatma)
5. Test: Engine çalıştır → uyku + sağlık verisi birleştir → Jarvis'e gönder
6. Test: Kötü uyku + esnetilebilir etkinlik → "10:00 toplantısını 11:00'e kaydırmamı ister misin?"
```

### 16.5 HA Otomasyonu

```
1. routine_and_medical_tracker.yaml'ı HA'a yükle
2. input_boolean.holistic_life_os_active → ON
3. Takvim sensor'ları (calendar.personal) HA'ta görünüyor mu kontrol et
4. Magic Mirror brifing modülü (MMM-Briefing) ekle (opsiyonel)
5. Test: Sabah uyanınca → Magic Mirror'da takvim + ilaç checklist
6. Test: Gece 02:00 + ışıklar açık + sabah sınav → "Uyku moduna geçiyorum"
7. Test: "Bu yemeği kalori takibime ekle" → Vision API → kalori bilgisi
```

### 16.6 Sağlık Koçu Prompt

```
1. life_coach_prompt_extension.md'yi Jarvis Core 3.0'a yükle:
   orchestrator.load_system_prompt("health_coach", prompt)
2. Gemini 3.5 modeline bu prompt gönderilir (sağlık verisi analizi)
3. agi_system_prompt_2026.md'ye extension olarak ekle
4. Test: "Jarvis, kan değerlerim nasıl?" → "D vitamini düşük. Güneşe çıkın."
5. Test: "Jarvis, bugün ne yapmalıyım?" → takvim + sağlık + tavsiye
```

---

## 🎬 Modül 17: hyperion_media_sync — Kurulum

### 17.1 Hyperion.ng Kurulumu

```
1. Raspberry Pi 4'e Raspberry Pi OS Lite (64-bit) yaz
2. Hyperion.ng kur:
   curl -sSL https://apt.hyperion-project.org/hyperion.pub.key | gpg --dearmor | sudo tee /usr/share/keyrings/hyperion.pub.gpg >/dev/null
   echo "deb [signed-by=/usr/share/keyrings/hyperion.pub.gpg] https://apt.hyperion-project.org/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hyperion.list
   sudo apt update && sudo apt install hyperion -y
3. Hyperion web arayüzü: http://PI_IP:8090
4. USB HDMI grabber'ı Pi'ye bağla (UCV007 / MS2109)
5. HDMI splitter: kaynak → splitter → TV + grabber
6. Hyperion → Input → USB Capture seç
7. Frame rate: 30 FPS, Smoothing: OFF (gecikme yok)
```

### 17.2 WLED UDP Senkronizasyonu

```
1. Hyperion → LED Hardware → Controller type: "WLED"
2. WLED IP: 192.168.1.104 (WLED ESP32 IP'si)
3. UDP port: 19446, Protocol: "WLED" (DRGB mode)
4. LED sayısı ve düzeni: ekran kenarına göre
5. WLED → Sync Settings → Receive: ON, UDP Port: 19446
6. Test: Ekranda kırmızı → WLED kırmızı (<16ms)
7. Test: Netflix film → oda ekranın rengini yansıtıyor
```

### 17.3 Stadyum Modu + Agentic Orchestrator

```
1. dynamic_stadium_atmosphere.yaml'ı HA'a yükle
2. agentic_media_orchestrator.py'yi Pi 4'e kopyala + systemd service
3. media_companion_prompt.md'yi Jarvis Core 3.0'a yükle
4. Test: "Jarvis, maç başlıyor" → Hyperion ON + takım renkleri + difüzör
5. Test: Blade Runner izle → 30sn sonra siberpunk atmosfer (neon pembe)
6. Test: Maç gol → "Güzel gol." (sonra sessiz)
7. Test: 2 saat sonra → Rest Idle + Hyperion OFF
```

---

---

## 📱 Modül 18: life_os_superapp — Kurulum

> **Ekstra donanım GEREKMEZ!** Mevcut HA PWA + HACS + ESP32-S3 (Modül 1) kullanır.

### 18.1 PWA Kurulumu

```
1. Telefonda Safari (iOS) veya Chrome (Android) ile HA'ı aç
2. Paylaş → "Ana Ekrana Ekle" → İsim: "Jarvis"
3. Ana ekranda Jarvis ikonu oluşur → tam ekran PWA
```

### 18.2 HACS Custom Cards

```
1. HACS → Frontend → Mushroom → Install
2. HACS → Frontend → Bubble Card → Install
3. HA → Settings → Dashboards → Resources → Mushroom + Bubble ekle
4. Jarvis Dark tema tanımla (configuration.yaml → frontend: themes:)
```

### 18.3 SuperApp Dashboard

```
1. superapp_lovelace_dashboard.yaml'ı HA Lovelace'e yükle
   (Raw Configuration Editor ile yapıştır veya YAML mode)
2. Dashboard'da 3 bölüm görünmeli:
   - Üst: Karşılama (günaydın + takvim)
   - Orta: Swipeable sekmeler (Ev kontrolü + Sağlık)
   - Alt: Spotify/Hyperion medya
3. Test: Sağa-sola kaydır → sekmeler değişir
4. Test: WLED/difüzör/klima kartları çalışır
5. Test: Sağlık sekmesi → uyku/kalori/nabız/adım/stres
```

### 18.4 AGI Chat Interface

```
1. agi_chat_interface.yaml'ı HA'a yükle
2. input_boolean.agi_chat_active → ON
3. MQTT topic'ler: jarvis/agi/chat_input, jarvis/agi/chat_output
4. multi_model_orchestrator.py chat_input'u dinlemeli
5. Test: Chat'ten "Bize cyberpunk ortamı yap" yaz → oda değişir
6. Test: Fotoğraf at + "Bunu kalori takibime ekle" → Vision API
```

### 18.5 Çağrı Yönlendirme

```
1. ESP32-S3'e Bluetooth Proxy ekle (ESPHome):
   bluetooth_proxy:
     active: true
2. HA Companion App → Settings → Sensors → Phone State → etkinleştir
3. sensor.phone_state sensörü HA'ta görünüyor mu kontrol et
4. call_routing_automation.yaml'ı HA'a yükle
5. input_boolean.call_routing_active → ON
6. Test: Telefona çağrı gel → müzik durakla + WLED mavi strobe
7. Test: Çağrı cevapla → WLED sakin mavi + BT Proxy ON
8. Test: Çağrı bit → atmosfer geri döner + müzik devam
```

---

---

## 📞 Modül 19: call_routing_and_ceo_mode — Kurulum

### 19.1 ESP32-S3 Bluetooth Proxy + HFP

```
1. Modül 1'deki ESP32-S3 ESPHome konfigürasyonuna ekle:
   bluetooth_proxy:
     active: true
     services:
       - service_uuid: "111E"  # HFP UUID
2. I2S DAC (MAX98357A) bağla:
   BCLK → GPIO 42, LRCLK → GPIO 41, DIN → GPIO 40
3. I2S DAC'ı hoparlöre bağ (çağrı sesi)
4. ESPHome firmware güncelle
5. Test: Telefon BT → ESP32-S3 bağlan → HFP aktif
```

### 19.2 CEO Çağrı Otomasyonu

```
1. ceo_call_routing_automation.yaml'ı HA'a yükle
2. hands_free_interraction_script.yaml'ı HA'a yükle
3. input_boolean.ceo_call_mode_active → ON
4. input_number.pre_call_volume tanımlı mı kontrol et
5. HA Companion App → phone_call_state sensörü çalışıyor mu
6. VIP listesi: sensor.is_vip_caller template'ini kişiselleştir
7. Test: Telefona çağrı gel → müzik %5 + WLED beyaz/mavi + klima quiet
8. Test: VIP arıyor → "Önemli arama, [Ad] arıyor"
9. Test: Çağrı cevapla → BT Proxy ON + WLED Solid + "Eller serbest"
10. Test: Çağrı bit → müzik fade-in + WLED eski atmosfere + "Görüşme sona erdi"
```

---

---

## 🪞 Modül 20: magic_mirror_comm_and_grooming — Kurulum

### 20.1 Donanım Montajı

```
1. USB web kamera (Logitech C270) ayna çerçevesine gizle:
   - Two-way mirror akrilik kenarında şeffaf alan bırak
   - Kamera lensi arkaya yapışık → "kenar süsü" gibi görünür
2. USB mikrofon ayna arkasına monte et
3. Mini hoparlör ayna arkasına monte et (TTS + arama sesi)
4. USB Hub → Pi Zero 2 W → kamera + mikrofon
5. Test: lsusb → kamera + mikrofon görünüyor mu
6. Test: fswebcam -d /dev/video0 test.jpg → fotoğraf al
7. Test: arecord test.wav → mikrofon testi
```

### 20.2 Görüntülü Arama (WebRTC)

```
1. Pi Zero'da aiortc kur:
   pip install aiortc opencv-python asyncio httpx
2. whatsapp_video_integration_module.py'yi Pi Zero'ya kopyala
3. systemd service oluştur (otomatik başlatma)
4. HA'a REST command ekle: mirror_capture_snapshot
5. Test: "Jarvis, aramayı aynadan aç" → kamera + mikrofon aktif
6. Test: Gelen arama → aynada "Gelen Arama: [Kişi]" bildirimi
```

### 20.3 Stil Koçu (GPT-5.6 Vision)

```
1. digital_grooming_coach_vision.yaml'ı HA'a yükle
2. digital_grooming_coach_module.yaml'ı HA'a yükle
3. input_boolean.grooming_coach_active → ON
4. input_boolean.grooming_protocol_active → ON
5. input_select.today_event_type tanımlı mı kontrol et
6. Takvim (calendar.personal) + hava durumu (weather.home) HA'ta aktif
7. Test: "Jarvis, kombin nasıl?" → snapshot → GPT-5.6 Vision → TTS
8. Test: "Bugün CEO görüşmesi var" → "Lacivert ceket giymelisin"
9. Test: Hava 5°C yağmur → "Mont + şemsiye öneririm"
```

### 20.4 Grooming Checklist UI

```
1. grooming_checklist_mirror_ui.js'yi MagicMirror modules dizinine kopyala:
   ~/MagicMirror/modules/MMM-Grooming-Checklist/MMM-Grooming-Checklist.js
2. MMM-Grooming-Checklist.css oluştur (Calm Technology stilleri)
3. magicmirror_config.js modules dizisine ekle:
   {
     module: "MMM-Grooming-Checklist",
     position: "bottom_right",
     config: { showGroomingScore: true, showRoutineChecklist: true }
   }
4. MagicMirror'ı yeniden başlat: pm2 restart mm
5. Test: Aynaya bak → sağ alt köşede checklist + kombin puanı
6. Test: Telefondan madde onayla → aynada silinir
```

---

## 🚗 Modül 21: car_knight_rider_core — Kurulum

### 21.1 Android Multimedya + Tailscale

```
1. Android Multimedya Ekranı'nı araca tak (ISO harness)
2. Play Store → HA Companion App + Tailscale indir
3. Tailscale → VPS ile aynı hesap → bağlan
4. HA Companion App → Tailscale IP → HA'a bağlan
5. Test: Araç içi ekranda HA dashboard görünüyor mu
```

### 21.2 OBD2 + Giant's Throne

```
1. ELM327 OBD2 adaptörünü direksiyon altı OBD2 portuna tak
2. Android → Bluetooth → ELM327 eşleştir
3. Torque/Car Scanner app kur → OBD2 verilerini oku
4. Webhook → HA → sensörler oluştur (RPM, hız, yakıt, sıcaklık)
5. giants_throne_automation.yaml'ı HA'a yükle
6. car_android_dashboard_config.yaml'ı HA Lovelace'e yükle
7. Test: Telefon aracın BT ağına bağlan → koltuk/direksiyon/ayna ayar
8. Test: "Jarvis, Blackout" → ekran karart + HUD
```

---

## 🔮 Modül 22: car_omniscience_copilot — Kurulum

```
1. IR kamera (FLIR One / Seek Thermal) Android ekranına USB-C ile bağla
2. OBD2 Wi-Fi adaptörü tak → Android'e bağlan
3. Akıllı saat → HA webhook → nabız/HRV verisi (Modül 16 ile paylaşımlı)
4. fatigue_and_ergonomic_guard.py'yi Pi 4'te çalıştır (systemd service)
5. predictive_maintenance_obd2.py'yi Pi 4'te çalıştır (systemd service)
6. g_force_and_driving_dynamics.yaml'ı HA'a yükle
7. Test: 2 saat sürüş → PERCLOS >%15 → "Yorgun görünüyorsunuz" + klima -2°C
8. Test: OBD2 yağ basıncı düşük → "500 km içinde yağ bakımı" kehaneti
9. Test: Yağmurlu zemin + viraj → "Kaygan zemin, yavaşlayın"
```

---

## 🌑 Modül 23: car_stealth_and_seduction — Kurulum

```
1. stealth_blackout_protocol.yaml'ı HA'a yükle
2. mobile_seduction_suite.yaml'ı HA'a yükle
3. scifi_soundspace_augmenter.py'yi Pi 4'te çalıştır (systemd service)
4. (Opsiyonel) Araç içi WLED şerit (ayak/kapı) → ESP32 + ESPHome
5. (Opsiyonel) Araç içi USB difüzör → imza koku
6. Test: "Jarvis, Blackout" → ekran %0, konsol off, HUD aktif
7. Test: "Date Mode" → WLED kırmızı, difüzör imza koku, Spotify R&B %12
8. Test: Gece sürüşü → OBD2 RPM → Sci-Fi motor sesi (hoparlörden)
```

---

## 🚀 Modül 24: car_edge_ai_vision — Kurulum

### 24.1 Jetson Nano + JetPack

```
1. JetPack SDK imajını 64GB MicroSD'ye yaz (BalenaEtcher)
2. Jetson Nano'yu başlat → Ubuntu kurulum (kullanıcı: jarvis)
3. nvcc --version → CUDA doğrula
4. sudo nvpmodel -m 0 → MAXN performans modu
5. sudo jetson_clocks → saat hızları sabit
6. Tailscale kur → VPS'e bağlan
```

### 24.2 IMX219 Kamera + OpenADAS

```
1. IMX219 kamera → CSI-2 port → dikiz aynası arkasına monte
2. nvgstcapture-1.0 → kamera görüntüsü test
3. Kamera kalibrasyonu (OpenCV distortion düzeltme)
4. open_adas_installation_script.sh'ı çalıştır:
   - OpenADAS klonla + bağımlılıklar + YOLO ağırlıkları + TensorRT FP16
5. cd ~/open-adas/build && ./open-adas --camera 0 --model yolov4-tiny
6. Test: Şerit takibi → neon mavi/yeşil çizgiler ekranda (30 FPS)
7. Test: Ön araç → Bounding Box + FCW uyarısı
```

### 24.3 ADAS HMI + HA Bridge

```
1. adas_hmi_display_config.py'yi çalıştır (Qt HMI, 30 FPS)
2. adas_home_assistant_bridge.py'yi çalıştır (MQTT köprüsü)
3. HA'a ADAS otomasyon YAML'ini yükle (MQTT → WLED + TTS)
4. systemd service oluştur (otomatik başlatma)
5. Test: FCW tehlikesi → MQTT → WLED kırmızı strobe + Jarvis sesli uyarı
6. Test: Şeritten çıkma → "Şeritten çıkma tespit edildi!" + WLED uyarı
```

---

## 🛡️ Modül 25: car_sentry_mode_security — Kurulum

### 25.1 Donanım (PIR + Röle + Jetson Deep Sleep)

```
1. PIR sensör (HC-SR501) → Jetson Nano GPIO 7'ye bağla:
   VCC → 3.3V, GND → GND, OUT → GPIO 7
2. MPU6050 şok sensör → I2C + INT → GPIO 8 (Modül 12 ile paylaşımlı)
3. Akıllı röle (12V→5V + voltaj sensör) → akü koruma:
   Akü <11.5V → röle açar → Jetson tamamen kapanır
4. Jetson Nano Deep Sleep yapılandırması:
   sudo systemctl edit suspend.service
   # GPIO interrupt → PIR tetiklediğinde uyan
5. (Opsiyonel) Arka kamera (USB webcam) → Jetson USB'ye bağla
```

### 25.2 Sentry Daemon + Telegram Bot

```
1. sentry_motion_trigger_daemon.py'yi Jetson'a kopyala:
   scp car_sentry_mode_security/sentry_motion_trigger_daemon.py jarvis@JETSON_IP:~/
2. Telegram Bot oluştur:
   - Telegram → @BotFather → /newbot → token al
   - Chat ID al: @userinfobot → kendi chat ID'ni öğren
   - Config'e token + chat_id gir
3. telegram_whatsapp_alert_bridge.py'yi Jetson'a kopyala
4. systemd service oluştur (otomatik başlatma):
   sudo nano /etc/systemd/system/sentry-daemon.service
   [Service]
   ExecStart=/usr/bin/python3 /home/jarvis/sentry_motion_trigger_daemon.py
   Restart=always
5. sudo systemctl enable sentry-daemon && sudo systemctl start sentry-daemon
6. Test: PIR tetikle → kamera aç → snapshot → Telegram'a fotoğraf gönder
```

### 25.3 HA Sentry Mode Panel

```
1. car_security_home_assistant_integration.yaml'ı HA'a yükle
2. input_boolean.car_sentry_mode → SuperApp'te Sentry anahtarı
3. counter.car_intrusions → ihlal sayacı
4. input_datetime.car_last_intrusion → son ihlal zamanı
5. SuperApp Lovelace'e Sentry panel ekle (Mushroom + picture-entity)
6. Test: SuperApp → Sentry ON → MQTT → Jetson ARM → Deep Sleep
7. Test: PIR tetikle → MQTT → HA → mobil critical bildirim + fotoğraf
8. Test: SuperApp → Sentry OFF → MQTT → Jetson DISARM → normal mod
```

---

## ✅ Genel Test ve Doğrulama

### Tüm Sistem Test Sırası

```
1. VPS + Tailscale + HA çalışıyor mu? → http://VPS_IP:8123
2. GL-MT3000 + MQTT broker çalışıyor mu? → MQTT Explorer ile test
3. Zigbee2MQTT + dongle çalışıyor mu? → Zigbee cihaz keşfi
4. Jarvis sesli komut: "Jarvis" → "Anlaşıldı efendim" (ElevenLabs sesi)
5. Gizli buton tek tık → Lounge modu (WLED + Spotify + difüzör)
6. Ahşap dokunma 2sn → Intimacy modu (WLED kırmızı + klima + koku)
7. NFC kahve → Barista modu (priz + ışıklar + müzik)
8. Gece yataktan kalk → Yatak altı LED %15
9. Sabah uyanış → WLED gündoğumu + perde + kahve
10. Mutfak: "Bunlardan ne çıkar?" → GPT-4o Vision tarif önerisi
11. Misafir geldi → Yüz tanıma → "Tekrar hoş geldiniz, Ayşe"
12. 15dk sessizlik → Jarvis proaktif sohbet başlat
```

---

## 🔄 Güncellemeler ve Bakım

| Görev | Sıklık | Nasıl |
|---|---|---|
| HA güncelleme | Aylık | `docker pull homeassistant/home-assistant:latest && docker restart homeassistant` |
| ESPHome güncelleme | Aylık | ESPHome web arayüzünden |
| ChromaDB yedekleme | Haftalık | `cp -r ~/jarvis_memory/chromadb /backup/` |
| Esans yağı yenileme | 2-4 hafta | Difüzör su haznesini doldur |
| Zigbee buton pil | 1-2 yıl | CR2032 değiştir |
| Kamera lens temizliği | Aylık | Mikro fiber bez ile |
| Kablo gizleme kontrolü | 3 ay | Kablolar görünür hale gelmiş mi kontrol et, yeniden bantla |
| Akım korumalı priz kontrolü | 6 ay | Surge protector LED'i yanıyor mu? Hasar var mı kontrol et |
| UPS batarya testi | 6 ay | UPS test butonu ile batarya sağlığını kontrol et |

---

## 🎨 Kablo Gizleme ve Estetik Montaj (Tüm Modüller)

> **"Tony Stark / Premium Lounge" teması için KRİTİK adım.**
> Tüm modüllerin donanımı kurulduktan sonra, kabloların gizlenmesi ŞARTTIR.
> WLED şeridinin, kameranın veya radarın kablosu duvardan sarkarsa, misafirin
> gözünde lüks algısı anında "öğrenci işi kablo karmaşasına" döner.
> Tüm ESP32'leri ve kabloları yatağın, masanın altına sıfır görünecek şekilde
> bantlamalısın. Sensörlerin sadece uçları görünmeli.

### Adım 1: Kablo Sleeve (Cırtlı Kılıf) ile Kablo Toplama

```
1. Birden fazla kabloyu (ESP32 güç + sensör kabloları) tek sleeve içinde topla
2. Sleeve'i cırtlı yapıştırarak kabloları içine yerleştir
3. Sleeve'i duvar rengine boyayabilirsin (tam gizleme için)
4. Sleeve'i mobilya arkasına/baseboard boyunca geçir
```

### Adım 2: İnce Kablo Kanalı (Duvar Kenarı)

```
1. PVC kablo kanalını (beyaz/duvar rengi, 15×10mm) duvar kenarına yapıştır
2. Kanalı duvar rengine boya (tam gizleme)
3. Kabloları kanal içine yerleştir, kapağı kapat
4. Kanalı baseboard (zemin süpürgeliği) boyunca gizle
```

### Adım 3: Mobilya Altı Bantlama (ESP32 + Sensörler)

```
1. Tüm ESP32'leri yatak/masa/komodin altına 3M VHB bant ile yapıştır
2. Sensör kablolarını mobilya altında kablo bağı ile topla
3. Kabloları mobilya alt yüzeyine bantla (sarkma yok)
4. Sadece sensör uçları (TTP223 pad, LD2410 anten, INMP441) dışarı baksın
5. Keçe kılıf (felt sleeve) ile mobilya altı kabloları gizle
```

### Adım 4: Kısa Kablo Prensibi

```
1. Mümkün olan en kısa kablo kullan (30-50cm düz başlı USB)
2. Sarkma olmasın — fazla kablo mobilya altında toplansın
3. Güç kabloları (220V) veri kablolarından ayrı kanalda (EMI önleme)
4. USB-C/Micro-USB kabloları düz başlı seç (mobilya altında az yer kaplar)
```

### Adım 5: Modül Bazlı Kablo Gizleme Kontrol Listesi

| Modül | Kablo Gizleme Yöntemi |
|---|---|
| **Modül 1 (jarvis_core)** | ESP32-S3 + INMP441 komodin içinde, kablolar komodin arkasında sleeve |
| **Modül 2 (hidden_triggers)** | TTP223 + ESP32 masa altında bantlı, kablo masa altında keçe kılıf |
| **Modül 3 (space_projection)** | Projeksiyon güç kablosu kitaplık arkasında, sleeve ile gizli |
| **Modül 4 (magic_mirror)** | Pi Zero + LCD kabloları ayna arkasında, hiçbiri görünmez |
| **Modül 5 (spatial_audio)** | Echo Dot güç kabloları kitaplık/bitki arkasında, kısa kablo |
| **Modül 6 (underbed_lighting)** | LD2410 + ESP32 + COB LED kabloları yatak kirişi boyunca bantlı |
| **Modül 7 (morning_after)** | SwitchBot Curtain güç kablosu perde rayı arkasında gizli |
| **Modül 8 (invisible_remote)** | Broadlink güç kablosu kitaplık arkasında, kısa USB |
| **Modül 9 (smart_diffuser)** | Difüzör güç kablosu mobilya arkasında, sleeve |
| **Modül 10 (audio_reactive_wled)** | ESP32 + INMP441 + LED güç kabloları tavan pervazı arkasında, kanal |
| **Modül 11 (barista_mode)** | Shelly priz kablo gerektirmez (duvar prizi) |
| **Modül 12 (intimacy_sync_mode)** | MPU6050 + ESP32 kabloları yatak kirişi boyunca bantlı, köpük altında |
| **Modül 13 (vision_chef_assistant)** | Tapo C200 güç kablosu dolap arkasında, USB kısa kablo |

### Altın Kural

> **"Sensörlerin sadece uçları görünmeli. Kablolar asla."**
> Misafir odaya girdiğinde, teknolojiyi "fark etmemeli" — sadece "çalıştığını"
> deneyimlemeli. Sarkık bir kablo, tüm illüzyonu bozar. Kablo gizleme,
> "premium lounge" hissinin görünmez ama en kritik parçasıdır.

---

*Bu dosya, tüm parçalar alındıktan sonra eksiksiz kurulum için rehberdir. Her modülün kendi `hardware_and_*.md` dosyasında daha detaylı bilgi bulunur.*