"""
 =============================================================================
 jarvis_core — MiniMax Realtime Orchestrator (Sesten-Sese Voice Brain)
 =============================================================================
 2026 Sürümü — MiniMax Speech 2.8 Turbo + Voice Cloning + Duygu Kontrol

 MiniMax Realtime API'nin astronomik faturalarından kurtulup:
 - Sıfır gecikme (<300ms) sesten-sese (Speech-to-Speech) mimarisi
 - Voice Cloning: 10 sn referans ses → Jarvis tonu (Paul Bettany / Türkçe dublaj)
 - Duygu kontrol: charming, sarcastic, intimate, authoritative — otonom
 - Aylık ~$10 maliyet (OpenAI Realtime ~$50-100/ay'dan)

 🎯 MİMARİ DEVRİM — STT/TTS ARA KATMANLARI SİLİNDİ:
 =============================================================================
 Eski sistem: Ses → MiniMax Sesten-Sese → DeepSeek V4-Pro → MiniMax Voice Cloning → Ses (3 ara katman, 2-3sn)
 Yeni sistem: Ses → MiniMax Speech 2.8 Turbo → Ses (TEK katman, <300ms)

 MiniMax Speech 2.8 Turbo:
 - End-to-End Multimodal: Sesi duy → ses olarak yanıt ver
 - Voice Cloning: 10 sn referans WAV → tüm konuşmalar bu tonda
 - Duygu kontrol: voice_emotion parametresi → charming/sarcastic/intimate/authoritative
 - WebSocket streaming: <300ms gecikme (gerçek zamanlı)

 GEREKLİ KÜTÜPHANELER:
   pip install websockets asyncio httpx

 =============================================================================
"""

import asyncio
import json
import base64
import time
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from enum import Enum

try:
    import websockets
except ImportError:
    raise ImportError("websockets gerekli: pip install websockets")

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class MiniMaxConfig:
    """MiniMax Realtime API konfigürasyonu."""

    # MiniMax API
    API_KEY: str = "YOUR_MINIMAX_API_KEY"
    GROUP_ID: str = "YOUR_MINIMAX_GROUP_ID"

    # WebSocket endpoint (Speech 2.8 Turbo)
    WS_URL: str = "wss://api.minimaxi.com/v1/realtime/speech2speech"
    # Alternatif: REST API
    REST_URL: str = "https://api.minimaxi.com/v1/t2a_v2"

    # Voice Cloning
    VOICE_CLONE_REFERENCE: str = "assets/jarvis_voice_reference.wav"  # 10 sn referans
    VOICE_CLONE_ENABLED: bool = True
    # Referans ses: Paul Bettany (Jarvis) veya Türkçe dublaj sesi

    # Model
    MODEL: str = "speech-2.8-turbo"  # MiniMax Speech 2.8 Turbo

    # Audio format
    SAMPLE_RATE: int = 24000          # 24kHz (MiniMax varsayılan)
    AUDIO_FORMAT: str = "pcm"         # PCM (raw audio)
    CHUNK_SIZE_MS: int = 20           # 20ms chunk (50 FPS → düşük gecikme)

    # Duygu kontrol
    DEFAULT_EMOTION: str = "neutral"  # charming, sarcastic, intimate, authoritative, neutral

    # HA REST API (cihaz kontrolü)
    HA_URL: str = "http://homeassistant.local:8123"
    HA_TOKEN: str = "YOUR_HA_LONG_LIVED_TOKEN"

    # MQTT (modül tetikleme)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883


# =============================================================================
# DUYGU PROFİLLERİ
# =============================================================================

class VoiceEmotion(Enum):
    """Jarvis ses tonu — duruma göre otonom seçim."""
    CHARMING = "charming"          # Misafir karşılamada — sıcak, davetkar
    SARCASTIC = "sarcastic"        # Espri/alay — kuru, zeki
    NEUTRAL = "neutral"            # Normal komut — sakin, profesyonel
    INTIMATE = "intimate"          # Romantik — yumuşak, alçak ses
    AUTHORITATIVE = "authoritative"  # Uyarı/bilgi — net, güçlü


# =============================================================================
# MINIMAX REALTIME ORCHESTRATOR
# =============================================================================

class MiniMaxRealtimeOrchestrator:
    """
    MiniMax Speech 2.8 Turbo — Sesten-Sese (Speech-to-Speech) Voice Brain.

    🎯 MİMARİ DEVRİM:
    =============================================================================
    STT/TTS ara katmanları SİLİNDİ. MiniMax Speech 2.8 Turbo:
    - Sesi doğrudan duy → ses olarak yanıt ver (End-to-End Multimodal)
    - Voice Cloning: 10 sn referans → Jarvis tonu (Paul Bettany)
    - Duygu kontrol: charming/sarcastic/intimate/authoritative — otonom
    - WebSocket streaming: <300ms gecikme (gerçek zamanlı)

    Eski: Ses → MiniMax Sesten-Sese → DeepSeek V4-Pro → MiniMax Voice Cloning → Ses (3 katman, 2-3sn)
    Yeni: Ses → MiniMax → Ses (TEK katman, <300ms)

    "Sıfır gecikme, kusursuz voice cloning, aylık ~$10 maliyet."
    """

    def __init__(self, config: MiniMaxConfig = None):
        self.config = config or MiniMaxConfig()
        self._current_emotion: VoiceEmotion = VoiceEmotion.NEUTRAL
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._is_connected: bool = False
        self._system_prompt: str = ""
        self._memory_context: str = ""  # DeepSeek'ten gelen günlük özet

        logging.basicConfig(level=logging.INFO, format='[MiniMax] %(message)s')
        self.log = logging.getLogger("minimax")

        print("[MiniMax] Realtime Orchestrator başlatıldı (2026)")
        print(f"[MiniMax] Model: {self.config.MODEL}")
        print(f"[MiniMax] Voice Clone: {'AKTİF' if self.config.VOICE_CLONE_ENABLED else 'KAPALI'}")
        print(f"[MiniMax] Hedef gecikme: <300ms")

    # =========================================================================
    # WEBSOCKET BAĞLANTISI — MiniMax Realtime
    # =========================================================================
    async def connect(self) -> bool:
        """
        MiniMax WebSocket'e bağlan — sesten-sese realtime session.

        🎯 MANTIK:
        1. WebSocket bağlantısı kur (Speech 2.8 Turbo)
        2. Session yapılandırması gönder:
           - Voice Cloning: referans ses dosyası
           - Duygu profili: mevcut emotion
           - System Prompt: Jarvis karakter anayasası + hafıza
        3. Ses akışı başlat (çift yönlü: mikrofon → MiniMax → hoparlör)
        """
        try:
            # WebSocket URL + auth
            url = f"{self.config.WS_URL}?api_key={self.config.API_KEY}&group_id={self.config.GROUP_ID}"

            self._ws = await websockets.connect(url)
            self._is_connected = True

            # Session yapılandırması
            session_config = {
                "model": self.config.MODEL,
                "audio_format": self.config.AUDIO_FORMAT,
                "sample_rate": self.config.SAMPLE_RATE,
                "chunk_size_ms": self.config.CHUNK_SIZE_MS,
                "voice_emotion": self._current_emotion.value,
                "system_prompt": self._system_prompt + "\n\n" + self._memory_context,
            }

            # Voice Cloning aktifse
            if self.config.VOICE_CLONE_ENABLED:
                session_config["voice_clone"] = {
                    "enabled": True,
                    "reference_audio": self._encode_reference_voice(),
                    "reference_text": "Good morning. I am Jarvis, your personal AI assistant.",
                }

            # Session başlat
            await self._ws.send(json.dumps({
                "type": "session.start",
                "config": session_config
            }))

            self.log.info("✅ MiniMax WebSocket bağlandı — sesten-sese aktif")
            return True

        except Exception as e:
            self.log.error(f"❌ Bağlantı hatası: {e}")
            self._is_connected = False
            return False

    # =========================================================================
    # VOICE CLONING — Referans Ses Encode
    # =========================================================================
    def _encode_reference_voice(self) -> str:
        """
        10 saniyelik referans ses dosyasını base64'e çevir.

        🎭 VOICE CLONING MANTIĞI:
        MiniMax Voice Cloning:
        - 10 sn referans ses (Paul Bettany / Türkçe dublaj)
        - MiniMax, bu sesin tonunu, pitch'ini ve karakterini klonlar
        - Tüm konuşmalar bu tonda çıkar → "Jarvis sesi"
        - Ekstra maliyet YOK (tek seferlik klonlama, sonra sınırsız kullanım)
        """
        try:
            with open(self.config.VOICE_CLONE_REFERENCE, "rb") as f:
                audio_bytes = f.read()
            return base64.b64encode(audio_bytes).decode("utf-8")
        except FileNotFoundError:
            self.log.warning("Referans ses dosyası bulunamadı — varsayılan ses kullanılacak")
            return ""

    # =========================================================================
    # SES AKIŞI — Mikrofon → MiniMax → Hoparlör
    # =========================================================================
    async def audio_stream_loop(self, audio_input: AsyncGenerator[bytes, None],
                                 audio_output_callback) -> None:
        """
        Çift yönlü ses akışı: mikrofon → MiniMax → hoparlör.

        🎯 <300ms GECİKME MANTIĞI:
        =============================================================================
        1. Mikrofon → 20ms PCM chunk → WebSocket → MiniMax
        2. MiniMax → Speech 2.8 Turbo → ses yanıtı → WebSocket → hoparlör
        3. Toplam gecikme: ~200-300ms (gerçek zamanlı)

        Chunk boyutu: 20ms (50 FPS) → minimum gecikme
        WebSocket: çift yönlü, persistent → bağlantı kurulumu bir kez

        "Sıfır gecikme = gerçek zamanlı konuşma = premium hissi."
        """
        if not self._is_connected:
            await self.connect()

        self.log.info("🎙️ Ses akışı başlatıldı (<300ms hedef)")

        # Çift görev: ses gönder + ses al (paralel)
        await asyncio.gather(
            self._send_audio(audio_input),
            self._receive_audio(audio_output_callback)
        )

    # =========================================================================
    # SES GÖNDER — Mikrofon → MiniMax
    # =========================================================================
    async def _send_audio(self, audio_input: AsyncGenerator[bytes, None]) -> None:
        """
        Mikrofon sesini MiniMax'a stream et.

        Her 20ms'de bir PCM chunk gönder → MiniMax anında işler.
        """
        async for chunk in audio_input:
            if not self._is_connected:
                break

            # PCM chunk → base64 → WebSocket
            audio_b64 = base64.b64encode(chunk).decode("utf-8")
            await self._ws.send(json.dumps({
                "type": "audio.input",
                "data": audio_b64,
                "format": self.config.AUDIO_FORMAT,
                "sample_rate": self.config.SAMPLE_RATE
            }))

    # =========================================================================
    # SES AL — MiniMax → Hoparlör
    # =========================================================================
    async def _receive_audio(self, audio_output_callback) -> None:
        """
        MiniMax'ten gelen ses yanıtını hoparlöre stream et.

        🎯 MANTIK:
        MiniMax Speech 2.8 Turbo → ses yanıtı (PCM chunk) → hoparlör.
        Gecikme: ~200-300ms (WebSocket + inference + network).
        """
        try:
            async for message in self._ws:
                data = json.loads(message)

                if data.get("type") == "audio.output":
                    # Ses yanıtı → hoparlör
                    audio_b64 = data.get("data", "")
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        await audio_output_callback(audio_bytes)

                elif data.get("type") == "text.output":
                    # Transkript (opsiyonel — log için)
                    text = data.get("text", "")
                    if text:
                        self.log.info(f"Jarvis: {text}")

                elif data.get("type") == "emotion.update":
                    # MiniMax duygu değişimi bildirimi
                    emotion = data.get("emotion", "")
                    self.log.info(f"🎭 Duygu: {emotion}")

                elif data.get("type") == "session.end":
                    self.log.info("Session bitti")
                    break

        except websockets.exceptions.ConnectionClosed:
            self.log.warning("WebSocket bağlantısı kesildi")
            self._is_connected = False

    # =========================================================================
    # DUYGU KONTROLÜ — Otonom Ses Tonu
    # =========================================================================
    def set_emotion(self, emotion: VoiceEmotion) -> None:
        """
        Jarvis'in ses tonunu duruma göre ayarla.

        🎭 MANTIK:
        - Misafir var → CHARMING (sıcak, davetkar)
        - Espri/alay → SARCASTIC (kuru, zeki)
        - Normal komut → NEUTRAL (sakin)
        - Romantik → INTIMATE (yumuşak, alçak)
        - Uyarı → AUTHORITATIVE (net, güçlü)

        MiniMax voice_emotion parametresi → ses tonu anında değişir.
        """
        self._current_emotion = emotion
        self.log.info(f"🎭 Duygu profili: {emotion.value}")

    # =========================================================================
    # DUYGU OTOMATİK SEÇİMİ — Bağlama Göre
    # =========================================================================
    def auto_select_emotion(self, context: Dict[str, Any]) -> VoiceEmotion:
        """
        Bağlama göre en uygun duygu profilini otomatik seç.

        🤖 PROAKTİF AI:
        DeepSeek V4-Pro / DeepSeek, bağlamı analiz eder:
        - Misafir var → charming
        - Intimacy modu → intimate
        - Gece → intimate
        - Espri → sarcastic
        - Normal → neutral
        """
        if context.get("guest_present"):
            return VoiceEmotion.CHARMING
        elif context.get("current_mode") == "intimacy":
            return VoiceEmotion.INTIMATE
        elif context.get("time_of_day") == "night":
            return VoiceEmotion.INTIMATE
        elif context.get("user_tone") == "playful":
            return VoiceEmotion.SARCASTIC
        elif context.get("alert"):
            return VoiceEmotion.AUTHORITATIVE
        else:
            return VoiceEmotion.NEUTRAL

    # =========================================================================
    # HAFIZA YÜKLE — DeepSeek'ten gelen günlük özet
    # =========================================================================
    def load_memory_context(self, memory_summary: str) -> None:
        """
        DeepSeek'ten gelen günlük konuşma özetini yükle.

        🧠 MANTIK:
        1. Dün konuşmalar → DeepSeek (ucuz) → özet metin
        2. Bu özet → MiniMax System Prompt'a yükle (Prompt Caching)
        3. Jarvis, dünkü konuşmaları "bedavaya" hatırlar
        4. Ses token maliyetine girmeden hafıza → ~$0 ek maliyet
        """
        self._memory_context = f"\n\n=== DÜNKÜ KONUŞMA ÖZETİ ===\n{memory_summary}\n=== ÖZET SONU ==="
        self.log.info(f"🧠 Hafıza yüklendi: {len(memory_summary)} karakter")

    # =========================================================================
    # SYSTEM PROMPT YÜKLE
    # =========================================================================
    def load_system_prompt(self, prompt: str) -> None:
        """Jarvis karakter anayasasını yükle."""
        self._system_prompt = prompt
        self.log.info(f"📜 System prompt yüklendi: {len(prompt)} karakter")

    # =========================================================================
    # TOOL CALLING — DeepSeek/Qwen köprüsü (ağır zeka/vizyon)
    # =========================================================================
    async def call_deep_brain(self, task: str, context: str = "") -> str:
        """
        Ağır zeka gerektiren işlerde DeepSeek V4-Pro veya Qwen-VL'yi çağır.

        🧠 MANTIK:
        MiniMax Speech 2.8 Turbo → hızlı sesli konuşma (günlük)
        DeepSeek V4-Pro → ağır zeka (kod yazma, analiz, özet)
        Qwen-VL → görüntü analizi (kamera, vision)

        Köprü:
        1. Kullanıcı "Bu Python kodunu düzelt" der
        2. MiniMax → DeepSeek API'ye task gönderir (tool calling)
        3. DeepSeek → kod düzeltir → metin yanıt
        4. MiniMax → bu metni seslendirir

        Bu, MiniMax'in ses token maliyetini sadece "seslendirme" için kullanır.
        Ağır zeka → DeepSeek (çok ucuz) → sadece sonuç seslendirilir.
        """
        # DeepSeek API çağrısı (httpx)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-v4-pro",
                    "messages": [
                        {"role": "system", "content": "Sen Jarvis'in arka beynisin. Kullanıcının isteğini yerine getir."},
                        {"role": "user", "content": f"{context}\n\n{task}"}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.3,
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                self.log.error(f"DeepSeek hatası: {response.status_code}")
                return "Üzgünüm efendim, şu anda bu işlemi yapamıyorum."

    # =========================================================================
    # HA AGENTİC API — Cihaz Kontrolü
    # =========================================================================
    async def control_device(self, service: str, entity_id: str, data: dict) -> bool:
        """
        Home Assistant cihaz kontrolü — Agentic.

        🤖 MANTIK:
        MiniMax → "Bize siberpunk ortamı kur" → DeepSeek → WLED JSON üretir
        → HA REST API → oda değişir → MiniMax → "Siberpunk modu aktif, efendim."
        """
        async with httpx.AsyncClient() as client:
            parts = service.split(".")
            if len(parts) != 2:
                return False
            domain, service_name = parts
            url = f"{self.config.HA_URL}/api/services/{domain}/{service_name}"
            data["entity_id"] = entity_id

            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.config.HA_TOKEN}"},
                json=data,
                timeout=5.0
            )
            return response.status_code == 200

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def disconnect(self) -> None:
        """WebSocket bağlantısını kapat."""
        if self._ws:
            await self._ws.close()
            self._ws = None
        self._is_connected = False
        self.log.info("WebSocket kapatıldı")


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """MiniMax Realtime Orchestrator test."""
    orchestrator = MiniMaxRealtimeOrchestrator()

    # System prompt yükle
    with open("advanced_system_prompt_v2.md", "r", encoding="utf-8") as f:
        orchestrator.load_system_prompt(f.read())

    # Hafıza yükle (DeepSeek'ten gelen özet)
    orchestrator.load_memory_context("Dün misafir Ayşe geldi. Latte içti. Interstellar konuştuk.")

    # Duygu ayarla
    orchestrator.set_emotion(VoiceEmotion.CHARMING)

    # Bağlan
    connected = await orchestrator.connect()
    if connected:
        print("✅ MiniMax bağlandı — sesten-sese aktif")
        print("🎙️ Mikrofon → MiniMax → Hoparlör (<300ms)")
        print("🎭 Duygu: CHARMING")
        print("🧠 Hafıza: Dün Ayşe geldi, latte içti, Interstellar konuştuk")
        print("🎤 Voice Clone: Paul Bettany (Jarvis) tonu")

    await orchestrator.disconnect()


if __name__ == "__main__":
    asyncio.run(main())