"""
 =============================================================================
 jarvis_core — Hybrid Brain & Memory Manager (Ucuz Zeka ve Hafıza)
 =============================================================================
 2026 Sürümü — DeepSeek V4-Pro + Qwen-VL + Günlük Özet + Prompt Caching

 Bu modül, Jarvis'in "ucuz beynini" ve "hafızasını" yönetir:
 1. Konuşma oturumu bittiğinde → DeepSeek (çok ucuz) → günlük özet
 2. Ertesi gün → özet → MiniMax System Prompt'a yükle (Prompt Caching)
 3. Ağır zeka/vizyon gerektiren işlerde → DeepSeek V4-Pro / Qwen-VL köprüsü

 🧠 "HYBRID BRAIN" MANTIĞI — MALİYET OPTİMİZASYONU:
 =============================================================================
 MiniMax Speech 2.8 Turbo → hızlı sesli konuşma (günlük, ~$10/ay)
 DeepSeek V4-Pro → ağır zeka (kod, analiz, özet — çok ucuz, ~$1-2/ay)
 Qwen-VL → görüntü analizi (kamera, vision — ucuz)

 Böl ve yönet:
 - Hızlı konuşma → MiniMax (ses token = pahalı → sadece konuşma için)
 - Ağır düşünme → DeepSeek (metin token = çok ucuz → özet, kod, analiz)
 - Görüntü → Qwen-VL (vision token = ucuz → kamera analizi)

 "Ses token'larını sadece konuşmaya harca, düşünmeyi ucuz beyne devret."

 GEREKLİ KÜTÜPHANELER:
   pip install httpx asyncio

 =============================================================================
"""

import asyncio
import json
import time
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta

try:
    import httpx
except ImportError:
    raise ImportError("httpx gerekli: pip install httpx")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class HybridBrainConfig:
    """Hybrid Brain & Memory Manager konfigürasyonu."""

    # DeepSeek API (ucuz zeka — özet, kod, analiz)
    DEEPSEEK_API_KEY: str = "YOUR_DEEPSEEK_API_KEY"
    DEEPSEEK_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-v4-pro"  # En gelişmiş DeepSeek modeli

    # Qwen-VL API (görüntü analizi — vision)
    # OpenAI-uyumlu DashScope endpoint (modern format)
    QWEN_API_KEY: str = "YOUR_QWEN_API_KEY"
    QWEN_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    QWEN_MODEL: str = "qwen-vl-max-latest"

    # Hafıza saklama
    MEMORY_DIR: str = "jarvis_memory/daily_summaries"  # Lokal JSON dosyaları
    MAX_MEMORY_DAYS: int = 30  # Son 30 günü hatırla

    # Özet parametreleri
    SUMMARY_MAX_TOKENS: int = 500  # Özet maksimum 500 token (kısa, ucuz)
    SUMMARY_TEMPERATURE: float = 0.3  # Düşük sıcaklık → tutarlı özet


# =============================================================================
# HYBRID BRAIN & MEMORY MANAGER
# =============================================================================

class HybridBrainMemoryManager:
    """
    Jarvis'in ucuz beyni ve hafıza yöneticisi.

    🧠 "HYBRID BRAIN" MANTIĞI:
    =============================================================================
    MiniMax (pahalı ses) + DeepSeek (ucuz metin) = optimum maliyet

    1. GÜNLÜK ÖZET (Session bittiğinde):
       - O günkü konuşma transkripti → DeepSeek → özet metin
       - Özet: "Misafir Ayşe geldi. Latte içti. Interstellar konuştuk."
       - Maliyet: ~$0.001 (DeepSeek metin token çok ucuz)

    2. HAFIZA YÜKLEME (Ertesi gün):
       - Özet → MiniMax System Prompt'a yükle (Prompt Caching)
       - Jarvis, dünkü konuşmayı "bedavaya" hatırlar
       - Ses token maliyetine girmeden hafıza

    3. AĞIR ZEKA KÖPRÜSÜ (Tool Calling):
       - "Bu Python kodunu düzelt" → DeepSeek V4-Pro
       - "Kameradan mutfağa bak" → Qwen-VL (görüntü analizi)
       - MiniMax → DeepSeek/Qwen → sonuç → MiniMax seslendirir

    "Ses token'larını sadece konuşmaya harca, düşünmeyi ucuz beyne devret."
    """

    def __init__(self, config: HybridBrainConfig = None):
        self.config = config or HybridBrainConfig()
        self.client = httpx.AsyncClient(timeout=30.0)

        logging.basicConfig(level=logging.INFO, format='[HybridBrain] %(message)s')
        self.log = logging.getLogger("hybrid_brain")

        print("[HybridBrain] Memory Manager başlatıldı (2026)")
        print(f"[HybridBrain] DeepSeek: {self.config.DEEPSEEK_MODEL}")
        print(f"[HybridBrain] Qwen-VL: {self.config.QWEN_MODEL}")

    # =========================================================================
    # GÜNLÜK ÖZET — Konuşma → DeepSeek → Özet
    # =========================================================================
    async def summarize_daily_conversation(self, transcript: str, date: str = None) -> str:
        """
        O günkü konuşma transkriptini DeepSeek ile özetle.

        🧠 MANTIK:
        Konuşma oturumu bittiğinde:
        1. Tüm konuşma transkripti → DeepSeek V4-Pro
        2. DeepSeek → kısa özet (max 500 token)
        3. Özet → lokal JSON dosyasına kaydet
        4. Ertesi gün → bu özet MiniMax'e yüklenir

        Maliyet: ~$0.001 (DeepSeek metin token çok ucuz)
        "Ses token maliyetine girmeden, geçmişi bedavaya hatırlar."
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        self.log.info(f"📝 Günlük özet hazırlanıyor: {date} ({len(transcript)} karakter)")

        # DeepSeek'e özet taskı gönder
        response = await self.client.post(
            self.config.DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.config.DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Sen Jarvis'in hafıza yöneticisisin. Verilen konuşma transkriptini "
                            "kısa bir özete çevir. Özet şu bilgileri içermeli:\n"
                            "1. Konuşulan konular (kısa)\n"
                            "2. Önemli kararlar/istekler\n"
                            "3. Misafir bilgileri (varsa)\n"
                            "4. Duygusal ton (neşeli, stresli, romantik, vb.)\n"
                            "Özet maksimum 3-4 cümle olsun. Türkçe yaz."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Tarih: {date}\n\nKonuşma transkripti:\n{transcript}"
                    }
                ],
                "max_tokens": self.config.SUMMARY_MAX_TOKENS,
                "temperature": self.config.SUMMARY_TEMPERATURE,
            }
        )

        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"]

            # Lokal dosyaya kaydet
            await self._save_memory(date, summary)

            self.log.info(f"✅ Özet kaydedildi: {date} → {len(summary)} karakter")
            return summary
        else:
            self.log.error(f"❌ DeepSeek özet hatası: {response.status_code}")
            return ""

    # =========================================================================
    # HAFIZA KAYDET — Lokal JSON
    # =========================================================================
    async def _save_memory(self, date: str, summary: str) -> None:
        """Günlük özeti lokal JSON dosyasına kaydet."""
        import os
        os.makedirs(self.config.MEMORY_DIR, exist_ok=True)

        filepath = f"{self.config.MEMORY_DIR}/{date}.json"
        memory_data = {
            "date": date,
            "summary": summary,
            "timestamp": time.time()
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

    # =========================================================================
    # HAFIZA YÜKLE — Son N Günün Özetini Al
    # =========================================================================
    async def load_recent_memory(self, days: int = 7) -> str:
        """
        Son N günün özetlerini birleştir → MiniMax System Prompt'a yükle.

        🧠 MANTIK:
        1. Son 7 günün özet dosyalarını oku
        2. Birleştir → tek bağlam metni
        3. MiniMax → load_memory_context() → System Prompt'a yükle
        4. Jarvis, son 7 günü "bedavaya" hatırlar

        "Ses token maliyetine girmeden, geçmişi bedavaya hatırlar."
        """
        import os
        memories = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            filepath = f"{self.config.MEMORY_DIR}/{date}.json"

            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    memories.append(f"[{date}] {data['summary']}")

        if not memories:
            return "Önceki konuşma kaydı yok."

        combined = "\n".join(memories)
        self.log.info(f"🧠 {len(memories)} gün hafızası yüklendi")
        return combined

    # =========================================================================
    # DEEPSEEK KÖPRÜSÜ — Ağır Zeka (Kod, Analiz, Planlama)
    # =========================================================================
    async def call_deep_brain(self, task: str, context: str = "") -> str:
        """
        Ağır zeka gerektiren işlerde DeepSeek V4-Pro'yu çağır.

        🧠 MANTIK:
        MiniMax → "Bu Python kodunu düzelt" → DeepSeek V4-Pro
        DeepSeek → kod düzeltir → metin yanıt
        MiniMax → bu metni seslendirir

        Bu, MiniMax'in ses token maliyetini sadece "seslendirme" için kullanır.
        Ağır düşünme → DeepSeek (çok ucuz) → sadece sonuç seslendirilir.

        Maliyet: DeepSeek ~$0.01/istek (MiniMax ses ~$0.10/dk ile karşılaştır)
        """
        self.log.info(f"🧠 DeepSeek çağrılıyor: {task[:50]}...")

        response = await self.client.post(
            self.config.DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.config.DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen Jarvis'in arka beynisin. Kullanıcının isteğini yerine getir. Kısa ve net yanıt ver."
                    },
                    {
                        "role": "user",
                        "content": f"{context}\n\n{task}" if context else task
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
            }
        )

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            self.log.info(f"✅ DeepSeek yanıtı: {len(answer)} karakter")
            return answer
        else:
            self.log.error(f"❌ DeepSeek hatası: {response.status_code}")
            return "Üzgünüm efendim, şu anda bu işlemi yapamıyorum."

    # =========================================================================
    # QWEN-VL KÖPRÜSÜ — Görüntü Analizi (Vision)
    # =========================================================================
    async def call_vision_brain(self, image_base64: str, prompt: str) -> str:
        """
        Görüntü analizi gerektiren işlerde Qwen-VL'yi çağır.

        🧠 MANTIK:
        MiniMax → "Kameradan mutfağa bak" → Qwen-VL (görüntü analizi)
        Qwen-VL → görüntüyü analiz eder → metin yanıt
        MiniMax → bu metni seslendirir

        Kullanım:
        - "Kameradan mutfağa bak, ne pişiriyor?" → Qwen-VL
        - "Bu yemeği kalori takibime ekle" → Qwen-VL → kalori analizi
        - "Kombin nasıl?" → Qwen-VL → stil analizi

        Maliyet: Qwen-VL ~$0.02/görüntü (MiniMax vision ~$0.50 ile karşılaştır)
        """
        self.log.info(f"👁️ Qwen-VL çağrılıyor: {prompt[:50]}...")

        response = await self.client.post(
            self.config.QWEN_URL,
            headers={
                "Authorization": f"Bearer {self.config.QWEN_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.config.QWEN_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            self.log.info(f"✅ Qwen-VL yanıtı: {len(answer)} karakter")
            return answer
        else:
            self.log.error(f"❌ Qwen-VL hatası: {response.status_code}")
            return "Görüntüyü analiz edemedim efendim."

    # =========================================================================
    # TOOL CALLING ROUTER — Hangi Beyin?
    # =========================================================================
    async def route_task(self, task: str, image: str = None) -> str:
        """
        Görev tipine göre doğru "beyni" seç (Tool Calling Router).

        🧠 MANTIK:
        - Sesli konuşma → MiniMax (orchestrator tarafından yönetilir)
        - Kod/analiz/özet → DeepSeek V4-Pro
        - Görüntü/vision → Qwen-VL
        - Cihaz kontrolü → HA REST API

        Bu router, "hangi beyin hangi iş için" kararını verir.
        "Ses token'larını sadece konuşmaya harca, düşünmeyi ucuz beyne devret."
        """
        # Görüntü var → Qwen-VL
        if image:
            return await self.call_vision_brain(image, task)

        # Kod/analiz/planlama → DeepSeek
        code_keywords = ["kod", "python", "düzenle", "analiz", "özet", "plan", "yaz", "hesapla"]
        if any(kw in task.lower() for kw in code_keywords):
            return await self.call_deep_brain(task)

        # Varsayılan → DeepSeek (genel zeka)
        return await self.call_deep_brain(task)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    async def close(self):
        await self.client.close()


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Hybrid Brain & Memory Manager test."""
    manager = HybridBrainMemoryManager()

    # Test: Günlük özet
    transcript = """
    Kullanıcı: Jarvis, ışıkları kıs
    Jarvis: Elbette efendim.
    Kullanıcı: Misafirimiz Ayşe geliyor, kahve hazırla
    Jarvis: İhmal etmedim efendim. Kahve hazırlanıyor.
    Kullanıcı: Ayşe'ye Interstellar'dan bahsettim, çok beğendi
    Jarvis: Güzel bir film. Nolan'ın başyapıtlarından.
    """

    summary = await manager.summarize_daily_conversation(transcript)
    print(f"\n📝 Özet: {summary}")

    # Test: Hafıza yükle
    memory = await manager.load_recent_memory(7)
    print(f"\n🧠 Hafıza: {memory[:200]}...")

    # Test: DeepSeek köprüsü
    result = await manager.call_deep_brain("Python'da bir fonksiyon yaz: iki sayıyı topla")
    print(f"\n🧠 DeepSeek: {result[:100]}...")

    await manager.close()


if __name__ == "__main__":
    asyncio.run(main())