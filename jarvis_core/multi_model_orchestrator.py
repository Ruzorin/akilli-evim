"""
 =============================================================================
 jarvis_core 3.0 — Multi-Model Orchestrator (Mixture of Experts)
 =============================================================================
 2026 Sürümü — Agentic AGI Orchestrator

 Bu modül, Jarvis'in "Mixture of Experts" (Uzmanlık Dağılımı) mimarisini
 uygular. Tek bir LLM yerine, görev tipine göre en uygun AI modeline
 yönlendirme yapar:

   MiniMax Speech 2.8 Turbo  → Cihaz kontrolü, hızlı eylemler, espri/wingman, vision
   DeepSeek V4-Pro     → Derin felsefi/psikolojik sohbet, yaratıcı rol yapma
   DeepSeek V4-Pro    → Dil Koçu (Modül 15), dil pratik, kelime öğretimi
   DeepSeek V4-Pro        → Biyometrik duygu analizi, devasa bağlam penceresi

 🧠 "MIXTURE OF EXPERTS" MANTIĞI:
 =============================================================================
 Her AI modelinin farklı uzmanlık alanı vardır:
   - MiniMax Speech 2.8 Turbo: Hızlı, gerçek zamanlı, çok modlu (vision + ses + metin)
   - DeepSeek V4-Pro: Derin düşünme, empati, felsefe, yaratıcılık
   - DeepSeek V4-Pro: Dil eğitimi, pedagoji, sabırlı koçluk
   - DeepSeek V4-Pro: Devasa bağlam (2M token), çoklu sensör verisi analizi

 Orchestrator, kullanıcının niyetini (intent) analiz eder ve en uygun
 modele yönlendirir. Bu, "tek boyutlu asistan" → "çok boyutlu zihin"
 dönüşümüdür.

 🤖 AGENTIC FRAMEWORK:
 =============================================================================
 2026 standartları: LangGraph (LangChain 2026) tabanlı asenkron agent graph.
 Statik intent script'leri YOK — agent'lar dinamik karar verir.

 GEREKLİ KÜTÜPHANELER (2026):
   pip install langgraph langchain-openai langchain-anthropic
   pip install langchain-google-genai asyncio httpx

 =============================================================================
"""

import asyncio
from typing import Optional, Dict, Any, Literal
from enum import Enum
from dataclasses import dataclass

# =============================================================================
# 2026 KÜTÜPHANE IMPORTLARI
# =============================================================================
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
except ImportError:
    raise ImportError(
        "langgraph gerekli (2026): pip install langgraph\n"
        "LangChain 2026 Agentic Framework"
    )

try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    raise ImportError(
        "langchain provider'ları gerekli:\n"
        "pip install langchain-openai langchain-anthropic langchain-google-genai"
    )


# =============================================================================
# MODEL TANIMLARI (2026)
# =============================================================================

class ExpertModel(Enum):
    """Mixture of Experts — her modelin uzmanlık alanı."""
    GPT56_REALTIME = "MiniMax Speech 2.8 Turbo"       # Hızlı, çok modlu, cihaz kontrolü
    CLAUDE5_OPUS = "claude-5-opus-2026"       # Derin düşünme, felsefe, empati
    CLAUDE5_FABLE = "claude-5-fable-2026"     # Dil eğitimi, pedagoji
    GEMINI35 = "gemini-3.5-pro-2026"          # Devasa bağlam, sensör analizi


@dataclass
class ModelConfig:
    """Her model için konfigürasyon."""
    name: str
    model_id: str
    api_key_env: str
    temperature: float
    max_tokens: int
    specialty: str


# Model konfigürasyonları
MODEL_CONFIGS = {
    ExpertModel.GPT56_REALTIME: ModelConfig(
        name="MiniMax Speech 2.8 Turbo Realtime",
        model_id="MiniMax Speech 2.8 Turbo",
        api_key_env="OPENAI_API_KEY",
        temperature=0.7,
        max_tokens=150,
        specialty="Cihaz kontrolü, hızlı eylem, vision, espri/wingman"
    ),
    ExpertModel.CLAUDE5_OPUS: ModelConfig(
        name="DeepSeek V4-Pro",
        model_id="claude-5-opus-2026",
        api_key_env="ANTHROPIC_API_KEY",
        temperature=0.8,
        max_tokens=500,
        specialty="Derin felsefe, psikolojik sohbet, yaratıcı rol yapma"
    ),
    ExpertModel.CLAUDE5_FABLE: ModelConfig(
        name="DeepSeek V4-Pro",
        model_id="claude-5-fable-2026",
        api_key_env="ANTHROPIC_API_KEY",
        temperature=0.6,
        max_tokens=300,
        specialty="Dil eğitimi, pedagoji, sabırlı koçluk, IELTS/TEF"
    ),
    ExpertModel.GEMINI35: ModelConfig(
        name="DeepSeek V4-Pro Pro",
        model_id="gemini-3.5-pro-2026",
        api_key_env="GOOGLE_API_KEY",
        temperature=0.5,
        max_tokens=200,
        specialty="Biyometrik analiz, devasa bağlam, sensör verisi"
    ),
}


# =============================================================================
# INTENT SINIFLANDIRICI — Hangi model hangi görev için?
# =============================================================================

class IntentClassifier:
    """
    Kullanıcının niyetini (intent) analiz eder ve en uygun AI modeline yönlendirir.

    🧠 MANTIK AĞACI:
    1. Cihaz kontrolü / hızlı eylem / espri → MiniMax Speech 2.8 Turbo
    2. Dil eğitimi / dil pratik → DeepSeek V4-Pro
    3. Derin sohbet / felsefe / rol yapma → DeepSeek V4-Pro
    4. Duygu analizi / sensör verisi → DeepSeek V4-Pro
    """

    @staticmethod
    def classify(
        user_input: str,
        context: Dict[str, Any],
        active_persona: str = "default"
    ) -> ExpertModel:
        """
        Kullanıcı girdisini analiz edip en uygun modeli seç.

        Args:
            user_input: Kullanıcının metin/ses girdisi
            context: Bağlam (aktif modül, sensör verisi, yüz tanıma)
            active_persona: Aktif Jarvis kişiliği (default, language_tutor, chef)

        Returns:
            En uygun ExpertModel
        """
        input_lower = user_input.lower()

        # -------------------------------------------------------------------------
        # 1. DİL EĞİTMENİ MODU → DeepSeek V4-Pro
        # -------------------------------------------------------------------------
        if active_persona == "language_tutor":
            return ExpertModel.CLAUDE5_FABLE

        # Dil çalışma komutları
        language_keywords = [
            "fransızca", "ingilizce", "çalış", "kelime", "gramer",
            "ielts", "tef", "tcf", "sınav", "pratik", "telaffuz",
            "french", "english", "study", "vocabulary", "grammar"
        ]
        if any(kw in input_lower for kw in language_keywords):
            return ExpertModel.CLAUDE5_FABLE

        # -------------------------------------------------------------------------
        # 2. DERİN SOHBET / FELSEFE / ROL YAPMA → DeepSeek V4-Pro
        # -------------------------------------------------------------------------
        deep_keywords = [
            "neden", "nasıl", "felsefe", "psikoloji", "hisset",
            "düşün", "yaşam", "anlam", "rol yap", "hikaye",
            "why", "how", "philosophy", "psychology", "feel",
            "think", "life", "meaning", "roleplay", "story"
        ]
        if any(kw in input_lower for kw in deep_keywords):
            return ExpertModel.CLAUDE5_OPUS

        # -------------------------------------------------------------------------
        # 3. DUYGU ANALİZİ / SENSÖR VERİSİ → DeepSeek V4-Pro
        # -------------------------------------------------------------------------
        emotion_keywords = [
            "stres", "üzgün", "yorgun", "mutlu", "duygu",
            "kalp", "nefes", "biyometrik", "radar",
            "stress", "sad", "tired", "happy", "emotion",
            "heart", "breath", "biometric"
        ]
        if any(kw in input_lower for kw in emotion_keywords):
            return ExpertModel.GEMINI35

        # Eğer sensör verisi bağlamda varsa → DeepSeek V4-Pro
        if context.get("biometric_data") or context.get("sensor_fusion"):
            return ExpertModel.GEMINI35

        # -------------------------------------------------------------------------
        # 4. VARSAYILAN → MiniMax Speech 2.8 Turbo (hızlı, çok modlu)
        # -------------------------------------------------------------------------
        # Cihaz kontrolü, hızlı eylemler, espri, wingman, vision
        return ExpertModel.GPT56_REALTIME


# =============================================================================
# MULTI-MODEL ORCHESTRATOR (LangGraph Agent Graph)
# =============================================================================

class MultiModelOrchestrator:
    """
    2026 Agentic Orchestrator — LangGraph tabanlı çok-modelli agent graph.

    Bu orchestrator:
    1. Kullanıcı girdisini alır
    2. IntentClassifier ile en uygun modeli seçer
    3. Seçilen modeli çağırır (async)
    4. Modelin cevabını alır
    5. Eğer model HA aksiyonu gerektiriyorsa → AgenticHomeAssistantAPI'ye yönlendir

    🤖 AGENTIC MANTIK:
    Statik intent script'leri YOK. Agent'lar dinamik karar verir.
    MiniMax Speech 2.8 Turbo, "Bize cyberpunk ortamı yap" gibi soyut komutları aldıysa:
    1. WLED için neon mor/yeşil JSON'u KENDİSİ ÜRETİR
    2. Spotify'dan Synthwave müziği KENDİSİ BULUR
    3. HA REST API'ye KENDİSİ İSTEK GÖNDERİR
    4. Sonucu kullanıcıya bildirir

    Bu, "önceden yazılmış komutlara" ihtiyaç duymadan HA'ı manipüle etmektir.
    """

    def __init__(self):
        # Her model için LangChain client oluştur
        self.models: Dict[ExpertModel, Any] = {
            ExpertModel.GPT56_REALTIME: ChatOpenAI(
                model=MODEL_CONFIGS[ExpertModel.GPT56_REALTIME].model_id,
                temperature=MODEL_CONFIGS[ExpertModel.GPT56_REALTIME].temperature,
                max_tokens=MODEL_CONFIGS[ExpertModel.GPT56_REALTIME].max_tokens,
            ),
            ExpertModel.CLAUDE5_OPUS: ChatAnthropic(
                model=MODEL_CONFIGS[ExpertModel.CLAUDE5_OPUS].model_id,
                temperature=MODEL_CONFIGS[ExpertModel.CLAUDE5_OPUS].temperature,
                max_tokens=MODEL_CONFIGS[ExpertModel.CLAUDE5_OPUS].max_tokens,
            ),
            ExpertModel.CLAUDE5_FABLE: ChatAnthropic(
                model=MODEL_CONFIGS[ExpertModel.CLAUDE5_FABLE].model_id,
                temperature=MODEL_CONFIGS[ExpertModel.CLAUDE5_FABLE].temperature,
                max_tokens=MODEL_CONFIGS[ExpertModel.CLAUDE5_FABLE].max_tokens,
            ),
            ExpertModel.GEMINI35: ChatGoogleGenerativeAI(
                model=MODEL_CONFIGS[ExpertModel.GEMINI35].model_id,
                temperature=MODEL_CONFIGS[ExpertModel.GEMINI35].temperature,
                max_tokens=MODEL_CONFIGS[ExpertModel.GEMINI35].max_tokens,
            ),
        }

        # System prompt'lar (her model/persona için ayrı)
        self.system_prompts: Dict[str, str] = {}

        # Aktif persona
        self.active_persona: str = "default"

        # Agentic HA API (kendi kendini kodlayan oda)
        from agentic_home_assistant_api import AgenticHomeAssistantAPI
        self.ha_agent = AgenticHomeAssistantAPI()

        print("[Orchestrator] Multi-Model Orchestrator başlatıldı (2026)")
        print(f"[Orchestrator] Modeller: {[m.value for m in ExpertModel]}")

    # =========================================================================
    # ANA ORCHESTRATION FONKSİYONU
    # =========================================================================
    async def process(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Kullanıcı girdisini işle ve en uygun modelden cevap al.

        Bu, LangGraph agent graph'ının ana giriş noktasıdır.

        Args:
            user_input: Kullanıcının metin/ses girdisi
            context: Bağlam (sensör, yüz, modül durumu, duygu)

        Returns:
            Jarvis'in cevabı (metin)

        🤖 AGENTIC AKIŞ:
        1. IntentClassifier → en uygun modeli seç
        2. Modeli çağır (system prompt + user input + context)
        3. Eğer model "HA_ACTION" etiketi dönerse → HA agent'a yönlendir
        4. HA agent, modelin ürettiği JSON'u HA REST API'ye gönderir
        5. Sonucu kullanıcıya döndür
        """
        context = context or {}

        # Adım 1: En uygun modeli seç
        selected_model = IntentClassifier.classify(
            user_input, context, self.active_persona
        )

        print(f"[Orchestrator] Seçilen model: {selected_model.value}")
        print(f"[Orchestrator] Uzmanlık: {MODEL_CONFIGS[selected_model].specialty}")

        # Adım 2: System prompt'u al
        system_prompt = self.system_prompts.get(
            self.active_persona,
            self.system_prompts.get("default", "")
        )

        # Adım 3: Modeli çağır (async)
        model = self.models[selected_model]

        # Bağlamı prompt'a ekle
        context_str = self._format_context(context)

        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + context_str},
            {"role": "user", "content": user_input},
        ]

        # Model cevabı (async)
        response = await model.ainvoke(messages)
        ai_response = response.content

        # Adım 4: Eğer cevap HA aksiyonu içeriyorsa → Agentic HA API
        if "HA_ACTION:" in ai_response or "DEVICE_CONTROL:" in ai_response:
            print("[Orchestrator] Agentic HA aksiyonu tespit edildi → HA Agent")
            ai_response = await self.ha_agent.execute_agentic_action(
                ai_response, context
            )

        return ai_response

    # =========================================================================
    # BAĞLAM FORMATLAMA
    # =========================================================================
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Sensör, yüz tanıma ve duygu verilerini model için formatla.

        DeepSeek V4-Pro'in devasa bağlam penceresi (2M token) sayesinde tüm
        sensör verisini tek seferde gönderebiliriz.
        """
        parts = []

        if context.get("face"):
            face = context["face"]
            parts.append(
                f"ODADAKİ KİŞİ: {face.get('name', 'Bilinmiyor')}. "
                f"Son ziyaret: {face.get('last_visit', '?')}. "
                f"Sohbet özeti: {face.get('conversation_summary', '')}."
            )

        if context.get("biometric"):
            bio = context["biometric"]
            parts.append(
                f"BİYOMETRİK: Kalp atışı: {bio.get('heart_rate', '?')} BPM. "
                f"Nefes: {bio.get('breath_rate', '?')}/dk. "
                f"Stres seviyesi: {bio.get('stress_level', '?')}/10. "
                f"Duygu durumu: {bio.get('emotion', 'belirsiz')}."
            )

        if context.get("active_modules"):
            parts.append(f"AKTİF MODÜLLER: {', '.join(context['active_modules'])}")

        if context.get("activity_level"):
            parts.append(f"YATAK AKTİVİTESİ: {context['activity_level']}/100")

        return "\n".join(parts) if parts else "Bağlam yok."

    # =========================================================================
    # PERSONA DEĞİŞTİRME
    # =========================================================================
    def set_persona(self, persona: str) -> None:
        """Jarvis'in kişiliğini değiştir (default, language_tutor, chef)."""
        self.active_persona = persona
        print(f"[Orchestrator] Persona: {persona}")

    # =========================================================================
    # SYSTEM PROMPT YÜKLEME
    # =========================================================================
    def load_system_prompt(self, persona: str, prompt: str) -> None:
        """Bir persona için system prompt yükle."""
        self.system_prompts[persona] = prompt
        print(f"[Orchestrator] System prompt yüklendi: {persona}")


# =============================================================================
# LANGGRAPH AGENT GRAPH (2026 Agentic Framework)
# =============================================================================

def build_agent_graph(orchestrator: MultiModelOrchestrator):
    """
    LangGraph tabanlı agent graph oluştur.

    Bu graph, Jarvis'in "düşün → karar ver → eyleme geç → gözlemle"
    döngüsünü yönetir. Statik intent'ler YOK — her şey dinamik.

    Graph düğümleri:
    1. classify_intent → Kullanıcı niyetini analiz et
    2. select_model → En uygun AI modelini seç
    3. invoke_model → Modeli çağır
    4. check_action → HA aksiyonu var mı kontrol et
    5. execute_action → HA REST API'ye gönder (agentic)
    6. generate_response → Kullanıcıya cevap üret
    """
    from typing import TypedDict

    class AgentState(TypedDict):
        user_input: str
        context: Dict[str, Any]
        selected_model: str
        model_response: str
        ha_action: Optional[str]
        final_response: str

    # Graph oluştur
    workflow = StateGraph(AgentState)

    # -------------------------------------------------------------------------
    # Düğüm 1: Intent sınıflandır
    # -------------------------------------------------------------------------
    async def classify_intent(state: AgentState) -> AgentState:
        model = IntentClassifier.classify(
            state["user_input"],
            state.get("context", {}),
            orchestrator.active_persona
        )
        state["selected_model"] = model.value
        return state

    # -------------------------------------------------------------------------
    # Düğüm 2: Modeli çağır
    # -------------------------------------------------------------------------
    async def invoke_model(state: AgentState) -> AgentState:
        response = await orchestrator.process(
            state["user_input"],
            state.get("context", {})
        )
        state["model_response"] = response
        return state

    # -------------------------------------------------------------------------
    # Düğüm 3: HA aksiyonu kontrol et
    # -------------------------------------------------------------------------
    async def check_action(state: AgentState) -> str:
        """HA aksiyonu varsa 'execute', yoksa 'respond'."""
        if "HA_ACTION:" in state.get("model_response", ""):
            return "execute"
        return "respond"

    # -------------------------------------------------------------------------
    # Düğüm 4: HA aksiyonu çalıştır (Agentic)
    # -------------------------------------------------------------------------
    async def execute_action(state: AgentState) -> AgentState:
        result = await orchestrator.ha_agent.execute_agentic_action(
            state["model_response"],
            state.get("context", {})
        )
        state["ha_action"] = result
        state["final_response"] = result
        return state

    # -------------------------------------------------------------------------
    # Düğüm 5: Cevap üret (HA aksiyonu yoksa)
    # -------------------------------------------------------------------------
    async def generate_response(state: AgentState) -> AgentState:
        state["final_response"] = state["model_response"]
        return state

    # Düğümleri graph'a ekle
    workflow.add_node("classify", classify_intent)
    workflow.add_node("invoke", invoke_model)
    workflow.add_node("execute", execute_action)
    workflow.add_node("respond", generate_response)

    # Bağlantıları tanımla
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "invoke")
    workflow.add_conditional_edges(
        "invoke",
        check_action,
        {
            "execute": "execute",
            "respond": "respond",
        }
    )
    workflow.add_edge("execute", END)
    workflow.add_edge("respond", END)

    return workflow.compile()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Jarvis Core 3.0 — Multi-Model Orchestrator ana giriş."""

    orchestrator = MultiModelOrchestrator()

    # System prompt'ları yükle
    with open("agi_system_prompt_2026.md", "r", encoding="utf-8") as f:
        default_prompt = f.read()
    orchestrator.load_system_prompt("default", default_prompt)

    with open("../immersive_language_tutor/tutor_persona_prompt.yaml", "r") as f:
        tutor_prompt = f.read()
    orchestrator.load_system_prompt("language_tutor", tutor_prompt)

    # Agent graph oluştur
    graph = build_agent_graph(orchestrator)

    # Test: "Bize cyberpunk bir ortam yap"
    print("\n=== TEST: Cyberpunk ortamı ===")
    result = await orchestrator.process(
        "Bize cyberpunk bir ortam yap",
        context={"active_modules": []}
    )
    print(f"Jarvis: {result}")

    # Test: Dil eğitmeni
    print("\n=== TEST: Fransızca çalışma ===")
    orchestrator.set_persona("language_tutor")
    result = await orchestrator.process(
        "Je veux pratiquer mon français",
        context={"active_modules": ["language_tutor"]}
    )
    print(f"Jarvis: {result}")


if __name__ == "__main__":
    asyncio.run(main())