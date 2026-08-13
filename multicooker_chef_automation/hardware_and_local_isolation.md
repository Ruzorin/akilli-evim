# multicooker_chef_automation — Donanım Seçimi ve Yerel İzolasyon

> **Modül 28: Multicooker Chef Automation**
> Jarvis'in mutfaktaki "kasları" — ticari akıllı tencere, yerel ağda izole
> Modül 13 (Vision Chef) görür → Modül 28 (Cooker) pişirir

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