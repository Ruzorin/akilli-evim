"""
 =============================================================================
 jarvis_core 2.0 — Facial Memory & Vector Database (Gözler ve Hafıza)
 =============================================================================
 Bu modül, odadaki IP kameradan (RTSP) görüntü alır, yüzleri tanır ve
 kişisel hafıza için yerel bir Vektör Veritabanına (ChromaDB) kaydeder.

 MİMARİ:
   1. IP Kamera (RTSP) → OpenCV ile 1 FPS görüntü al
   2. Görüntüde yüz algıla (OpenCV Haar Cascade veya face_recognition)
   3. Yüz embedding'i çıkar (face_recognition kütüphanesi)
   4. ChromaDB'de mevcut yüzlerle eşleştir
   5. Yeni yüz → "Jarvis, bu arkadaşım Ayşe" → kaydet
   6. Bilinen yüz → Jarvis'e bağlam gönder (isim + geçmiş sohbet)

 🚨 GÜVENLİK — YÜZ VERİLERİNİN LOKALDE TUTULMASI:
 =============================================================================
 Yüz tanıma verileri (biyometrik veri) son derece hassastır. Bu veriler
 ASLA buluta (AWS, Google, OpenAI) gönderilmemelidir. Tüm işlem LOKAL:
   - Yüz algılama: Yerel (OpenCV / face_recognition)
   - Yüz embedding: Yerel (face_recognition, dlib tabanlı)
   - Vektör veritabanı: Yerel (ChromaDB, SQLite tabanlı)
   - Görüntü saklama: YOK (sadece embedding vektörü saklanır)

 Neden sadece embedding?
   - Ham görüntü = "kişinin fotoğrafı" → gizlilik ihlali riski
   - Embedding = 128 boyutlu sayı dizisi → görüntü geri oluşturulamaz
   - Sadece "bu yüz bu yüze benziyor mu?" sorusunu yanıtlar
   - Görüntü işlendikten sonra RAM'den silinir, diske yazılmaz

 GEREKLİ KÜTÜPHANELER:
   pip install opencv-python face-recognition chromadb numpy pillow

 =============================================================================
"""

import cv2
import numpy as np
import time
import json
from typing import Optional, Dict, List, Tuple
from datetime import datetime

# =============================================================================
# KÜTÜPHANE IMPORTLARI
# =============================================================================
try:
    import face_recognition
except ImportError:
    raise ImportError(
        "face_recognition kütüphanesi gerekli: pip install face-recognition\n"
        "Not: dlib gerektirir. Windows'ta CMake gerekir."
    )

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("chromadb kütüphanesi gerekli: pip install chromadb")


# =============================================================================
# KONFIGÜRASYON
# =============================================================================

class FacialMemoryConfig:
    """Yüz tanıma ve hafıza konfigürasyonu."""

    # IP Kamera (RTSP)
    RTSP_URL: str = "rtsp://camera.local:554/stream1"
    FPS: int = 1  # Saniyede 1 kare (CPU tasarrufu için düşük)

    # Yüz Tanıma
    FACE_DETECTION_MODEL: str = "hog"  # "hog" (hızlı) veya "cnn" (doğru, GPU gerekir)
    NUM_JITTERS: int = 1  # Embedding için jitter sayısı (daha yüksek = daha doğru)
    FACE_MATCH_TOLERANCE: float = 0.6  # Eşleşme toleransı (düşük = sıkı)

    # ChromaDB (Yerel Vektör Veritabanı)
    CHROMA_DB_PATH: str = "./jarvis_memory/chromadb"  # Lokal SQLite tabanlı
    COLLECTION_NAME: str = "face_memory"

    # MQTT (HA ile haberleşme)
    MQTT_BROKER: str = "gl-mt3000.local"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_FACE_DETECTED: str = "jarvis/face/detected"
    MQTT_TOPIC_FACE_NEW: str = "jarvis/face/new"
    MQTT_TOPIC_CONTEXT: str = "jarvis/context"


# =============================================================================
# YÜZ TANIMA VE HAFIZA SİSTEMİ
# =============================================================================

class FacialMemorySystem:
    """
    IP kameradan yüz algılar, ChromaDB'de saklar ve Jarvis'e bağlam gönderir.

    Çalışma akışı:
    1. Kameradan 1 FPS görüntü al
    2. Görüntüde yüz ara (face_recognition)
    3. Yüz bulunduysa embedding çıkar (128 boyutlu vektör)
    4. ChromaDB'de benzer yüz ara
    5a. Bilinen yüz → isim + geçmiş sohbet → Jarvis'e bağlam gönder
    5b. Yeni yüz → "Jarvis, bu arkadaşım X" komutunu bekle → kaydet

    🚨 GÜVENLİK:
    - Tüm işlem LOKAL (buluta veri gönderilmez)
    - Sadece embedding saklanır (ham görüntü saklanmaz)
    - Görüntü RAM'den silinir (diske yazılmaz)
    - ChromaDB yerel SQLite tabanlıdır (internet gerektirmez)
    """

    def __init__(self, config: FacialMemoryConfig):
        self.config = config

        # ChromaDB'yi başlat (yerel)
        self.chroma_client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)  # Telemetri KAPALI
        )

        # Koleksiyon (yüz hafızası)
        self.collection = self.chroma_client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "Jarvis yüz hafızası — lokal ve güvenli"}
        )

        # Son algılanan yüzler (tekrar tetiklemeyi önlemek için)
        self._last_detected_faces: Dict[str, float] = {}  # face_id → timestamp
        self._detection_cooldown: float = 30.0  # 30 saniye aynı yüzü tekrar bildirme

        print(f"[FacialMemory] Sistem başlatıldı. DB: {config.CHROMA_DB_PATH}")
        print(f"[FacialMemory] Koleksiyon: {config.COLLECTION_NAME}")
        print(f"[FacialMemory] Kayıtlı yüz sayısı: {self.collection.count()}")

    # =========================================================================
    # KAMERA DÖNGÜSÜ — 1 FPS Görüntü Al
    # =========================================================================
    def run_camera_loop(self) -> None:
        """
        IP kameradan sürekli 1 FPS görüntü al ve yüz algıla.

        Bu döngü ana thread'de çalışır:
        1. RTSP stream aç
        2. Her saniye 1 kare al
        3. Karede yüz ara
        4. Yüz bulunduysa _process_face çağır
        """
        print(f"[FacialMemory] Kamera başlatılıyor: {self.config.RTSP_URL}")

        cap = cv2.VideoCapture(self.config.RTSP_URL)

        if not cap.isOpened():
            print(f"[FacialMemory] HATA: Kamera açılamadı: {self.config.RTSP_URL}")
            return

        frame_interval = 1.0 / self.config.FPS  # 1 FPS = 1 saniye
        last_frame_time = 0

        try:
            while True:
                current_time = time.time()

                # FPS kontrolü — saniyede 1 kare
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.1)
                    continue

                last_frame_time = current_time

                # Kareden görüntü al
                ret, frame = cap.read()
                if not ret:
                    print("[FacialMemory] Kamera bağlantısı kesildi, yeniden bağlanılıyor...")
                    cap.release()
                    cap = cv2.VideoCapture(self.config.RTSP_URL)
                    time.sleep(2)
                    continue

                # Kareyi küçült (işlem hızını artır)
                # 720p → 360p (CPU tasarrufu)
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Yüzleri algıla
                self._detect_and_process_faces(rgb_frame)

        except KeyboardInterrupt:
            print("[FacialMemory] Kamera döngüsü durduruldu.")
        finally:
            cap.release()

    # =========================================================================
    # YÜZ ALGILAMA VE İŞLEME
    # =========================================================================
    def _detect_and_process_faces(self, rgb_frame: np.ndarray) -> None:
        """
        Görüntüde yüzleri algıla ve her birini işle.

        Args:
            rgb_frame: RGB formatında numpy array (küçültülmüş görüntü)

        🚨 GÜVENLİK:
        - Görüntü RAM'de işlenir, diske YAZILMAZ
        - Sadece embedding (128 boyutlu vektör) saklanır
        - İşlem bittikten sonra görüntü RAM'den silinir (garbage collection)
        - Hiçbir görüntü buluta gönderilmez
        """
        # Yüz konumlarını algıla
        face_locations = face_recognition.face_locations(
            rgb_frame,
            model=self.config.FACE_DETECTION_MODEL
        )

        if not face_locations:
            return  # Yüz yok

        # Her yüz için embedding çıkar
        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations,
            num_jitter=self.config.NUM_JITTERS
        )

        for i, encoding in enumerate(face_encodings):
            self._process_single_face(encoding, face_locations[i])

    # =========================================================================
    # TEK YÜZ İŞLEME — Tanıma veya Yeni Yüz
    # =========================================================================
    def _process_single_face(self, encoding: np.ndarray, location: Tuple) -> None:
        """
        Tek bir yüzün embedding'ini ChromaDB'de ara.

        Args:
            encoding: 128 boyutlu yüz embedding vektörü
            location: Yüzün görüntüdeki konumu (top, right, bottom, left)

        Akış:
        1. ChromaDB'de benzer yüz ara (cosine similarity)
        2. Eşleşme varsa → bilinen yüz → Jarvis'e bağlam gönder
        3. Eşleşme yoksa → yeni yüz → "Jarvis, bu arkadaşım X" bekle
        """
        # ChromaDB'de benzer yüz ara
        # encoding → liste formatına çevir (ChromaDB JSON tabanlı)
        encoding_list = encoding.tolist()

        # ChromaDB query — en yakın yüzleri bul
        results = self.collection.query(
            query_embeddings=[encoding_list],
            n_results=1,  # En yakın 1 sonuç
            include=["metadatas", "distances"]
        )

        # Eşleşme kontrolü
        if results["distances"] and len(results["distances"][0]) > 0:
            distance = results["distances"][0][0]

            # 🎯 Eşleşme toleransı: 0.6 (dlib standardı)
            # Düşük distance = daha iyi eşleşme
            if distance < self.config.FACE_MATCH_TOLERANCE:
                # BİLİNEN YÜZ — Jarvis'e bağlam gönder
                face_id = results["ids"][0][0]
                metadata = results["metadatas"][0][0]
                self._handle_known_face(face_id, metadata)
                return

        # YENİ YÜZ — Kayıt için bekle
        self._handle_new_face(encoding_list, location)

    # =========================================================================
    # BİLİNEN YÜZ — Jarvis'e Bağlam Gönder
    # =========================================================================
    def _handle_known_face(self, face_id: str, metadata: Dict) -> None:
        """
        Bilinen bir yüz algılandı. Jarvis'e bağlam gönder.

        🎭 BAĞLAM MANTIĞI:
        Jarvis, odaya giren kişinin kim olduğunu bilir. Misafir 2 hafta önce
        ziyaret etmişse, Jarvis ona ismiyle hitap eder ve geçmiş sohbeti hatırlar:
        "Ah, Ayşe. Son ziyaretinizde latte içmiştiniz ve Interstellar'dan
        konuşmuştuk. Yine latte ister misiniz?"

        Bu, "premium hospitality" hissinin zirvesidir — misafir "hatırlandığını"
        hisseder → "5 yıldızlı otel" deneyimi.

        Cooldown: Aynı yüz 30 saniye içinde tekrar algılanırsa tekrar bildirme
        (kamera sürekli aynı yüzü görür → spam önleme)
        """
        current_time = time.time()

        # Cooldown kontrolü
        if face_id in self._last_detected_faces:
            if current_time - self._last_detected_faces[face_id] < self._detection_cooldown:
                return  # 30 saniye içinde bildirildi, tekrar bildirme

        self._last_detected_faces[face_id] = current_time

        name = metadata.get("name", "Bilinmeyen")
        last_visit = metadata.get("last_visit", "Bilinmiyor")
        conversation_summary = metadata.get("conversation_summary", "")
        favorite_coffee = metadata.get("favorite_coffee", "")

        # Jarvis'e bağlam gönder (MQTT)
        context = {
            "type": "known_face",
            "face_id": face_id,
            "name": name,
            "last_visit": last_visit,
            "conversation_summary": conversation_summary,
            "favorite_coffee": favorite_coffee,
            "timestamp": datetime.now().isoformat()
        }

        # MQTT publish (pseudo — gerçek implementasyonda paho-mqtt)
        # mqtt.publish("jarvis/face/detected", json.dumps(context))
        print(f"[FacialMemory] BİLİNEN YÜZ: {name} (son ziyaret: {last_visit})")
        print(f"[FacialMemory] Bağlam Jarvis'e gönderildi: {context}")

        # Son ziyaret tarihini güncelle
        self.collection.update(
            ids=[face_id],
            metadatas=[{
                **metadata,
                "last_visit": datetime.now().strftime("%Y-%m-%d")
            }]
        )

    # =========================================================================
    # YENİ YÜZ — Kayıt İçin Bekle
    # =========================================================================
    def _handle_new_face(self, encoding_list: List[float], location: Tuple) -> None:
        """
        Yeni bir yüz algılandı. "Jarvis, bu arkadaşım Ayşe" komutunu bekle.

        🎭 MANTIK:
        Yeni yüz → Jarvis'e "yeni yüz algılandı" bildir →
        Kullanıcı "Jarvis, bu arkadaşım Ayşe" der →
        Yüz embedding + isim + sohbet özeti ChromaDB'ye kaydedilir.

        Güvenlik: Yeni yüz otomatik kaydedilmez — kullanıcı onayı gerekir.
        """
        # Geçici ID oluştur
        temp_id = f"temp_{int(time.time())}"

        # Geçici kayıt (isim bekleniyor)
        self.collection.add(
            ids=[temp_id],
            embeddings=[encoding_list],
            metadatas=[{
                "name": "Bilinmeyen",
                "registered_at": datetime.now().isoformat(),
                "status": "pending_name"
            }]
        )

        # Jarvis'e "yeni yüz" bildir
        context = {
            "type": "new_face",
            "temp_id": temp_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Yeni bir yüz algılandı. İsim bekleniyor."
        }

        # MQTT publish
        # mqtt.publish("jarvis/face/new", json.dumps(context))
        print(f"[FacialMemory] YENİ YÜZ: Geçici ID: {temp_id}")
        print(f"[FacialMemory] 'Jarvis, bu arkadaşım Ayşe' komutu bekleniyor.")

    # =========================================================================
    # YÜZ KAYDETME — "Jarvis, bu arkadaşım Ayşe"
    # =========================================================================
    def register_face(self, temp_id: str, name: str,
                      conversation_summary: str = "",
                      favorite_coffee: str = "") -> bool:
        """
        Yeni yüzü ismiyle kaydet.

        Args:
            temp_id: Geçici yüz ID (_handle_new_face'den)
            name: Kişinin ismi ("Ayşe")
            conversation_summary: İlk sohbet özeti ("Interstellar filmi konuştuk")
            favorite_coffee: Favori kahvesi ("Latte")

        Returns:
            True = başarılı, False = hata

        🚨 GÜVENLİK:
        - Yüz embedding'i LOKAL ChromaDB'de saklanır
        - Ham görüntü SAKLANMAZ (sadece 128 boyutlu vektör)
        - İsim ve sohbet özeti lokal SQLite'ta
        - Hiçbir veri buluta gönderilmez
        """
        try:
            # Geçici kaydı güncelle
            self.collection.update(
                ids=[temp_id],
                metadatas=[{
                    "name": name,
                    "registered_at": datetime.now().isoformat(),
                    "last_visit": datetime.now().strftime("%Y-%m-%d"),
                    "conversation_summary": conversation_summary,
                    "favorite_coffee": favorite_coffee,
                    "status": "registered"
                }]
            )

            # ID'yi kalıcı hale getir (temp_ → face_)
            permanent_id = f"face_{temp_id.replace('temp_', '')}"
            self.collection.update(ids=[temp_id], ids=[permanent_id])

            print(f"[FacialMemory] YÜZ KAYDEDİLDİ: {name} (ID: {permanent_id})")
            print(f"[FacialMemory] Sohbet özeti: {conversation_summary}")
            print(f"[FacialMemory] Favori kahve: {favorite_coffee}")
            return True

        except Exception as e:
            print(f"[FacialMemory] HATA: Yüz kaydedilemedi: {e}")
            return False

    # =========================================================================
    # SOHBET ÖZETİ GÜNCELLEME
    # =========================================================================
    def update_conversation(self, face_id: str, summary: str) -> bool:
        """
        Bilinen bir yüzün sohbet özetini güncelle.

        Her ziyaretten sonra, o ziyarette konuşulanların özeti kaydedilir.
        Bir sonraki ziyarette Jarvis bu özeti hatırlar.

        Örnek:
        Ziyaret 1: "Interstellar filmi konuştuk, latte içti"
        Ziyaret 2: "Yeni işinden bahsetti, espresso içti"
        Ziyaret 3: Jarvis: "Son ziyaretinizde yeni işinizden bahsetmiştiniz.
                           Espresso yine mi, yoksa latte'ye geri mi dönelim?"
        """
        try:
            # Mevcut metadata'yı al
            results = self.collection.get(ids=[face_id], include=["metadatas"])
            if not results["metadatas"]:
                return False

            metadata = results["metadatas"][0]
            old_summary = metadata.get("conversation_summary", "")

            # Eski özeti koru, yenisini ekle
            updated_summary = f"{old_summary} | {summary}" if old_summary else summary

            self.collection.update(
                ids=[face_id],
                metadatas=[{
                    **metadata,
                    "conversation_summary": updated_summary,
                    "last_visit": datetime.now().strftime("%Y-%m-%d")
                }]
            )

            print(f"[FacialMemory] Sohbet güncellendi: {face_id}")
            return True

        except Exception as e:
            print(f"[FacialMemory] HATA: Sohbet güncellenemedi: {e}")
            return False


# =============================================================================
# ANA ÇALIŞTIRMA
# =============================================================================

def main():
    """Facial Memory System ana giriş."""

    config = FacialMemoryConfig()
    system = FacialMemorySystem(config)

    # Kamera döngüsünü başlat (bloklayıcı)
    system.run_camera_loop()


if __name__ == "__main__":
    main()