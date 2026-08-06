"""
 =============================================================================
 vision_chef_assistant — Vision Frame Analyzer (Mutfak Gözü)
 =============================================================================
 Bu script, mutfak tezgahını tepeden gören IP kameradan (RTSP) görüntü alır,
 OpenAI DeepSeek V4-Pro-mini (Vision) API'sine gönderir ve Jarvis'in şef kişiliğiyle
 analiz etmesini sağlar.

 MİMARİ:
   1. RTSP stream → OpenCV ile kare al (On-Demand veya 1 FPS)
   2. Kareyi base64'e çevir
   3. OpenAI Qwen-VL Max API'ye gönder (async)
   4. DeepSeek V4-Pro'dan tarif/uyarı/eleştiri al
   5. Jarvis'e (TTS) gönder → hoparlörden şef yorumu

 🎯 ON-DEMAND ANALİZ MANTIĞI:
 =============================================================================
 Kamera SÜREKLİ analiz etmez. Bu, hem CPU/bant genişliği tasarrufu sağlar
 hem de gereksiz API çağrılarını engeller. Sadece:
   - Kullanıcı "Jarvis, bunlardan ne çıkar?" dediğinde (On-Demand)
   - Otomasyon tetiklediğinde (buton, NFC, sensör)
   - Güvenlik modunda (ocak gözetimsiz kaldıysa) düşük FPS ile

 Sürekli analiz = CPU yorgunluğu + API maliyeti + gereksiz trafik
 On-Demand analiz = Sadece ihtiyaç anında → verimli, ekonomik, hızlı

 GEREKLİ KÜTÜPHANELER:
   pip install opencv-python openai asyncio httpx

 =============================================================================
"""

import asyncio
import base64
import cv2
import time
from typing import Optional, Dict
from enum import Enum

# =============================================================================
# KÜTÜPHANE IMPORTLARI
# =============================================================================
try:
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError("openai kütüphanesi gerekli: pip install openai")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class VisionChefConfig:
    """Vision Chef Assistant konfigürasyonu."""

    # IP Kamera (RTSP)
    # TP-Link Tapo RTSP formatı: rtsp://kullanıcı:şifre@IP:554/stream1
    RTSP_URL: str = "rtsp://admin:password@192.168.1.107:554/stream1"

    # Qwen-VL API
    OPENAI_API_KEY: str = "YOUR_OPENAI_API_KEY"
    VISION_MODEL: str = "DeepSeek V4-Pro-mini"  # Hızlı ve ekonomik vision modeli
    MAX_TOKENS: int = 200  # Kısa cevaplar (şef yorumu max 2-3 cümle)

    # Analiz Modu
    ANALYSIS_FPS: float = 0.1  # On-Demand modda: 0.1 FPS (10 saniyede 1 kare)
    # Güvenlik modu (ocak gözetimsiz): 0.5 FPS (2 saniyede 1 kare)
    SAFETY_FPS: float = 0.5

    # MQTT (HA ile haberleşme)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_CHEF_ANALYSIS: str = "jarvis/chef/analysis"
    MQTT_TOPIC_CHEF_WARNING: str = "jarvis/chef/warning"
    MQTT_TOPIC_CHEF_REQUEST: str = "jarvis/chef/request"  # HA'dan analiz isteği


# =============================================================================
# ANALİZ MODLARI
# =============================================================================

class AnalysisMode(Enum):
    """Kamera analiz modları."""
    ON_DEMAND = "on_demand"      # Sadece istek geldiğinde (en verimli)
    RECIPE = "recipe"             # Tarif önerisi ("bunlardan ne çıkar?")
    SAFETY = "safety"             # Güvenlik (ocak gözetimsiz, duman, yanma)
    INTERACTIVE = "interactive"   # Etkileşimli (durum güncellemesi, komik yorum)


# =============================================================================
# VISION FRAME ANALYZER
# =============================================================================

class VisionFrameAnalyzer:
    """
    Mutfak kamerasından görüntü alır, OpenAI Vision ile analiz eder.

    Çalışma modları:
    1. ON_DEMAND: HA'dan "jarvis/chef/request" geldiğinde tek kare al ve analiz et
    2. SAFETY: Güvenlik modunda düşük FPS ile sürekli izle (ocak, duman, yanma)
    3. RECIPE: "Bunlardan ne çıkar?" → malzemeleri tanı → tarif öner
    4. INTERACTIVE: Durum güncellemesi → komik/akıllıca yorum
    """

    def __init__(self, config: VisionChefConfig):
        self.config = config
        self.openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

        # Şef kişiliği system prompt'u (chef_persona_system_prompt.yaml'den yüklenir)
        self.chef_system_prompt: str = ""

        # Kamera bağlantısı
        self._cap: Optional[cv2.VideoCapture] = None

        # Son analiz zamanı (rate limiting için)
        self._last_analysis_time: float = 0
        self._min_analysis_interval: float = 3.0  # En az 3 saniye ara

    # =========================================================================
    # KAMERA BAĞLANTISI
    # =========================================================================
    def _connect_camera(self) -> bool:
        """RTSP kamera bağlantısı aç."""
        if self._cap is not None and self._cap.isOpened():
            return True

        self._cap = cv2.VideoCapture(self.config.RTSP_URL)

        if not self._cap.isOpened():
            print(f"[VisionChef] HATA: Kamera açılamadı: {self.config.RTSP_URL}")
            return False

        print("[VisionChef] Kamera bağlantısı başarılı.")
        return True

    # =========================================================================
    # KARE YAKALAMA
    # =========================================================================
    def capture_frame(self) -> Optional[bytes]:
        """
        Kameradan tek bir kare yakala ve JPEG formatında byte olarak döndür.

        Returns:
            JPEG encoded frame bytes, veya None (hata durumunda)

        🎯 ON-DEMAND MANTIĞI:
        Bu fonksiyon sadece çağrıldığında kare alır. Sürekli döngü YOK.
        Bu, CPU ve bant genişliği tasarrufu sağlar.
        """
        if not self._connect_camera():
            return None

        # RTSP buffer'ı temizle (eski kareleri at)
        # RTSP'de buffer dolu olabilir → en son kareyi al
        for _ in range(5):
            self._cap.grab()

        ret, frame = self._cap.read()
        if not ret or frame is None:
            print("[VisionChef] HATA: Kare alınamadı.")
            return None

        # Kareyi JPEG'e çevir (base64 için)
        # Kalite: 85 (iyi kalite, düşük boyut)
        _, jpeg_buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

        return jpeg_buffer.tobytes()

    # =========================================================================
    # GÖRÜNTÜYÜ BASE64'E ÇEVİR
    # =========================================================================
    def _encode_frame(self, frame_bytes: bytes) -> str:
        """JPEG byte'ları base64 string'e çevir (OpenAI Vision için)."""
        return base64.b64encode(frame_bytes).decode('utf-8')

    # =========================================================================
    # OPENAI VISION ANALİZİ (ASYNC)
    # =========================================================================
    async def analyze_frame(
        self,
        mode: AnalysisMode = AnalysisMode.ON_DEMAND,
        user_message: str = ""
    ) -> Optional[str]:
        """
        Kameradan kare al, OpenAI Qwen-VL Max'a gönder, analiz et.

        Args:
            mode: Analiz modu (ON_DEMAND, RECIPE, SAFETY, INTERACTIVE)
            user_message: Kullanıcının isteği ("bunlardan ne çıkar?", vb.)

        Returns:
            Jarvis'in şef yorumu (metin), veya None (hata)

        🎯 ASYNC MANTIK:
        MiniMax API çağrısı asenkron — kamera karesi alınırken API beklerken
        diğer görevler çalışabilir. Bu, gecikmeyi minimize eder.
        """
        # Rate limiting kontrolü
        current_time = time.time()
        if current_time - self._last_analysis_time < self._min_analysis_interval:
            print("[VisionChef] Rate limit: Çok sık analiz isteği.")
            return None

        self._last_analysis_time = current_time

        # Kare yakala
        frame_bytes = self.capture_frame()
        if frame_bytes is None:
            return None

        # Base64'e çevir
        frame_b64 = self._encode_frame(frame_bytes)

        # Mode'a göre prompt hazırla
        prompt = self._build_prompt(mode, user_message)

        print(f"[VisionChef] Qwen-VL Max'a gönderiliyor (mod: {mode.value})...")

        # Qwen-VL API çağrısı (async)
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.VISION_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                messages=[
                    {
                        "role": "system",
                        "content": self.chef_system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame_b64}",
                                    "detail": "low"  # Düşük detay = hızlı, ekonomik
                                }
                            }
                        ]
                    }
                ]
            )

            analysis = response.choices[0].message.content
            print(f"[VisionChef] Analiz sonucu: {analysis}")
            return analysis

        except Exception as e:
            print(f"[VisionChef] HATA: Qwen-VL API hatası: {e}")
            return None

    # =========================================================================
    # MOD'A GÖRE PROMPT HAZIRLAMA
    # =========================================================================
    def _build_prompt(self, mode: AnalysisMode, user_message: str) -> str:
        """
        Analiz moduna göre OpenAI Vision'a gönderilecek prompt'u hazırla.

        Her mod farklı bir soru sorar:
        - RECIPE: "Bu malzemelerle ne yapılabilir?"
        - SAFETY: "Ocakta bir şey yanıyor mu? Duman var mı?"
        - INTERACTIVE: "Tezgahın durumunu komik bir şekilde yorumla."
        - ON_DEMAND: Kullanıcının sorusunu kullan
        """
        if mode == AnalysisMode.RECIPE:
            return (
                "Bu mutfak tezgahının fotoğrafını analiz et. Tezgahtaki malzemeleri "
                "tanı ve bu malzemelerle yapılabilecek pratik, şık bir yemek öner. "
                "Cevabın KISA olsun (max 3 cümle). Tarif adı ve 1-2 ipucu ver."
            )

        elif mode == AnalysisMode.SAFETY:
            return (
                "Bu mutfak tezgahının fotoğrafını analiz et. AŞAĞIDAKİLERİ KONTROL ET:\n"
                "1. Ocakta duman tütüyor mu?\n"
                "2. Bir şey yanmaya başlamış mı?\n"
                "3. Ocak gözetimsiz mi (etrafta kimse yok gibi mi)?\n"
                "Eğer TEHLİKE varsa, 'UYARI:' ile başla ve kısa bir uyarı ver.\n"
                "Eğer tehlike yoksa, sadece 'Her şey yolunda.' de."
            )

        elif mode == AnalysisMode.INTERACTIVE:
            return (
                "Bu mutfak tezgahının fotoğrafını analiz et. Tezgahın mevcut "
                "durumunu KOMİK ve ZEKİCE yorumla. Gordon Ramsay ile Tony Stark "
                "karışımı, hafif kibirli ama yardımcı bir şef gibi. Max 2 cümle."
            )

        else:  # ON_DEMAND
            return (
                f"Bu mutfak tezgahının fotoğrafını analiz et. "
                f"Kullanıcının sorusu: {user_message}\n"
                f"Cevabın KISA ve ZARİF olsun (max 3 cümle)."
            )

    # =========================================================================
    # GÜVENLİK MODU — Sürekli İzleme (Düşük FPS)
    # =========================================================================
    async def safety_monitor_loop(self) -> None:
        """
        Güvenlik modu: Ocağı düşük FPS ile sürekli izle.

        Bu döngü sadece güvenlik modunda çalışır:
        - Ocağın açık olup olmadığını kontrol et
        - Duman/yanma tespiti yap
        - Gözetimsiz ocak uyarısı ver

        🎯 DÜŞÜK FPS MANTIĞI:
        0.5 FPS (2 saniyede 1 kare) — CPU ve API maliyeti düşük.
        Güvenlik için 2 saniye gecikme kabul edilebilir (yangın anında değil,
        "yanmaya başladı" aşamasında uyarı).
        """
        print("[VisionChef] Güvenlik modu başlatıldı (0.5 FPS).")

        frame_interval = 1.0 / self.config.SAFETY_FPS  # 2 saniye

        while True:
            # Güvenlik analizi
            analysis = await self.analyze_frame(
                mode=AnalysisMode.SAFETY
            )

            if analysis and "UYARI" in analysis.upper():
                # Tehlike tespit edildi → MQTT'ye uyarı gönder
                print(f"[VisionChef] ⚠️ TEHLİKE TESPİTİ: {analysis}")
                # mqtt.publish("jarvis/chef/warning", analysis)

            await asyncio.sleep(frame_interval)

    # =========================================================================
    # ON-DEMAND ANALİZ — HA'dan İstek Geldiğinde
    # =========================================================================
    async def on_demand_analysis(
        self,
        mode: AnalysisMode = AnalysisMode.ON_DEMAND,
        user_message: str = ""
    ) -> Optional[str]:
        """
        HA'dan analiz isteği geldiğinde tek kare al ve analiz et.

        Bu, en verimli moddur — sadece ihtiyaç anında kamera çalışır.

        Args:
            mode: Analiz modu
            user_message: Kullanıcının sorusu

        Returns:
            Jarvis'in şef yorumu
        """
        return await self.analyze_frame(mode, user_message)

    # =========================================================================
    # KAPATMA
    # =========================================================================
    def cleanup(self) -> None:
        """Kamera bağlantısını kapat."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        print("[VisionChef] Kamera bağlantısı kapatıldı.")


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

async def main():
    """Vision Chef Assistant ana giriş."""

    config = VisionChefConfig()
    analyzer = VisionFrameAnalyzer(config)

    # Şef system prompt'unu yükle (chef_persona_system_prompt.yaml'den)
    # Gerçek implementasyonda YAML okunur
    analyzer.chef_system_prompt = (
        "Sen Jarvis'in mutfak modusun. Gordon Ramsay ile Tony Stark karışımı, "
        "hafif kibirli ama zekice dalga geçen ama bir o kadar da yardımcı bir şefsin. "
        "Cevapların KISA (max 3 cümle), zekice ve hafif alaycı olmalı."
    )

    # On-Demand mod: Tek analiz yap
    print("[VisionChef] On-Demand analiz başlatılıyor...")
    result = await analyzer.on_demand_analysis(
        mode=AnalysisMode.RECIPE,
        user_message="Bunlardan ne çıkar?"
    )

    if result:
        print(f"\n🧑‍🍳 Jarvis Şef: {result}")

    analyzer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())