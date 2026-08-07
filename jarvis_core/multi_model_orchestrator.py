"""
 =============================================================================
 jarvis_core — Multi-Model Orchestrator (Eski Sürüm — Arşiv)
 =============================================================================
 ⚠️ DİKKAT: Bu dosya eski mimariye (LangChain/LangGraph + OpenAI/Anthropic/Google) dayanmaktadır.
 Artık kullanılmıyor — yerine `minimax_realtime_orchestrator.py` kullanın.

 ESKİ MİMARİ (Bu dosya):
    LangGraph 2026 + LangChain provider'ları (OpenAI, Anthropic, Google)
    Mixture of Experts: GPT-5.6 + Claude 5 + Gemini 3.6
    Maliyet: ~$25-35/ay (çoklu API abonelik)

 YENİ MİMARİ (minimax_realtime_orchestrator.py + hybrid_brain_and_memory_manager.py):
    MiniMax Speech 2.8 Turbo (sesten-sese, <300ms, voice cloning, duygu kontrol)
    + DeepSeek V4-Pro (ağır zeka, kod, özet — ~$1-2/ay)
    + Qwen-VL Max (görüntü analizi — ~$2/ay)
    Maliyet: ~$12-15/ay (3-5x ucuz)

 Bu dosya referans için tutulmaktadır. Aktif sistemde kullanmayın.
 Aktif sistem: `minimax_realtime_orchestrator.py` + `hybrid_brain_and_memory_manager.py`
 =============================================================================
"""

# Bu dosya artık aktif değildir. Yeni mimari için:
# - minimax_realtime_orchestrator.py (sesten-sese, voice cloning, duygu kontrol)
# - hybrid_brain_and_memory_manager.py (DeepSeek ağır zeka + günlük hafıza + Qwen-VL vision)
#
# Eski LangChain/LangGraph kodu aşağıda referans olarak korunmuştur.
# =============================================================================

# ESKİ IMPORTLAR (artık gerekmez)
# from langgraph.graph import StateGraph, END
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI


class ExpertModel:
    """Eski model enum — artık kullanılmıyor."""
    MINIMAX_REALTIME = "minimax-speech-2.8-turbo"
    DEEPSEEK = "deepseek-v4-pro"
    QWEN_VL = "qwen-vl-max-latest"


# Bu dosya deprecated'tir. Aktif kod için:
# python3 minimax_realtime_orchestrator.py
# python3 hybrid_brain_and_memory_manager.py