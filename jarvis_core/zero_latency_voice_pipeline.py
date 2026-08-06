"""
 =============================================================================
 jarvis_core — Zero-Latency Voice Pipeline (Eski Sürüm — Arşiv)
 =============================================================================
 ⚠️ DİKKAT: Bu dosya eski mimariye (OpenAI Realtime API) dayanmaktadır.
 Artık kullanılmıyor — yerine `minimax_realtime_orchestrator.py` kullanın.

 ESKİ MİMARİ (Bu dosya):
    Ses → OpenAI Realtime API (WebRTC) → Metin → ElevenLabs TTS → Ses
    (3 katman, ~500ms — ama OpenAI faturası ~$50-100/ay)

 YENİ MİMARİ (minimax_realtime_orchestrator.py):
    Ses → MiniMax Speech 2.8 Turbo → Ses (TEK katman, <300ms)
    + Voice Cloning (10 sn referans → Jarvis tonu)
    + Duygu kontrol (charming/sarcastic/intimate/authoritative)
    + ~$10/ay (OpenAI'den 5-10x ucuz)

 Bu dosya referans için tutulmaktadır. Aktif sistemde kullanmayın.
 Aktif sistem: `minimax_realtime_orchestrator.py` + `hybrid_brain_and_memory_manager.py`
 =============================================================================
"""

# Bu dosya artık aktif değildir. Yeni mimari için:
# - minimax_realtime_orchestrator.py (sesten-sese, voice cloning, duygu kontrol)
# - hybrid_brain_and_memory_manager.py (DeepSeek ağır zeka + günlük hafıza)
#
# Eski OpenAI Realtime API kodu aşağıda referans olarak korunmuştur.
# =============================================================================

import asyncio
import json
import base64
from typing import Optional, AsyncGenerator

# ESKİ IMPORTLAR (artık gerekmez — MiniMax kullanın)
# from openai import AsyncOpenAI
# from elevenlabs import ElevenLabs, AsyncElevenLabs


class JarvisConfig:
    """Eski konfigürasyon — artık kullanılmıyor."""

    # Eski: OpenAI Realtime API
    OPENAI_API_KEY: str = "DEPRECATED"
    REALTIME_MODEL: str = "DEPRECATED"

    # Eski: ElevenLabs TTS
    ELEVENLABS_API_KEY: str = "DEPRECATED"
    ELEVENLABS_VOICE_ID: str = "DEPRECATED"

    # YENİ: MiniMax Speech 2.8 Turbo (minimax_realtime_orchestrator.py'de)
    # YENİ: DeepSeek V4-Pro (hybrid_brain_and_memory_manager.py'de)


# Bu dosya deprecated'tir. Aktif kod için:
# python3 minimax_realtime_orchestrator.py
# python3 hybrid_brain_and_memory_manager.py