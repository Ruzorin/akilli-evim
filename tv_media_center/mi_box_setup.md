# 📺 Modül 34: TV Medya Merkezi — Mi Box S 4K Kurulumu

> **"TV artık sadece TV değil — ayna, medya merkezi ve HA kontrol paneli."**

## 📦 Donanım

| Bileşen | Model | Fiyat (≈) | Durum |
|---|---|---|---|
| TV Box | Xiaomi TV Box S 4K 32GB WiFi 6 (3rd Gen) | ~$60 | 🔄 Planlanan |
| TV | Yeni TV (mevcut TV'nin IR alıcısı arızalı) | — | 🔄 Değişecek |

## 🔧 Kurulum Adımları

### 1. Mi Box Temel Kurulum

```
1. Mi Box S 4K'yi TV HDMI girişine tak (HDMI 2.1a)
2. Güç bağla → Google TV 14 kurulum sihirbazı:
   → Dil: Türkçe/İngilizce
   → Google hesabı ile giriş
   → WiFi: GL-MT3000 ağına (JarvisNet) bağlan
3. Google Play'den app'leri kur:
   → Spotify (medya cast + kontrol)
   → Home Assistant Companion (HA panel TV'de)
   → Tam ekran tarayıcı (MagicMirror² Kiosk için)
   → Netflix / YouTube / Prime Video (medya)
```

### 2. HA Android TV Entegrasyonu (ADB)

```
1. Mi Box'ta geliştirici modunu aç:
   Settings → Device Preferences → About →
   Build Number'a 7 kez tıkla → "You are now a developer"
2. ADB debugging aç:
   Settings → Device Preferences → Developer Options →
   USB Debugging → ON
   Network Debugging → ON (IP üzerinden ADB)
3. Mi Box IP'sini bul (GL-MT3000 admin paneli → DHCP listesi)
4. HA → Settings → Devices → Add → Android TV:
   → IP: 192.168.8.XXX
   → Mi Box ekranında "Allow USB debugging?" → OK (her zaman)
5. media_player.mi_box entity'si oluşur:
   → Power on/off, volume, app launch, home/back
```

### 3. Chromecast (Dahili)

```
1. HA Chromecast entegrasyonu Mi Box'ı otomatik keşfeder
   (aynı ağda — GL-MT3000)
2. media_player.mi_box_chromecast oluşur
3. jarvis_core medya cast hedefi olarak kaydet:
   → "Spotify'da Lo-Fi çal" → Chromecast'e cast
   → "YouTube'da X oynat" → Chromecast'e cast
```

### 4. MagicMirror² Web Kiosk (Modül 4 — Pi'siz Ayna)

```
1. VPS'te MagicMirror² Docker çalışıyor (Modül 4):
   http://VPS_IP:8080
2. Mi Box tarayıcısında aç → tam ekran (Kiosk)
3. Otomatik açılış:
   → "Fullscreen Browser" app kur
   → Startup URL: http://VPS_IP:8080
   → Boot'ta otomatik aç
4. (Opsiyonel) Two-way mirror akrilik TV önüne:
   → TV kapalı = ayna, TV açık = MagicMirror²
```

### 5. HA Otomasyonları

```yaml
# Örnek: Netflix & Chill otomasyonu (Modül 8 güncellemesi)
automation:
  - id: "netflix_and_chill"
    alias: "Netflix & Chill"
    trigger:
      - platform: mqtt
        topic: "jarvis/tv/command"
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.action == 'netflix_chill' }}"
    action:
      # Mi Box'ta Netflix aç (ADB)
      - service: media_player.select_source
        target:
          entity_id: media_player.mi_box
        data:
          source: "Netflix"
      # Sinema ışıkları (Yeelight + WLED)
      - service: mqtt.publish
        data:
          topic: "jarvis/yeelight/scene"
          payload: '{"scene":"cinema"}'
      # Klima sessiz mod (Tuya IR+RF)
      - service: remote.send_command
        target:
          entity_id: remote.tuya_ir_rf
        data:
          command: "klima_quiet_22"
```

### 6. Test Senaryosu

```
1. "Jarvis, televizyonu aç" → media_player.mi_box ON (ADB)
2. "Jarvis, Netflix aç" → Netflix app launch + sinema ışıkları
3. "Jarvis, Spotify'da Lo-Fi çal" → Chromecast cast
4. "Jarvis, aynayı göster" → Tarayıcı Kiosk → MagicMirror²
5. "Jarvis, televizyonu kapat" → Mi Box OFF → TV standby
6. Oda boş 1 saat → Mi Box otomatik kapanır (enerji tasarrufu)
```

## 🔒 Zero-Trust Notları

| Kural | Açıklama |
|---|---|
| **ADB yerel** | Android TV entegrasyonu yerel ağ üzerinden ADB — bulut yok |
| **Chromecast yerel** | Cast protokolü yerel mDNS — Google bulutu komut için gerekmez |
| **Mi Box Google hesabı** | Play Store için Google hesabı gerekir (tek bulut teması) — ama HA kontrolü tamamen yerel |
| **MagicMirror² VPS'te** | Web sayfası Tailscale ağından — dışarıya açık değil |

---

*Bu dosya, Mi Box S 4K kurulumunu ve TV'nin üç işlevli (medya + ayna + kontrol paneli) kullanımını detaylandır. TV değişimi + Mi Box alımı sonrası kurulur.*
