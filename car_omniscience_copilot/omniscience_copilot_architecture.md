# car_omniscience_copilot — Gözetmen Copilot Mimarisi

> **Modül 22: Car Omniscience Copilot (Dalgınlık, Kehanet ve G-Kuvveti)**
> 2.10m/125kg kullanıcının omurga yükünü izlemek, OBD2'den arıza kehaneti, IR kamera ile sürücü dalgınlığı tespiti ve G-Kuvveti optimizasyonu.

---

## 🧠 Omniscience Copilot — Sensor Fusion Mimarisi

### Veri Kaynakları

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    ARAÇ (Omniscience Copilot)                 │
  │                                                             │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
  │  │ IR Kamera     │  │ Akıllı Saat  │  │ OBD2 Wi-Fi        │  │
  │  │ (Sürücü yüzü) │  │ (Nabız, HRF) │  │ (MAF, yağ, şanz.) │  │
  │  │ → PERCLOS     │  │ → Stres      │  │ → Anomali tespiti │  │
  │  │ → Esneme      │  │ → Yorgunluk  │  │ → Kehanet        │  │
  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
  │         │                  │                    │            │
  │  ┌──────┴──────────────────┴────────────────────┴─────────┐  │
  │  │  Android Multimedya (Tailscale → VPS)                    │  │
  │  │  - Webhook → HA (saniyede veri akışı)                   │  │
  │  │  - AI süzme: GPT-5.6 / Gemini 3.6 (anomali → uyarı)     │  │
  │  └────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
          │ Tailscale VPN
          ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  VPS: Home Assistant + jarvis_core 3.0                       │
  │  - Sensor Fusion: IR + Saat + OBD2 → Gemini 3.6             │
  │  - Anomali tespiti → Jarvis sesli uyarı (<2sn)              │
  │  - Kehanet: "Yağ basıncı düşüyor, 500 km içinde bakım"     │
  └─────────────────────────────────────────────────────────────┘
```

### Veri Akışı ve AI Süzme

| Kaynak | Veri | Frekans | AI Süzme |
|---|---|---|---|
| **IR Kamera** | Yüz mikro-ifadeleri, göz kırpma, esneme | 10 FPS | GPT-5.6 Vision → PERCLOS hesapla |
| **Akıllı Saat** | Nabız, HRV (kalp atış varyabilitesi), stres | 1 Hz | Gemini 3.6 → yorgunluk skoru |
| **OBD2** | MAF, silindir ateşleme, yağ basıncı, şanzıman sıcaklığı | 10 Hz | Anomali tespiti (istatistiksel) |
| **GPS + İvmeölçer** | Hız, ivme, G-kuvveti, viraj açısı | 10 Hz | Sürtünme katsayısı hesapla |

### Gecikmesiz Uyarı Mekanizması

```
  Sensör verisi → Android (Webhook) → Tailscale → VPS (HA)
       │
       ▼ (<500ms)
  HA otomasyon → eşik kontrolü
       │
       ├── Normal → sessiz (kayıt only)
       ├── Anomali → Jarvis TTS (<2sn) → "Efendim, yorgun görünüyorsunuz"
       └── KRİTİK → Jarvis TTS + mobil bildirim + klima/difüzör/koltuk aksiyonu
```

> **"Tanrı Kompleksi" titizliği:** Sistem her veriyi süzgeçten geçirir. Normal → sessiz. Anomali → uyarı. Kritik → müdahale. Sürücü farkında olmadan korunur.

---

## 📋 Gerekli Donanım

| # | Bileşen | Model / Tip | Adet | Fiyat (≈) | Not |
|---|---|---|---|---|---|
| 1 | IR Kamera | FLIR One / Seek Thermal (USB-C) | 1 | ~$200 | Sürücü yüzü → PERCLOS (gece görüş) |
| 2 | OBD2 Wi-Fi | ELM327 Wi-Fi (Bluetooth yerine) | 1 | ~$20 | Daha hızlı veri akışı (10 Hz) |
| 3 | Akıllı Saat | Apple Watch / Wear OS (mevcut) | — | $0 | Nabız, HRV, stres (Modül 16 ile paylaşımlı) |
| 4 | GPS | Android dahili GPS | — | $0 | Hız, konum |
| 5 | İvmeölçer | Android dahili / MPU6050 | — | $0 | G-kuvveti, ivme |

> **Toplam ekstra maliyet: ~$220** (IR kamera + OBD2 Wi-Fi adaptörü)

---

## ✅ Kurulum Kontrol Listesi

- [ ] IR kamera (FLIR One / Seek Thermal) Android ekranına bağlandı
- [ ] OBD2 Wi-Fi adaptörü takıldı → Android'e bağlandı
- [ ] Akıllı saat → HA webhook → nabız/HRV verisi geliyor
- [ ] `fatigue_and_ergonomic_guard.py` Pi 4'te çalışıyor
- [ ] `predictive_maintenance_obd2.py` Pi 4'te çalışıyor
- [ ] `g_force_and_driving_dynamics.yaml` HA'a yüklendi
- [ ] Test: 2 saat sürüş → PERCLOS > %15 → "Yorgun görünüyorsunuz" + klima -2°C + nane difüzör
- [ ] Test: OBD2 yağ basıncı düşük → "500 km içinde yağ bakımı" kehaneti
- [ ] Test: Yağmurlu zemin + viraj → "Kaygan zemin, yavaşlayın" uyarısı