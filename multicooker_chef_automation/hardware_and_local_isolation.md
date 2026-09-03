# multicooker_chef_automation — Donanım, Mealie ve Yerel İzolasyon

> **Modül 28: Multicooker Chef Automation**
> Jarvis'in mutfaktaki "kasları" — Mealie (açık kaynak tarif yöneticisi) +
> **Hisense HMC6SBK 6L Multicooker (ELDE — Eylül 2026)**, Tuya akıllı prizle güç izleme
> Thermomix/Cookidoo'ya açık kaynak rakibi
> Modül 13 (Vision Chef) görür → Mealie eşleştirir → priz izler → Jarvis bildirir

> **⚠️ EKİPMAN DEĞİŞİKLİĞİ (Eylül 2026):** Xiaomi Mi Smart Multi Cooker 3L yerine
> **Hisense HMC6SBK 6L** alındı. 2× kapasite (6L), 2× güç (1500W), basınçlı pişirme VAR.
> WiFi YOK → Çin bulutu izolasyonu (iptables) ARTIK GEREKMEZ — sıfır bulut riski.
> "Akıllı" kısım: Tuya akıllı priz güç izleme (1500W pişirme → 40W keep-warm tespiti)
> + Vision-Cooker orkestrasyonu (kamera + Mealie + Jarvis).

---

## 🆚 Thermomix vs Jarvis + Mealie + Hisense HMC6SBK

| Özellik | Thermomix TM6 (~100.000₺) | Jarvis + Mealie + Hisense (~3.500₺) |
|---------|---------------------------|--------------------------------------|
| **Tarif veritabanı** | Cookidoo (kapalı, abonelik) | Mealie (açık kaynak, ücretsiz) |
| **Tarif ekleme** | Sadece Cookidoo'dan | Herhangi bir siteden URL scrape |
| **Makro hesabı** | Yok (sabit tarifler) | DeepSeek → sporcu hedefine göre dinamik |
| **Porsiyon ölçekleme** | Manuel | Otomatik (DeepSeek + Mealie API) |
| **Görüntü tanıma** | Yok | Qwen-VL Max (Modül 13) tezgahı görür |
| **Sesli kontrol** | Yok | MiniMax Speech 2.8 Turbo |
| **Fiziksel bildirim** | Yok | Yeelight flash + WLED turuncu (pürüzsüz) |
| **VSS koruması** | Yok | WLED strobe YASAK, pürüzsüz geçiş |
| **Bulut bağımlılığı** | Cookidoo bulutu (zorunlu) | SIFIR — Hisense WiFi'siz, priz yerel (LocalTuya) |
| **Kapasite** | 2.2L | 6L (misafir yemeği) |
| **Basınçlı pişirme** | Var | Var (Hisense HMC6SBK) |
| **Yemek planı** | Cookidoo takvimi | Mealie takvimi (REST API) |
| **Alışveriş listesi** | Cookidoo | Mealie (otomatik oluşturma) |
| **Toplam maliyet** | ~100.000₺ + abonelik | ~3.500₺ (tek seferlik) |

> **Sonuç:** Thermomix'in 100.000₺'lik kapalı Cookidoo ekosistemi yerine,
> Mealie (açık kaynak) + Hisense HMC6SBK 6L (~3.500₺) ile aynı
> fonksiyonları fazlasıyla karşılar. Üstelik makro hesabı, görüntü tanıma
> ve sesli kontrol Thermomix'te YOK. Hisense WiFi'siz olduğu için Çin bulutu
> riski sıfırdır — Xiaomi'deki iptables izolasyonu bile gerekmez.

---

## 🍲 Hisense HMC6SBK — Güç İzleme Stratejisi (WiFi'siz "Akıllı" Tencere)

| Durum | Güç (Tuya priz) | HA Tespiti |
|---|---|---|
| Kapalı/bekleme | 0-2W | `switch` OFF konumunda |
| Isınma/pişirme | 1200-1500W | `binary_sensor.multicooker_cooking` ON (2 dk üstünde) |
| Keep-warm (sıcak bekleme) | 30-50W | `binary_sensor.multicooker_done` ON (3 dk üstünde) |

```
Vision-Cooker kapalı döngü (güncellenmiş):
1. Tapo C200 (Modül 13) tezgaha bakar → Qwen-VL malzemeleri tanır
2. Mealie'de tarif eşleştirir → Jarvis önerir ("Bunlardan ne çıkar?")
3. Kullanıcı onaylar → malzemeler Hisense'e konur → program seçilir
4. Tuya prizden güç izleme: 1500W (pişirme başladı)
5. Güç 40W'a düşer (keep-warm) → "Pişirme bitti"
6. Jarvis "Yemeğiniz hazır" der → WLED turuncu → Yeelight flash
   → (Beklemede: Lamba Modül 29 başını sallar)
```

---

## 📚 Mealie — Açık Kaynak Tarif Yöneticisi

### Nedir?

Mealie, kendi sunucunuzda çalışan açık kaynak tarif yöneticisi ve yemek
planlayıcısıdır. REST API (FastAPI + Swagger) ile tam kontrol sağlar.
URL yapıştırarak herhangi bir siteden tarif scrape eder.

| Özellik | Detay |
|---------|-------|
| **Kaynak** | https://github.com/mealie-recipes/mealie |
| **Lisans** | AGPL-3.0 (açık kaynak) |
| **Sürüm** | 3.13+ (2026) |
| **API** | REST API (FastAPI + Swagger docs) |
| **Veritabanı** | SQLite (varsayılan) veya PostgreSQL |
| **Scrape** | URL yapıştır → otomatik malzeme/talimat/besin çıkarımı |
| **Yemek Planı** | Takvim görünümü, haftalık/aylık plan |
| **Alışveriş Listesi** | Yemek planından otomatik oluşturma |
| **Webhook** | Yemek planı bildirimleri (3. parti servisler) |
| **Çok Kullanıcı** | Household grupları (aile paylaşımı) |

### Docker Kurulumu (VPS veya Pi)

```yaml
# docker-compose.yaml
services:
  mealie:
    image: ghcr.io/mealie-recipes/mealie:latest
    container_name: mealie
    restart: always
    volumes:
      - ./volumes/mealie:/app/data/
    ports:
      - "9925:9000"
    environment:
      PUID: 1000
      PGID: 1000
      TZ: Europe/Istanbul
      TOKEN_TIME: 87600  # 10 yıl token
```

```bash
# Başlat
docker compose up -d

# API docs: http://localhost:9925/docs
# UI: http://localhost:9925
```

### REST API Endpoint'leri

| Endpoint | Metod | İşlev |
|----------|-------|-------|
| `/api/auth/token` | POST | Bearer token al (giriş) |
| `/api/recipes/create/url` | POST | URL'den tarif scrape et |
| `/api/recipes/{slug}` | GET | Tarif detayı (malzeme, talimat, besin) |
| `/api/recipes/{slug}` | PUT | Tarif güncelle (porsiyon ölçekle) |
| `/api/recipes` | GET | Tarif ara/listele |
| `/api/households/mealplans` | POST | Yemek planı oluştur |
| `/api/parser/ingredients` | POST | Malzeme parse (nlp/brute/openai) |

---

## 🍳 Donanım Seçimi

### Önerilen: Xiaomi Mi Smart Multi Cooker (3L)

| Özellik | Detay |
|---------|-------|
| **Model** | Xiaomi Mi Smart Multi Cooker 3L (chunmi.cooker.normal4) |
| **Kapasite** | 3 litre (yurt odası için yeterli) |
| **Güç** | 700W |
| **WiFi** | 2.4GHz (GL-MT3000 ağına bağlanır) |
| **HA Entegrasyonu** | Xiaomi Miot Auto (HACS) — `miot_local: true` |
| **Yerel Kontrol** | ✅ miot-spec LAN mode destekler |
| **Fiyat** | ~1.500-2.000₺ |

### Alternatif: Tuya Akıllı Multicooker

| Özellik | Detay |
|---------|-------|
| **Model** | Tuya Smart Multicooker (çeşitli markalar) |
| **HA Entegrasyonu** | Tuya Local (HACS) — LocalTuya |
| **Yerel Kontrol** | ✅ Local key ile tam yerel |
| **Avantaj** | Daha ucuz (~800-1.200₺) |
| **Dezavantaj** | DP eşlemesi manuel gerekir |

### Karşılaştırma

| Kriter | Xiaomi Miot Auto | Tuya Local |
|--------|-----------------|------------|
| **Kurulum** | Otomatik keşif | Manuel DP eşleme |
| **Yerel mod** | `miot_local: true` | Local key gerekir |
| **Stabilite** | Yüksek (miot-spec) | Orta (Tuya protokol) |
| **Cloud bağımlılık** | İlk kurulum sonra yok | İlk kurulum sonra yok |
| **Fiyat** | ~1.500₺ | ~1.000₺ |
| **Öneri** | ✅ **Önerilen** | Bütçe alternatifi |

---

## 🔒 Yerel İzolasyon — Çin Bulutunu Koparma

### Adım 1: Cihazı WiFi'a Bağla (Geçici)

```
1. Xiaomi Home / Tuya Smart app ile cihazı WiFi'a bağla
2. Cihazın IP adresini router'dan not et (örn: 192.168.1.108)
3. Cihazın MAC adresini not et (router → DHCP listesi)
```

### Adım 2: HA Entegrasyonu Kur

#### Xiaomi Miot Auto (Önerilen)

```yaml
# HACS → Integrations → Xiaomi Miot Auto → Install
# HA → Settings → Devices → Add → Xiaomi Miot Auto
# Xiaomi hesabınla giriş yap → Cihaz otomatik keşfedilir

# configuration.yaml — Yerel mod zorla
xiaomi_miot:
  device_customizes:
    'chunmi.cooker.normal4':
      miot_local: true       # Yerel LAN modu ZORLA
      chunk_properties: 7    # Toplu özellik okuma
```

```yaml
# customize.yaml — Entity bazında yerel mod
domain.chunmi_cooker:
  miot_local: true            # Cloud'a çıkma, yerel LAN kullan
  miot_cloud: false           # Cloud tamamen kapalı
  check_lan: true             # LAN bağlantısını doğrula
```

#### Tuya Local (Alternatif)

```yaml
# HACS → Integrations → Tuya Local → Install
# Tuya IoT Platform (iot.tuya.com) → Cloud project → Local key al
# HA → Settings → Devices → Add → Tuya Local
# Cihaz IP + Local key gir → Cihaz yerel olarak eklenir
```

### Adım 3: Router'dan İnterneti Kes (KRİTİK)

```
GL-MT3000 Admin Panel → Firewall → Access Control

1. Yeni kural oluştur:
   - Hedef: 192.168.1.108 (Multicooker IP)
   - veya MAC: AA:BB:CC:DD:EE:FF (Multicooker MAC)
   - Eylem: BLOCK (WAN yönünde)
   - Protokol: ALL

2. Kuralı aktif et → Cihaz internete çıkamaz
3. Sadece yerel ağ (LAN) içinde HA ile konuşur
```

**GL-MT3000 komut satırı (SSH):**
```bash
# Multicooker IP'sini internetten kes
iptables -A FORWARD -s 192.168.1.108 -j DROP
iptables -A FORWARD -d 192.168.1.108 -j DROP

# Kalıcı yap
/etc/init.d/firewall save
```

### Adım 4: MQTT Bridge (Opsiyonel)

HA entegrasyonu zaten yerel kontrol sağlar, ama MQTT bridge ile
daha hızlı tepki için:

```yaml
# HA → MQTT bridge
mqtt:
  climate:
    - name: "Smart Multicooker"
      modes:
        - "cook"      # Pişirme modu
        - "keep_warm" # Sıcak tutma
        - "soup"      # Çorba
        - "rice"      # Pilav
        - "porridge"  # Lapa
      temperature_command_topic: "multicooker/command/temperature"
      mode_command_topic: "multicooker/command/mode"
      mode_state_topic: "multicooker/state/mode"
```

---

## 📊 Multicooker HA Entity'leri

| Entity | Tip | İşlev |
|--------|-----|-------|
| `climate.smart_multicooker` | climate | Sıcaklık + mod kontrolü |
| `switch.multicooker_power` | switch | Aç/kapa |
| `sensor.multicooker_temperature` | sensor | Mevcut sıcaklık |
| `sensor.multicooker_remaining_time` | sensor | Kalan süre |
| `sensor.multicooker_status` | sensor | Durum (idle/cooking/keep_warm) |
| `binary_sensor.multicooker_cooking` | binary_sensor | Pişirme aktif mi? |

---

## 🔗 İlgili Dosyalar

- [`vision_cooker_orchestration.yaml`](vision_cooker_orchestration.yaml) — Modül 13 + 28 kapalı döngü
- [`cooking_notification_automation.yaml`](cooking_notification_automation.yaml) — MiniMax + WLED bildirim
- [`config.yaml`](config.yaml) — Modül konfigürasyonu