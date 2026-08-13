# SAFETY — Jarvis Embodied Avatar

> Güvenlik sınırları — LLM üzerinden GEÇMEZ, doğrudan HAL'da uygulanır.

## Motion

### Servo Açı Sınırları (Derece)

| Eksen | Min | Max | Neden |
|-------|-----|-----|-------|
| Base | 0° | 180° | Masa tabanı rotasyon |
| Shoulder | 30° | 150° | Kol yukarı/aşağı — 30° altı çarpışma riski |
| Elbow | 0° | 135° | Kol büküm — 135° üstü mekanik stres |
| Wrist Pitch | 0° | 180° | Kafa yukarı/aşağı |
| Wrist Roll | 0° | 180° | Kafa sağa/sola |

### Hareket Hızı

- **Maksimum:** 60°/saniye (ani hareket = mekanik şok)
- **Yumuşak hareket:** 2° adım, 30ms delay → pürüzsüz geçiş
- **E-STOP:** PWM anında kesilir, tüm servolar donar

### E-STOP Tetikleyicileri

1. MQTT `jarvis/lamp/safety/estop` komutu
2. Servo açı sınırı aşılmaya çalışıldığında (otomatik reddet)
3. Sistem sağlığı kritik (healthwatch)
4. MQTT bağlantısı 30 sn kesildi (watchdog)

## Light

### Parlaklık Sınırları

- **Maksimum:** %80 (VSS için — tam parlaklık aşırı uyarıcı)
- **Gece modu:** %15 (22:00-07:00 — otomatik)
- **Titreşim frekansı:** Max 2Hz (VSS tetikleyici — hızlı titreşim yasak)

### Renk Sınırları (VSS Koruması)

- ✅ **İzinli:** Kehribar (255, 191, 0), Sıcak beyaz (255, 180, 120), Kırmızı (180, 0, 0)
- ❌ **Yasak:** Saf beyaz (255, 255, 255), Mavi (0, 0, 255), Hızlı renk değişimi
- **Neden:** VSS hastaları beyaz/mavi ışıkta kar desisi artar

## Audio

### Ses Seviyesi

- **Maksimum:** %65 (startup_volume)
- **Gece modu:** %30 (22:00-07:00)
- **Gece sessiz saat:** 00:00-07:00 → sadece fiziksel hareket, ses yok

## Privacy

- Kamera karesi YEREL işlenir (MediaPipe) — Cloud'a sadece açı değeri gönderilir
- Mikrofon sesi sadece aktif komut sırasında gönderilir
- Sürekli kayıt YOK — on-demand ve komut tetikli