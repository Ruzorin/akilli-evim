# car_stealth_and_seduction — Gizli Tetik ve Mod Mimarisi

> **Modül 23: Car Stealth & Seduction (Blackout, Seduction Suite, Sci-Fi Soundspace)**
> Tek tuşla araç içi tüm ekranları karartan "Night Ops / Blackout" modu, seduction mantığını arabaya taşıyan "Mobile Seduction Suite" ve OBD2'yi siberpunk ses'e dönüştüren "Sci-Fi Soundspace".

---

## 🔘 Gizli Fiziksel Tetik Mimarisi

### Direksiyon Tuşları → HA Otomasyon

```
  Direksiyon Tuşu (gizli)
       │ CAN Bus / Android
       ▼
  Android Multimedya (HA Companion App)
       │ Tailscale VPN → VPS
       ▼
  Home Assistant (otomasyon tetik)
       │ <100ms
       ▼
  Mod aktivasyon (Blackout / Seduction / Soundspace)
```

### Tetik Yöntemleri

| Yöntem | Gecikme | Kullanım |
|---|---|---|
| **Direksiyon tuş kombinasyonu** (örn: Vol+ + Vol- 3sn basılı) | <100ms | Gizli — misafir fark etmez |
| **Sesli komut** ("Jarvis, Blackout") | ~2sn | Sesli — Jarvis işler |
| **HA Companion App butonu** (araç içi ekranda) | <200ms | Dokunmatik |
| **Bluetooth buton** (araç içi gizli Zigbee buton) | <150ms | Fiziksel buton |

### Milisaniyelik Tetik Mekanizması

```
  Tetik → Android (HA Companion App) → Tailscale VPN → VPS (HA)
       │
       ▼ <100ms (Tailscale WireGuard = düşük gecikme)
  HA otomasyon → MQTT → araç içi cihazlar
       │
       ├── Ekran parlaklığı → 0% (Android brightness control)
       ├── WLED → kırmızı/amber (MQTT → ESP32 → LED)
       ├── Difüzör → imza koku (MQTT → Tuya)
       ├── Spotify → fade-in (HA → media_player)
       └── Sci-Fi ses → OBD2 senkron (Python → audio stream)
```

> **"God Mode" hissi:** Sürücü tek tuşa basar → 100ms içinde tüm araç dönüşür. Ekranlar kararır, ışıklar kırmızıya döner, koku yayılır, müzik başlar, motor sesi siberpunk'a dönüşür. "Tony Stark bir düğmeye basar ve dünya değişir."

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | (Yazılım) | HA Companion App (Android) | — | $0 | Direksiyon tuşu → HA |
| 2 | (Opsiyonel) | Zigbee mini buton (araç içi gizli) | 1 | ~$10 | Direksiyon altına gizli |
| 3 | (Opsiyonel) | Araç içi WLED şerit (ayak/kapı) | 1m | ~$5 | ESP32 + WS2812B |
| 4 | (Opsiyonel) | Araç içi USB difüzör | 1 | ~$20 | Imza koku için |

> **Toplam ekstra maliyet: ~$0-35** (mevcut altyapı + opsiyonel WLED/difüzör)

---

## ✅ Kurulum Kontrol Listesi

- [ ] Direksiyon tuş kombinasyonu → HA Companion App → HA otomasyon tetik
- [ ] "Jarvis, Blackout" sesli komut → HA conversation → otomasyon
- [ ] `stealth_blackout_protocol.yaml` HA'a yüklendi
- [ ] `mobile_seduction_suite.yaml` HA'a yüklendi
- [ ] `scifi_soundspace_augmenter.py` Pi 4'te çalışıyor
- [ ] Test: "Jarvis, Blackout" → ekran %0, konsol ışıkları off, HUD aktif
- [ ] Test: "Date Mode" → WLED kırmızı, difüzör imza koku, Spotify R&B fade-in
- [ ] Test: Gece sürüşü → OBD2 RPM → Sci-Fi motor sesi (hoparlörden)