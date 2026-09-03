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
   - MiniMax Voice Cloning (Modül 1)
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

### 1.2 jarvis_core Python (VPS Docker — Raspberry Pi YOK)

> **Mimari değişiklik:** Raspberry Pi 4 ÇÖP. jarvis_core Python + ChromaDB + Mealie + OpenClaw
> hepsi VPS üzerinde Docker konteynerlerinde çalışır. Yurt odasında sıfır sunucu donanımı.

```
1. VPS'e SSH ile bağlan (DigitalOcean / Hetzner — 2 vCPU, 4GB RAM)
2. Docker + Docker Compose kur:
   curl -fsSL https://get.docker.com | sh
3. docker-compose.yml oluştur (HA + jarvis_core + ChromaDB + Mealie):
   services:
     home-assistant:
       image: ghcr.io/home-assistant/home-assistant:stable
       volumes: [./ha:/config]
       network_mode: host
     jarvis-core:
       build: ./jarvis_core
       volumes: [./jarvis_core:/app]
       restart: always
     chromadb:
       image: chromadb/chroma
       volumes: [./chroma:/chroma]
     mealie:
       image: hkex03/mealie:latest
       volumes: [./mealie:/app/data]
4. Gerekli Python kütüphaneleri (jarvis_core Dockerfile):
   pip install websockets asyncio httpx
   pip install opencv-python-headless face-recognition chromadb numpy pillow pypdf2 mediapipe
5. API anahtarlarını config'e gir:
   - MiniMax (Speech 2.8 Turbo — sesten-sese, voice cloning)
   - DeepSeek (V4-Pro — ağır zeka, özet)
   - Qwen-VL (Max — görüntü analizi)
6. Voice Cloning referans ses dosyası hazırla:
   - 10 sn WAV/MP3 (Jarvis tonu — Paul Bettany veya Türkçe dublaj)
   - assets/jarvis_voice_reference.wav olarak kaydet
7. System prompt'u yükle (advanced_system_prompt_v2.md — karakter anayasası)
8. Konteynerleri başlat:
   docker compose up -d
9. Tüm servisler otomatik başlar (restart: always — VPS reboot'ta bile)
10. Test: docker compose logs jarvis-core — MQTT bağlantısı kurulmuş olmalı
```

### 1.3 HA Entegrasyonu

```
1. HA → Settings → Devices → Add → Extended OpenAI Conversation
2. MiniMax API key gir
3. openai_conversation_agent.yaml'ı configuration.yaml'a import et:
   openai_conversation: !include jarvis_core/openai_conversation_agent.yaml
4. MiniMax Voice Cloning yapılandır:
   tts:
     - platform: MiniMax Voice Cloning
       api_key: "YOUR_KEY"
       voice: "Adam"
5. master_orchestration_intents.yaml'ı HA'a yükle
6. autonomous_conversation_trigger.yaml'ı HA'a yükle
7. Test: "Jarvis" de → "Anlaşıldı efendim" cevabı gelmeli
```

---

## 🔘 Modül 2: hidden_triggers — Kurulum

> **Mimari değişiklik:** Sonoff ZBMINI ÇÖP — yurt priz/anahtar tesisatı sökülmüyor.
> Gizli tetikleyiciler TTP223B dokunmatik sensörlerle (×5, ELDE) masa altına.

### 2.1 TTP223B Dokunmatik Sensörler (×5 — ELDE)

```
1. 5× TTP223B'yi ESP32 Sensör Hub'a bağla:
   TTP223 #1 (masa sol)  → GPIO 4
   TTP223 #2 (masa sağ)  → GPIO 5
   TTP223 #3 (komodin)   → GPIO 6
   TTP223 #4 (yatak başı) → GPIO 7
   TTP223 #5 (mutfak tezgah altı) → GPIO 15
   (Hepsi: VCC → 3.3V, GND → GND)
2. Her TTP223'ü ahşap yüzey altına yapıştır (sensör pad'i ahşaba bakar)
3. (Kalın ahşap >10mm) Bakır folyo şerit lehimle → alan genişlet
4. ESP32'ye stealth_button_esphome.yaml'i yükle (ESPHome web — 5 sensör birden)
5. WiFi + MQTT yapılandır
6. Kalibrasyon (her sensör için):
   - ESPHome log'larını izle (USB)
   - Ahşaba dokun → "Desk Hidden Touch: ON" gelmeli
   - Gelmiyorsa → ahşap çok kalın, bakır folyo ekle
   - Titreşimli → debounce artır (100ms → 200ms)
7. HA'da 5× binary_sensor görünüyor mu kontrol et:
   - binary_sensor.desk_touch_left
   - binary_sensor.desk_touch_right
   - binary_sensor.bedside_touch
   - binary_sensor.bedframe_touch
   - binary_sensor.kitchen_counter_touch
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

## 🪞 Modül 4: magic_mirror — Kurulum (Pi'siz — VPS + Mi Box)

> **Mimari değişiklik:** Raspberry Pi Zero ÇÖP. MagicMirror² VPS Docker'da web
> servisi olarak çalışır → TV'de Mi Box S 4K tarayıcısında tam ekran (Kiosk) gösterilir.

### 4.1 MagicMirror² Web Sunucusu (VPS Docker)

```
1. VPS'te MagicMirror² Docker konteyneri oluştur (server-only mod):
   docker run -d --name magicmirror \
     -p 8080:8080 \
     -v ./magicmirror/config:/opt/magic_mirror/config \
     -v ./magicmirror/modules:/opt/magic_mirror/modules \
     bastilimbach/magicmirror
2. MMM-Spotify modülünü kur:
   cd ./magicmirror/modules
   git clone https://github.com/skuethe/MMM-Spotify.git
3. MMM-MQTT modülünü kur:
   git clone https://github.com/shbatm/MMM-MQTT.git
4. magicmirror_config.js'yi config/config.js olarak kopyala
5. Spotify API bilgilerini ve MQTT broker adresini (GL-MT3000) gir
6. custom.css'e "Calm Technology" stillerini ekle (beyaz yazı, siyah arka plan)
7. Test: http://VPS_IP:8080 → MagicMirror² web sayfası görünmeli
```

### 4.2 TV'de Gösterim (Mi Box S 4K — Planlanan)

```
1. Mi Box S 4K'yi TV'nin HDMI girişine tak
2. Mi Box kurulum: Google hesabı → Google TV 14
3. Tarayıcı aç (veya "Fullscreen Browser" app kur)
4. http://VPS_IP:8080 adresine git → MagicMirror² görünür
5. Kiosk mod: Tarayıcıyı tam ekran yap + otomatik açılış ayarla
6. (Opsiyonel) Two-way mirror akriliği TV ekranının önüne yerleştir
   → TV kapalıyken ayna, açıkken MagicMirror² ("TV Ayna" hibrit)
7. TV'yi Tuya akıllı prize tak → varlık algılayınca TV açılır
   → MagicMirror² otomatik görünür
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

## 🌅 Modül 7: morning_after — Kurulum (DIY Perde Motoru)

> **Mimari değişiklik:** SwitchBot Curtain (3000₺) ÇÖP → 28BYJ-48 Step Motor +
> ULN2003 Sürücü (ELDE, ~150₺) + ESP32 + ESPHome stepper.

### 7.1 Donanım Montajı (28BYJ-48 + ULN2003)

```
1. 28BYJ-48 step motoru ULN2003 sürücü kartına tak (5-pin konnektör)
2. ULN2003'ü ESP32'ye bağla:
   IN1 → GPIO 16
   IN2 → GPIO 17
   IN3 → GPIO 5
   IN4 → GPIO 18
   VCC → 5V (harici güç önerilir — motor akımı çeker)
   GND → GND (ESP32 GND ile ortak)
3. Mekanik bağlantı:
   - Motor miline dişli tak (3D baskı veya hazır dişli)
   - Perde rayına halat + kasnak sistemi kur
   - Motor → dişli → halat → perde mekanizması
   - (Alternatif) Motor miline bobin (spool) tak → perde ipini sar
4. Motoru perde rayının ucuna monte (braket + 3M VHB)
5. (Opsiyonel) Limit switch × 2 → açık/kapalı uç pozisyonları
   → GPIO 19 (açık) + GPIO 21 (kapalı)
```

### 7.2 ESPHome Stepper Konfigürasyonu

```yaml
# ESPHome stepper bileşeni (Sensör Hub config'ine ekle)
stepper:
  - platform: uln2003
    id: curtain_stepper
    pin_a: GPIO16
    pin_b: GPIO17
    pin_c: GPIO5
    pin_d: GPIO18
    max_speed: 250 steps/s  # Yavaş — sinematik açılım

cover:
  - platform: template
    id: smart_curtain
    name: "Perde"
    open_action:
      - stepper.set_target:
          id: curtain_stepper
          target: 2048  # Tam açık (kalibre et)
    close_action:
      - stepper.set_target:
          id: curtain_stepper
          target: 0      # Tam kapalı
    position_template: >-
      {{ (states('sensor.curtain_position') | float(0)) }}
```

### 7.3 Kalibrasyon + Otomasyon

```
1. ESPHome firmware yükle → WiFi + MQTT yapılandır
2. Kalibrasyon:
   - Perdeyi manuel tam kapat → stepper.set_target: 0
   - Perdeyi manuel tam aç → adım sayısını oku (örn. 2048)
   - Bu değeri config'e yaz
3. sunrise_simulation.yaml'ı HA'a yükle (script.sunrise_simulation)
4. morning_orchestration_automation.yaml'ı HA'a yükle
5. input_datetime.morning_wake_time'ı HA'ta tanımla
6. Hava durumu sensörü ekle (weather.home)
7. Test: "Jarvis, sabah 9'da uyandır" → input_datetime ayarlanır
8. Test: 9:00'dan 10 dk önce WLED gündoğumu + perde %20 başlamalı
9. Test: 9:00'da perde %100 (yavaş sinematik açılım ~30-60 sn) + barista tetiklenmeli
```

---

## 📡 Modül 8: invisible_remote — Kurulum (Tuya IR+RF)

> **Mimari değişiklik:** Broadlink RM4 Mini ÇÖP → Tuya WiFi Smart IR+RF (ELDE).
> Klima + vantilatör Tuya Smart app'te zaten bağlı. HA'da `tuya-local` ile tam yerel kontrol.

### 8.1 Tuya IR+RF Kumanda (ELDE — Klima + Vantilatör Bağlı)

```
1. Tuya Smart app'te klima + vantilatör zaten eşleşmiş ✅
2. HA'a tuya-local entegrasyonu kur (HACS):
   HACS → Integrations → "Tuya Local" → Install
3. HA → Settings → Devices → Add → Tuya Local
4. Tuya IR+RF cihazının IP'sini bul (GL-MT3000 admin panelinden)
5. Cihazı ekle → remote.tuya_ir_rf entity'si oluşur
6. IR kod öğrenme (tuya-local remote.learn_command):
   - HA → Developer Tools → Services → remote.learn_command
   - entity_id: remote.tuya_ir_rf
   - command: "klima_power_off"
   - Orijinal klima kumandasından Power Off tuşuna bas (30 sn içinde)
   - Kod kaydedilir (restart'ta kalıcı)
7. Klimanın tüm tuşlarını öğren:
   - power_on, power_off, temp_up, temp_down, mode_cool, mode_dry,
     fan_speed, swing_on, swing_off
8. Vantilatörün tüm tuşlarını öğren:
   - fan_power, fan_speed_1, fan_speed_2, fan_speed_3, fan_oscillate
9. Öğrenilen kodları smartir_climate_media.yaml'daki script'lere bağla
10. Test: HA'dan klimayı aç/kapa → klima tepki vermeli
```

> **Not (TV):** TV'nin IR alıcısı arızalı — Tuya kumanda TV'ye komut gönderse de
> TV almıyor. TV değişince + Mi Box S 4K takılınca TV kontrolü IR yerine
> Android TV entegrasyonu (ADB) + Chromecast ile yapılır (Modül 34).

### 8.2 ESP32 IR Blaster (Yedek — Parçalar ELDE)

```
1. TSOP1838 IR alıcıyı ESP32'ye bağla (kod öğrenme):
   OUT → GPIO 14 (ESPHome remote_receiver)
   VCC → 3.3V, GND → GND
2. LTE-4206 IR LED'leri 2N2222 transistörle sür (blaster):
   ESP32 GPIO 13 → 220Ω → 2N2222 Base
   2N2222 Collector → IR LED (-)
   IR LED (+) → 3.3V (2 LED seri)
   2N2222 Emitter → GND
3. ESPHome remote_transmitter + remote_receiver bileşenlerini yükle
4. Orijinal kumandaların kodlarını öğren (TSOP1838 üzerinden)
5. Tuya kumandanın görmediği köşelerde blaster olarak kullan
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

## ☕ Modül 11: barista_mode — Kurulum (HAUSBERG HB3723)

> **Mimari değişiklik:** HAUSBERG HB3723 Espresso (ELDE) + Tuya akıllı priz (planlanan).
> WiFi'siz makine → güç izleme ile "kahve hazır" tespiti.

```
1. HAUSBERG HB3723'ü Tuya UK akıllı prize tak
2. Tuya prizi Tuya Smart app ile WiFi'a bağla
3. HA'a LocalTuya entegrasyonu ile ekle (switch.coffee_machine_plug)
   → sensor.coffee_machine_power entity'si oluşur (güç izleme)
4. HAUSBERG'in güç anahtarını ON konumunda bırak
   (Priz açılınca makine ısınmaya başlar)
5. NTAG213 NFC etiketi (ELDE) masanın altına yapıştır
6. HA Companion App → NFC Tags → Write → "nfc_coffee_table"
7. Spotify'da "Lo-Fi Coffee Shop" çalma listesi oluştur → URI'yi al
8. barista_automation.yaml'daki playlist URI'sini güncelle
9. barista_automation.yaml'ı HA'a yükle
10. smart_readiness_sensor.yaml'ı HA'a yükle — HAUSBERG güç profili:
    - Isınma: ~900W (thermoblock ısıtıcı)
    - Hazır bekleme: ~50W
    - Geçiş tespiti: 900W → 50W = "Espresso ready"
11. Çift cidarlı fincanları, şurupları ve kahveyi hazırla
12. Test: NFC'ye telefon dokundur → priz aç + ışıklar %30 amber + müzik %15
13. Test: Güç 900W'a çıkıp 50W'a düşerse → "Espresso ready" anonsu
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
   # Qwen-VL Max, OpenAI-uyumlu API kullanır (DashScope endpoint)
2. vision_frame_analyzer.py'yi Pi'ye kopyala:
   scp vision_chef_assistant/vision_frame_analyzer.py pi@PI_IP:~/
3. RTSP URL ve Qwen-VL Max API key'i config'e gir
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
4. Test: "Jarvis, bunlardan ne çıkar?" → kamera kare al → Qwen-VL Max → tarif
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
3. minimax_realtime_orchestrator.py'de persona switching desteği ekle
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
3. Python script: PDF → metin çıkar → DeepSeek V4-Pro'e gönder
4. DeepSeek V4-Pro: değerleri referanslarla karşılaştır → öneriler
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
2. DeepSeek V4-Pro modeline bu prompt gönderilir (sağlık verisi analizi)
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
4. hybrid_brain_and_memory_manager.py chat_input'u dinlemeli
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

### 20.3 Stil Koçu (Qwen-VL Max)

```
1. digital_grooming_coach_vision.yaml'ı HA'a yükle
2. digital_grooming_coach_module.yaml'ı HA'a yükle
3. input_boolean.grooming_coach_active → ON
4. input_boolean.grooming_protocol_active → ON
5. input_select.today_event_type tanımlı mı kontrol et
6. Takvim (calendar.personal) + hava durumu (weather.home) HA'ta aktif
7. Test: "Jarvis, kombin nasıl?" → snapshot → Qwen-VL Max → TTS
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
4. Jarvis sesli komut: "Jarvis" → "Anlaşıldı efendim" (MiniMax Voice Cloning sesi)
5. Gizli buton tek tık → Lounge modu (WLED + Spotify + difüzör)
6. Ahşap dokunma 2sn → Intimacy modu (WLED kırmızı + klima + koku)
7. NFC kahve → Barista modu (priz + ışıklar + müzik)
8. Gece yataktan kalk → Yatak altı LED %15
9. Sabah uyanış → WLED gündoğumu + perde + kahve
10. Mutfak: "Bunlardan ne çıkar?" → Qwen-VL Max tarif önerisi
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

> **"Premium Lounge" teması için KRİTİK adım.**
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

---

## Faz 12: Modül 27 — OpenClaw Digital Sandbox (Dijital Ajan)

> Tamamen VPS üzerinde, donanım gerektirmez. Sadece Docker ve yazılım.

### Adım 1: Docker Kurulumu (VPS)
```bash
# VPS'e SSH ile bağlan
ssh root@vps-ip

# Docker zaten kurulu (HA için), OpenClaw için yeni konteyner
docker pull ghcr.io/openclaw/openclaw:latest

# Mealie (tarif veritabanı) — aynı Docker network
docker compose up -d  # docker-compose.yaml içinde mealie servisi
# Mealie: http://localhost:9925
# API docs: http://localhost:9925/docs
```

### Adım 2: OpenClaw Konfigürasyonu
```bash
# OpenClaw sandbox konteyner başlat
docker run -d --name openclaw \
  --network=homeassistant_default \
  -e MEALIE_URL=http://mealie:9925 \
  -e DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY \
  -e MQTT_BROKER=gl-mt3000.local \
  openclaw:latest

# Zero Trust sandbox ayarları (7 katman)
# → sandbox_and_security.md dosyasına bakın
```

### Adım 3: Mealie İlk Kurulum
```
1. Tarayıcıda http://localhost:9925 aç
2. İlk kullanıcı oluştur (jarvis@local)
3. API token al → .env dosyasına kaydet
4. Test: bir tarif URL'i yapıştır → scrape test
```

---

## Faz 13: Modül 28 — Multicooker Chef Automation (Hisense HMC6SBK)

> **Mimari değişiklik:** Xiaomi Mi Smart Multi Cooker → **Hisense HMC6SBK 6L** (ELDE).
> WiFi YOK → Çin bulutu izolasyonu GEREKMEZ (sıfır bulut riski).
> Zeka: Tuya akıllı priz güç izleme + Tapo C200 vision + Mealie orkestrasyonu.

### Adım 1: Hisense HMC6SBK'yi Akıllı Prize Bağla
```
1. Hisense HMC6SBK'yi (ELDE) Tuya UK akıllı prize tak
2. Tuya prizi Tuya Smart app ile WiFi'a bağla (GL-MT3000 ağı)
3. HA'a LocalTuya ile ekle:
   → switch.hisense_multicooker
   → sensor.hisense_multicooker_power (güç izleme)
4. Hisense'in güç tuşunu ON bırak — priz açılınca hazır olur
```

### Adım 2: Güç İzleme ile Pişirme Durumu Tespiti
```yaml
# Hisense HMC6SBK güç profili (1500W cihaz):
# - Isınma/pişirme: ~1200-1500W
# - Keep-warm (sıcak bekleme): ~30-50W
# - Bekleme (kapalı): ~0-2W
#
# HA template sensor (configuration.yaml):
template:
  - binary_sensor:
      - name: "Multicooker Cooking"
        state: >
          {{ states('sensor.hisense_multicooker_power') | float(0) > 500 }}
        delay_on: "00:02:00"   # 2 dk üstünde kalırsa pişirme başladı
      - name: "Multicooker Done"
        state: >
          {{ states('sensor.hisense_multicooker_power') | float(0) < 60
             and states('sensor.hisense_multicooker_power') | float(0) > 5 }}
        delay_on: "00:03:00"   # 3 dk keep-warm'da kaldıysa pişirme bitti
```

### Adım 3: Mealie + Vision-Cooker Otomasyonlarını Yükle
```bash
# HA'ya YAML dosyalarını kopyala
cp vision_cooker_orchestration.yaml /config/packages/
cp cooking_notification_automation.yaml /config/packages/
cp mealie_macro_orchestrator.py /config/python_scripts/

# HA yeniden başlat
ha core restart
```

### Adım 4: Vision-Cooker Kapalı Döngü Testi
```
1. Tapo C200 (Modül 13) mutfak tezgahına bakar
2. Malzemeleri tezgaha koy → Qwen-VL malzemeleri tanır
3. Mealie'de tarif eşleştirir → Jarvis önerir
4. Kullanıcı onaylar → malzemeleri Hisense'e koy → programı seç
5. Prizden güç izleme: 1500W (pişirme) → 40W (keep-warm)
6. "Multicooker Done" tetiklenir → Jarvis "Yemeğiniz hazır" der
   → WLED turuncu yanar → Lamba (beklemede) yerine Yeelight flash
```

---

## ⏸️ Faz 14: Modül 29 — Embodied Jarvis Avatar (5-DOF Lamba) — BEKLEMEDE

> **⚠️ BU FAZ BEKLEMEYE ALINDI:** "Önce odanın temeli (ses, ışık, otomasyon).
> Robotiğe 1 kuruş harcamıyoruz." Aşağıdaki adımlar oda temeli bitince
> aynen uygulanacaktır. Dokümantasyon korunmuştur.

### Adım 1: 3D Baskı
```
1. BCN3D Moveo STL dosyalarını indir
2. PLA filament ile 3D yazıcıda bas (~6 saat)
3. Parçaları zımparala (pürüzsüz yüzey)
4. F693ZZ rulmanları yerleştir (eklemlerde)
```

### Adım 2: Donanım Montajı
```
1. PCA9685'i Raspberry Pi 4'e I2C ile bağla:
   Pi SDA (GPIO2) → PCA9685 SDA
   Pi SCL (GPIO3) → PCA9685 SCL
   Pi 3.3V → PCA9685 VCC (lojik)
   5V 4A Adaptör → PCA9685 V+ (servo güç)

2. 5 servo'yu PCA9685'e bağla:
   Kanal 0: MG996R (omuz) — turuncu/kahve
   Kanal 1: MG996R (dirsek) — sarı
   Kanal 2: MG996R (bas dönüş) — yeşil
   Kanal 3: SG90 (bilek) — mavi
   Kanal 4: SG90 (kafa) — mor

3. WS2812 NeoPixel Ring'i Pi GPIO18'e bağla (SPI)

4. INMP441 mikrofonu I2S'e bağla (Modül 1 ile paylaşımlı)
```

### Adım 3: Autonomous OS Kurulumu
```bash
# Pi 4'te
git clone https://github.com/autonomous-ai/autonomous-os.git
cd autonomous-os

# Edge body mode (beyin bulut, gövde yerel)
export AUTONOMOUS_MODE=edge_body_only
export MQTT_BROKER=gl-mt3000.local

# DEVICE.md, SOUL.md, SAFETY.md dosyalarını kopyala
cp /config/embodied_jarvis_avatar/DEVICE.md ./config/
cp /config/embodied_jarvis_avatar/SOUL.md ./config/
cp /config/embodied_jarvis_avatar/SAFETY.md ./config/

# PCA9685 driver'ı kaydet
python3 embodied_lamp_driver.py

# systemd servis olarak kaydet
sudo systemctl enable embodied-lamp
sudo systemctl start embodied-lamp
```

### Adım 4: Postür Kalkanı
```bash
# Posture shield daemon
python3 posture_shield_daemon.py &

# Test: öne eğil → lamba size dönmeli + kehribar pulse
```

---

## ⏸️ Faz 15: Modül 30 — Desktop Pet Kame32 (Robot Evcil Hayvan) — BEKLEMEDE

> **⚠️ BU FAZ BEKLEMEYE ALINDI:** Oda temeli (ses, ışık, otomasyon) bitince
> uygulanacaktır. Dokümantasyon korunmuştur.

### Adım 1: 3D Baskı ve Montaj
```
1. Kame32 STL dosyalarını indir (Thingiverse #1265766)
2. PLA filament ile 3D yazıcıda bas (~4 saat)
3. F693ZZ rulmanları yerleştir (8 adet, eklemlerde)
4. 8 SG90 servo'ları monte et (4 bacak × 2 servo)
5. Paralelgram mekanizmasını kontrol et (ayak zemine dik)
```

### Adım 2: ESP32 Firmware Yükle
```bash
# Arduino IDE
# Board: ESP32 DevKit V1
# Library: ESP32Servo, PubSubClient, ArduinoJson

# kame_esp32_firmware.ino dosyasını aç
# WiFi SSID ve şifreyi gir (GL-MT3000)
# MQTT broker adresini gir (gl-mt3000.local)
# Upload → ESP32'ye yükle

# Test: MQTT'ten "kame/command/stand" gönder → Kame dik durmalı
```

### Adım 3: Qi Şarj Pedi Kurulumu
```
1. Qi verici pad'i masa üstüne sabitle (çift taraflı bant)
2. 5V/2A USB adaptörü Qi pad'e bağla
3. Qi alıcı coil'i Kame'nin altına yapıştır
4. TP4056 + 2S LiPo'yu Kame'nin gövdesine yerleştir
5. Voltage divider (10kΩ + 4.7kΩ) → GPIO34 (batarya ölçüm)
```

### Adım 4: Eye of Sauron Kalibrasyonu (Otonom Park)

> **Kritik adım:** Kame'nin Qi şarj pedine Tapo C200 kamerası ile
> nasıl hizalanacağının kalibrasyonu.

```bash
# 1. Tapo C200'ü masa üstüne monte et (Kame'yi yukarıdan görecek)
#    Kamera → GL-MT3000 → RTSP stream

# 2. Kame'nin üstüne parlak renkli bir çıkartma yapıştır (HSV filtre için)
#    Önerilen: neon yeşil veya neon pembe (OpenCV HSV'de kolay algılanır)

# 3. Kalibrasyon script'ini çalıştır
python3 eye_of_sauron_parking.py --calibrate

# 4. Kame'yi Qi pad'in yanına koy (manuel)
#    Script Kame'nin HSV renk aralığını otomatik tespit eder
#    → "HSV range: H[35-85], S[100-255], V[100-255]" gibi çıktı verir

# 5. Kame'yi Qi pad'den ~30cm uzağa koy
#    Script otonom park testini başlatır:
#    → Kamera görüntüsü → OpenCV Kame konumu → hata vektörü
#    → MQTT "kame/command/move" → Kame yürür
#    → Kamera tekrar görüntü → konum kontrolü
#    → Max 20 adımda Qi pad'e park

# 6. Başarı kriteri:
#    → Kame Qi pad üzerinde duruyor mu? (kamera ile doğrula)
#    → Batarya şarj oluyor mu? (GPIO34 ADC değer artıyor mu?)
#    → 10 denemenin kaçı başarılı? (>=8/10 olmalı)

# 7. Başarısızsa:
#    → Yürüme adım sayısını artır (max 30)
#    → HSV renk aralığını daralt
#    → Qi pad çevresine görsel işaret koy (OpenCV referans noktası)
```

### Adım 5: Audio-Reactive Dans Testi
```
1. Müzik çal (Spotify)
2. Modül 10 (WLED) BPM tespiti → MQTT "kame/command/dance"
3. Kame beat'e göre çömel/kalk/ayak vur/spin
4. Müzik dur → Kame çömel (uyku modu)
```

### Adım 6: Wingman Karşılama Testi
```
1. Misafir kapıya yaklaştır (NFC tag veya yüz tanıma)
2. Otomasyon tetiklenir:
   → Kame ayağa kalkar
   → 3 adım yürür
   → Reverans yapar (bow)
   → Jarvis sesli karşılar
   → Kame geri döner
3. Gece 23:00 → Kame uyku moduna geçer
4. Sabah 08:00 → Kame uyanır
```

---

## ⏸️ Faz 16: Modül 31 — Siber Barmen (CocktailBerry) — BEKLEMEDE

> **⚠️ BU FAZ BEKLEMEYE ALINDI:** Oda temeli bitince uygulanacaktır.
> Ayrıca Raspberry Pi gerektirdiğinden, Pi'siz yeni mimaride tekrar
> değerlendirilecek (VPS + ESP32 röle alternatifi). Dokümantasyon korunmuştur.

> **Kokteyl miksoloji robotu — Raspberry Pi 4 + 7" Touch + 10 pompa + 16-CH röle + 1N4007 diyot**

### Adım 1: Elektronik Kablolama (Pompalar → Röle → 1N4007 Diyot)

```
1. 12V 10A SMPS'i duvara bağla (akım korumalı priz üzerinden)
2. LM2596 Buck Converter'ı 12V rail'e bağla
   → Trimpot ile çıkışı 5.0V'a ayarla (multimetre ile doğrula)
   → 5V çıkışı Pi 4 USB-C girişine bağla

3. 10 pompayı 12V rail'e paralel bağla:
   Pompa + (kırmızı) → 12V
   Pompa - (siyah)   → Röle COM terminali
   Röle NO terminali → GND (12V rail)

4. ⚠️ KRİTİK — 1N4007 DİYOT LEHİMLEME (Ters Akım Koruması):
   Her pompanın + ve - terminaline 1N4007 diyot PARALEL lehimle:
   
   1N4007 Katot (çizgili taraf) → Pompa + (12V tarafı)
   1N4007 Anot                → Pompa - (GND tarafı)
   
   → Diyot TERS bias'ta: normal çalışmada iletim yok
   → Röle açıldığında ters EMF spike'ı diyot üzerinden kısa devre olur
   → Röle kontakları ve Pi GPIO pin'leri korunur
   
   10 pompa için 10 diyot lehimle
   Isı büzük boru ile izole et
   Multimetre ile doğrula: ters yönde yüksek direnç

5. 16-CH Röle kartını Pi GPIO'ya bağla:
   VCC → Pi 5V (Pin 2/4)
   GND → Pi GND (Pin 6)
   IN1 → GPIO 17 (Pompa 1 - Vodka)
   IN2 → GPIO 27 (Pompa 2 - Gin)
   IN3 → GPIO 22 (Pompa 3 - Rom)
   IN4 → GPIO 23 (Pompa 4 - Tekila)
   IN5 → GPIO 24 (Pompa 5 - Viski)
   IN6 → GPIO 25 (Pompa 6 - Campari)
   IN7 → GPIO 5  (Pompa 7 - Lime Juice)
   IN8 → GPIO 6  (Pompa 8 - Cranberry)
   IN9 → GPIO 12 (Pompa 9 - Soda)
   IN10→ GPIO 16 (Pompa 10 - Tonic)

6. 7" Touch Display DSI ribbon → Pi 4 DSI port
7. Silikon hortumları pompalardan nozüle bağla (gıda uyumlu)
```

### Adım 2: CocktailBerry Kurulumu (Tek Satır)

```bash
# Raspberry Pi 4 terminalinde (Raspberry Pi OS Bookworm 64-bit)
bash <(curl -sL https://raw.githubusercontent.com/AndreWohnsland/CocktailBerry/master/install.sh)

# Script otomatik:
# → Python venv oluşturur
# → CocktailBerry klonlar
# → Gereksinimleri yükler
# → GPIO izinlerini ayarlar
# → systemd servis kaydeder
# → Web UI: http://raspberrypi.local:5000
```

### Adım 3: Pompa Kalibrasyonu

```bash
# Her pompanın akış hızını ölç:
python3 -m CocktailBerry --calibrate-pump 1
# → 10 sn çalıştır → çıkan sıvıyı ml olarak ölç
# → Akış hızı = ml / 10 sn
# → config/ingredients.yaml'a kaydet
# 10 pompa için tekrarla

# Hortum doluluk (priming):
python3 -m CocktailBerry --prime-all
# → Hortumlar dolana kadar pompaları çalıştır
```

### Adım 4: Kiosk Modu (Tam Ekran UI)

```bash
# Chromium Kiosk servis oluştur
sudo tee /etc/systemd/system/cocktailberry-kiosk.service > /dev/null << 'EOF'
[Unit]
Description=CocktailBerry Kiosk Mode
After=cocktailberry.service
Requires=cocktailberry.service

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/chromium-browser --kiosk --noerrdialogs \
  --disable-translate --disable-infobars \
  --app=http://localhost:5000
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cocktailberry-kiosk
sudo systemctl start cocktailberry-kiosk

# Otomatik login (boot'ta grafik ortam):
sudo raspi-config
# → System Options → Boot / Auto Login → Desktop Autologin
```

### Adım 5: Jarvis MQTT Entegrasyonu

```bash
# MQTT bridge script kur
# (siber_barmen_cocktailberry/cocktailberry_kiosk_setup.md dosyasına bak)

# Bridge servis:
sudo systemctl enable cocktailberry-mqtt
sudo systemctl start cocktailberry-mqtt

# HA'ya rest_command ekle (configuration.yaml):
# rest_command:
#   cocktailberry_make:
#     url: "http://raspberrypi.local:5000/api/make"
#     method: POST
#     content_type: "application/json"
#     payload: '{"recipe":"{{ recipe }}"}'

# HA'ya otomasyonları ekle:
# siber_barmen_cocktailberry/jarvis_mqtt_integration.yaml
```

### Adım 6: Test

```
1. Pi'yi boot et → CocktailBerry + Kiosk otomatik başlar
2. Ekrandan "Negroni" seç → pompalar çalışır → kokteyl hazır
3. Jarvis'e "Bana Negroni yap" de:
   → MQTT "jarvis/barmen/command" {"recipe":"negroni"}
   → Bridge → CocktailBerry REST API → pompalar çalışır
   → Bitti → MQTT "jarvis/barmen/recipe_done"
   → Jarvis "Kokteyliniz hazır" der
   → Lamba (Modül 29) yeşil yanar + başını sallar
4. Acil stop: Ekrandaki STOP butonu → tüm röleler OFF
5. Günlük limit: 5 kokteyl → 6.'da Jarvis reddeder
```

---

## Faz 17: Modül 32 — Yurt İklim ve Solunum Kalkanı

> **Kıbrıs rutubeti + klima boğaz kurutması → otonom iklim yönetimi**

### Adım 1: Hisense D16CW + Shelly Plug S Kurulumu

```
1. Hisense D16CW'yi yurt odasına yerleştir:
   → Duvara yakın (~30cm) ama hava akışı engellenmeyecek
   → Tank altına damarlık tepsisi (opsiyonel)
   → Sürekli drenaj hortumu tak (tank dolum sorununu önle)

2. Hisense'i manuel aç:
   → Mode: Continuous (sürekli nem alma)
   → Fan: Low (sessiz)
   → Bu ayar KALSIN — Shelly prizle sadece güç kes/aç yapacağız

3. Hisense güç kablosunu → Shelly Plug S prizine tak
4. Shelly Plug S'i → duvar prizine tak (akım korumalı priz üzerinden)
5. Shelly'yi GL-MT3000 WiFi ağına bağla:
   → Shelly app veya web UI (http://shellyplug-xxxx.local)
   → WiFi: yurt ağı, statik IP ayarla
   → HA'ya entegre et (Shelly integration veya MQTT)

6. Test:
   → Shelly ON → Hisense güç alır → Auto-Restart → çalışır
   → Shelly OFF → Hisense durur
   → Shelly ON → Hisense otomatik başlar (butona basmaya gerek yok)
```

### Adım 2: BME280 + ESP32 Nem Sensörü

```bash
# ESPHome ile BME280 sensörü flaşla
# (climate_respiratory_shield/bme280_esphome.yaml dosyasını kullan)

# 1. ESP32'yi USB ile bilgisayara bağla
# 2. ESPHome web UI'da yeni device oluştur
# 3. bme280_esphome.yaml içeriğini yapıştır
# 4. secrets.yaml oluştur:
#    wifi_ssid: "yurt_wifi"
#    wifi_password: "yurt_sifre"
#    ota_password: "gizli_sifre"
# 5. Install → Wire → ESP32'ye flaşla
# 6. ESP32 yurt WiFi'sine bağlanır → MQTT yayınlar
# 7. HA'da sensor.oda_nemi, sensor.oda_sicakligi görünür
```

### Adım 3: DIY Hava Temizleyici Montajı

```
1. HEPA H13 filtreyi kutuya yerleştir (alt kısım)
2. 12V PC fanını kutunun üstüne monte et (üfler → yukarı)
3. Fan güç → 12V 2A adaptör → Shelly Plug S (veya ESP32 PWM)
4. Kutu altında hava giriş delikleri aç (kirli hava girer)
5. Kutu üstünde fan çıkışı (temiz hava çıkar)

Akış: Aşağıdan kirli hava → HEPA filtre → yukarıdan temiz hava

6. Shelly/ESP32'yi HA'ya entegre et:
   → switch.diy_air_purifier
```

### Adım 4: HA Otomasyonlarını Yükle

```bash
# climate_shield_automation.yaml içeriğini HA configuration.yaml'a ekle
# (veya packages/ klasörüne kopyala)

# Otomasyon mantığı:
# GÜNDÜZ (07:00-23:00):
#   Nem > %55 (5 dk) → Klima KAPAT + Hisense AÇ (Shelly ON)
#   Nem < %45 (5 dk) → Hisense KAPAT (Shelly OFF)
#
# GECE (23:00-07:00):
#   Hisense KAPAT (sessiz uyku)
#   Klima → 26°C (Broadlink IR)
#   Swing → TARA / Vertical Up (hava tavana → boğaz koruması)
#
# SABAH (07:00):
#   Klima KAPAT
#   Hisense → nem > %55 ise aç, değilse kapalı kal
```

### Adım 5: Broadlink Klima Komutları Öğret

```
1. HA → Broadlink RM4 Mini → Learn Command
2. Klima kumandasından şu komutları öğret:
   → "power_on"    : Klima aç
   → "power_off"   : Klima kapat
   → "cool_26"     : 26°C soğutma modu
   → "swing_vertical_up" : Swing dikey → yukarı (hava tavana)
   → "swing_off"   : Swing kapat
3. HA climate entegrasyonu veya remote.send_command ile kullan
```

### Adım 6: Test Senaryosu

```
GÜNDÜZ TEST:
1. BME280 nemini %60'a getir (nemli bez veya duş)
2. 5 dk sonra → Otomasyon tetiklenir
3. Klima kapanır, Hisense açılır
4. Jarvis "Oda nemi %55'in üstüne çıktı" der
5. Nem %40'a düşene kadar bekle → Hisense kapanır

GECE TEST:
1. Saat 23:00 → Gece modu tetiklenir
2. Hisense kapanır (sessiz)
3. Klima 26°C'ye ayarlanır, swing tavana
4. Jarvis "İyi geceler. Boğaz koruması devrede" der

SABAH TEST:
1. Saat 07:00 → Sabah modu
2. Klima kapanır
3. Nem > %55 ise Hisense açılır
4. Jarvis "Günaydın" der

SESLİ KOMUT TEST:
1. "Odamın nemini kontrol et" → Jarvis nem ve sıcaklığı söyler
2. "Nem alıcıyı aç" → Shelly ON → Hisense çalışır
3. "Gece moduna geç" → Hisense OFF + Klima 26°C + Swing tavan
```

---

## Faz 2 (Güncelleme): Modül 33 — Yeelight Ambiyans Ampul (ELDE)

### Yeelight Bulb 1S Kurulumu

```
1. Yeelight Bulb 1S'i lamba dukosuna tak
2. Yeelight app (Android/iOS) ile WiFi'a bağla (GL-MT3000 ağı)
3. Ampulü app'te aç → cihaz ayarları → "LAN Control" AKTİFLEŞTİR
   (Eski firmware'de "Developer mode" olarak geçer)
4. Firmware güncelle (app içinden) — LAN Control için gerekli
5. HA → Settings → Devices → Add → Yeelight
   → Ampul otomatik keşfedilir (yerel ağ taraması)
6. light.yeelight_color_bulb_1s entity'si oluşur
7. (Opsiyonel) Music mode etkinleştir:
   → HA Yeelight entegrasyonu ayarları → "Use music mode"
   → >60 istek/dk limiti kalkar → hızlı efekt geçişleri
8. Test: HA'dan ampulü aç → renk değiştir → parlaklık ayarla
9. WLED (Modül 10) ile senkron otomasyonu:
   → "Sinema modu": Yeelight %10 kehribar + WLED off
   → "Parti modu": Yeelight renk döngüsü + WLED audio reactive
   → "Sabah": Yeelight yumuşak beyaz + WLED sunrise
```

> **Zero-Trust notu:** LAN Control açıkken ampul bulut komutu ALMAZ —
> HA yerel ağdan komut gönderir. Yeelight bulutu tamamen atlanır.

---

## Faz 5 (Güncelleme): Modül 34 — TV Medya Merkezi (Mi Box S — Planlanan)

### Mi Box S 4K (3rd Gen) Kurulumu

```
1. Mi Box S 4K'yi TV HDMI girişine tak (HDMI 2.1a destekler)
2. Güç bağla → Google TV 14 kurulum sihirbazı:
   → Google hesabı ile giriş
   → WiFi: GL-MT3000 ağına bağlan
3. Google Play'den gerekli app'leri kur:
   → Spotify (medya cast + kontrol)
   → Home Assistant Companion (HA kontrol paneli TV'de)
   → Tam ekran tarayıcı (MagicMirror² Kiosk için)
4. HA Android TV entegrasyonu:
   → HA → Settings → Devices → Add → Android TV
   → Mi Box IP'sini gir (GL-MT3000 admin panelinden bul)
   → ADB debugging aç: Mi Box → Settings → Device Preferences →
     About → Build Number 7 kez tıkla → Developer Options →
     USB Debugging / Network Debugging AKTİF
   → media_player.mi_box entity'si oluşur (power, volume, app kontrolü)
5. Chromecast (dahili):
   → HA Chromecast entegrasyonu otomatik keşfeder
   → media_player.mi_box_chromecast → jarvis_core medya cast hedefi
6. MagicMirror² Kiosk (Modül 4):
   → Tarayıcıda http://VPS_IP:8080 aç → tam ekran
   → "Fullscreen Browser" app ile otomatik açılış ayarla
7. Test: "Jarvis, Spotify'da Lo-Fi çal" → Mi Box Chromecast'e cast
8. Test: HA'dan Mi Box power off → TV kapanır (enerji tasarrufu)
```

---

## Faz 3 (Güncelleme): Tuya UK Akıllı Prizler (Planlanan)

### Tuya Priz Kurulumu (Hausberg + Hisense + Klima)

```
1. Tuya UK Smart Plug'ı duvar prizine tak
2. Tuya Smart app ile WiFi'a bağla (GL-MT3000 ağı):
   → App → Add Device → Socket → WiFi bilgileri
3. Cihaz adlandır:
   → "Coffee Machine Plug" (Hausberg HB3723)
   → "Multicooker Plug" (Hisense HMC6SBK)
   → "AC Power Plug" (klima geri besleme)
4. HA'a LocalTuya entegrasyonu ile ekle (HACS → Tuya Local):
   → Her priz için: device_id + local_key (Tuya IoT Platform'dan)
   → switch + power sensor entity'leri oluşur
5. Güç izleme testi:
   → Hausberg'i prize tak, aç → ~900W (ısınma) → ~50W (hazır)
   → Hisense'i prize tak, program başlat → ~1500W (pişirme)
6. Zero-Trust notu: LocalTuya yerel protokol kullanır —
   Tuya bulutu komut için gerekmez (yalnızca ilk eşleştirme)

> Alternatif: Shelly Plug S (yerel MQTT, bulut sıfır) — ama Tuya priz
> ~$12 vs Shelly ~$15 ve Tuya Smart app ile ilk kurulum daha kolay.
> LocalTuya ile ikisi de yerel çalışır.
```

---

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
| **Modül 31 (CocktailBerry)** | Pi 4 + röle + SMPS kabloları bar kovanı arkasında, sleeve ile gizli. Pompa kabloları kovan içinde düzenli |
| **Modül 32 (İklim Kalkanı)** | BME280 ESP32 kitaplık arkasında bantlı. Hisense + Shelly kablosu duvar kenarı kanalda. DIY hava temizleyici kablosu mobilya altında |

### Altın Kural

> **"Sensörlerin sadece uçları görünmeli. Kablolar asla."**
> Misafir odaya girdiğinde, teknolojiyi "fark etmemeli" — sadece "çalıştığını"
> deneyimlemeli. Sarkık bir kablo, tüm illüzyonu bozar. Kablo gizleme,
> "premium lounge" hissinin görünmez ama en kritik parçasıdır.

---

*Bu dosya, tüm parçalar alındıktan sonra eksiksiz kurulum için rehberdir. Her modülün kendi `hardware_and_*.md` dosyasında daha detaylı bilgi bulunur.*