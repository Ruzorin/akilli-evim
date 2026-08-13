---
schema: autonomous.device.v1
id: jarvis-lamp
name: Jarvis Embodied Avatar
type: desk_robot
boards:
  - raspberry_pi_4
  - raspberry_pi_5
gateway:
  default:
    protocol: websocket
  # Beyin Cloud VPS'te — OpenClaw runtime MQTT üzerinden komut gönderir
  # Pi sadece "gövde" — agentic runtime DISABLE
  remote:
    protocol: mqtt
    broker: "100.x.x.x"  # Cloud VPS Tailscale IP
    port: 1883
voice:
  tts_provider: minimax  # MiniMax Speech 2.8 Turbo (Cloud VPS'te)
capabilities:
  audio:
    routes:
      speaker:
        required: true
      voice:
        required: true
  vision:
    routes:
      camera:
        driver: opencv
        required: true
  sensing:
    routes:
      posture:
        required: true  # MediaPipe Pose — postür analizi
    required: true
  presence:
    required: true
  motion:
    routes:
      servo:
        driver: pca9685  # Özel driver — MG996R + PCA9685
        required: true
        safety: SAFETY.md#motion
  light:
    routes:
      led:
        driver: ws2812
        required: true
        safety: SAFETY.md#light
  expression:
    required: true
  media:
    required: true
  connectivity:
    routes:
      bluetooth:
        required: false
  companion:
    required: false
  system:
    required: true
soul_ref: SOUL.md
safety_ref: SAFETY.md
memory:
  backend: remote  # Hafıza Cloud VPS'te (DeepSeek + HA)
startup_volume: 65
---

# Jarvis Embodied Avatar

DIY 5-DOF robotik masa lambası — Jarvis'in masadaki "fiziksel yüzü".

## Body

Ağırlıklı taban, 5-servo eklemli kol (MG996R × 3 + SG90 × 2, PCA9685 I2C
üzerinden), kehribar LED halkası (WS2812, 12 LED), Raspberry Pi Camera V2,
INMP441 I2S mikrofon, ve MAX98357A I2S hoparlör sürücü. İşlemci Raspberry
Pi 4. Gövde `hal/board/board.py`'ye göre kablolanır; ajan doğrudan
donanıma erişmez.

## What the agent should assume

- Kullanıcı fiziksel olarak yakında, özel bir alanda (yurt odası).
- Kamera ve mikrofon hassas — yerel işlemeyi tercih et, yeni kullanımlar
  için izin iste.
- Hareket insanları şaşırtabilir. Nazik, anlaşılır hareket et, komutla dur.
- Işık ve hareket iletişim kanallarıdır, dekorasyon değil.
- Kullanıcı 210 cm boyunda, Visual Snow Syndrome (VSS) ile mücadele ediyor —
  parlak/karlı ışıktan kaçın, kehribar/sıcak tonları tercih et.
- Postür koruması kritik — kullanıcı "Tech Neck" yaparsa fiziksel olarak
  müdahale et (kullanıcıya uzan, kehribar titre, uyar).

## Edge Mode

Bu cihaz "beyinsiz gövde" olarak çalışır — agentic runtime DISABLE.
Beyin Cloud VPS'te (Home Assistant + OpenClaw + DeepSeek V4-Pro).
Pi sadece sensör verisi toplar ve motor komutları uygular.
MQTT + Tailscale VPN ile düşük gecikmeli haberleşme.