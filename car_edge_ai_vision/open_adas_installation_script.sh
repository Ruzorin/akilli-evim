#!/bin/bash
# =============================================================================
# car_edge_ai_vision — OpenADAS Otomatik Kurulum Betiği
# =============================================================================
# Bu betik, Nvidia Jetson Nano üzerinde OpenADAS projesini otomatik
# klonlar, bağımlılıkları kurar, YOLO ağırlıklarını indirir ve projeyi derler.
#
# 🚀 TENSORRT HIZLANDIRMA MANTIĞI:
# =============================================================================
# TensorRT, Nvidia'nın çıkarım (inference) hızlandırma kütüphanesidir.
# YOLO modelini FP32 → FP16 (yarım hassasiyet) quantize eder →
# Jetson Nano'nun 128 CUDA core'unda milisaniyelik gecikmeyle çalışır.
#
# - FP32 YOLO: ~200ms/frame (5 FPS) → çok yavaş (sürüş için yetersiz)
# - TensorRT FP16: ~30ms/frame (30 FPS) → gerçek zamanlı (sürüş için ideal)
# - TensorRT INT8: ~15ms/frame (60 FPS) → ultra hız (kalibrasyon gerekir)
#
# Bu betik TensorRT FP16 optimizasyonu yapar → 30 FPS → gerçek zamanlı ADAS.
# =============================================================================

set -e  # Herhangi bir hatada dur

echo "🚀 OpenADAS Otomatik Kurulum Başlatılıyor..."
echo "================================================"

# -----------------------------------------------------------------------------
# 1. Sistem Güncelleme ve Temel Bağımlılıklar
# -----------------------------------------------------------------------------
echo "📦 [1/6] Sistem güncelleniyor..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "📦 [2/6] Bağımlılıklar kuruluyor..."
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-dev \
    libgtk2.0-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libcanberra-gtk-module \
    qt5-default \
    libqt5gui5 \
    libqt5core5 \
    libqt5dbus5 \
    libqt5network5 \
    libqt5widgets5 \
    qttools5-dev-tools \
    libeigen3-dev \
    libglew-dev \
    libglfw3-dev \
    libgl1-mesa-glx \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# -----------------------------------------------------------------------------
# 2. Python Bağımlılıkları
# -----------------------------------------------------------------------------
echo "🐍 [3/6] Python bağımlılıkları kuruluyor..."
pip3 install --upgrade pip
pip3 install numpy scipy matplotlib
pip3 install paho-mqtt  # MQTT → HA köprüsü için
pip3 install PyYAML    # Config dosyaları için

# -----------------------------------------------------------------------------
# 3. OpenADAS Projesini Klonla
# -----------------------------------------------------------------------------
echo "📂 [4/6] OpenADAS klonlanıyor..."
cd ~

# OpenADAS ana repo (vietanhdev/open-adas veya güncel fork)
if [ -d "open-adas" ]; then
    echo "open-adas zaten mevcut, güncelleniyor..."
    cd open-adas
    git pull
    cd ..
else
    git clone https://github.com/vietanhdev/open-adas.git
fi

cd open-adas

# -----------------------------------------------------------------------------
# 4. YOLO Ağırlıklarını İndir
# -----------------------------------------------------------------------------
echo "🧠 [5/6] YOLO ağırlıkları indiriliyor..."
mkdir -p models/weights

# YOLOv4-Tiny (hızlı — Jetson Nano için optimize)
if [ ! -f "models/weights/yolov4-tiny.weights" ]; then
    echo "YOLOv4-Tiny indiriliyor..."
    wget -O models/weights/yolov4-tiny.weights \
        https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
fi

# YOLOv4-Tiny config
if [ ! -f "models/weights/yolov4-tiny.cfg" ]; then
    wget -O models/weights/yolov4-tiny.cfg \
        https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
fi

# COCO sınıf isimleri (80 sınıf: araç, insan, tabelalar, vb.)
if [ ! -f "models/weights/coco.names" ]; then
    wget -O models/weights/coco.names \
        https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names
fi

# YOLOv5 (PyTorch — opsiyonel, daha iyi doğruluk)
if [ ! -d "models/yolov5" ]; then
    echo "YOLOv5 indiriliyor (opsiyonel)..."
    git clone https://github.com/ultralytics/yolov5.git models/yolov5
    cd models/yolov5
    pip3 install -r requirements.txt
    # YOLOv5s (küçük model — Jetson için optimize)
    python3 -c "import torch; torch.hub.load('ultralytics/yolov5', 'yolov5s')"
    cd ../..
fi

# -----------------------------------------------------------------------------
# 5. TensorRT Optimizasyonu (FP16 — Milisaniyelik Gecikme)
# -----------------------------------------------------------------------------
echo "⚡ [6/6] TensorRT FP16 optimizasyonu..."

# 🚀 TensorRT MANTIĞI:
# YOLO modelini TensorRT Engine'e dönüştür → FP16 yarım hassasiyet
# Jetson Nano GPU'da 30 FPS → gerçek zamanlı ADAS
# Bu adım olmadan YOLO ~5 FPS → sürüş için yetersiz

# darknet → TensorRT engine dönüştürme (opsiyonel — TensorRT eklentisi gerekir)
# veya YOLOv5 → TensorRT (PyTorch → ONNX → TensorRT)

if [ -d "models/yolov5" ]; then
    echo "YOLOv5 → ONNX → TensorRT FP16 dönüştürme..."
    cd models/yolov5
    # YOLOv5s → ONNX
    python3 export.py --weights yolov5s.pt --img 640 --include onnx
    # ONNX → TensorRT (trtexec ile)
    /usr/src/tensorrt/bin/trtexec \
        --onnx=yolov5s.onnx \
        --saveEngine=yolov5s_trt_fp16.engine \
        --fp16  # FP16 yarım hassasiyet → 2x hız, minimal doğruluk kaybı
    echo "✅ TensorRT FP16 engine oluşturuldu: yolov5s_trt_fp16.engine"
    cd ../..
fi

# -----------------------------------------------------------------------------
# 6. OpenADAS Derle
# -----------------------------------------------------------------------------
echo "🔨 OpenADAS derleniyor..."
mkdir -p build
cd build

# CMake ile derleme yapılandırması
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=17 \
    -DUSE_CUDA=ON \
    -DUSE_TENSORRT=ON \
    -DUSE_OPENCV=ON

# Derle (Jetson Nano'da ~10-15 dk)
make -j4  # 4 thread (Jetson Nano 4 core)

echo ""
echo "================================================"
echo "✅ OpenADAS Kurulumu Tamamlandı!"
echo "================================================"
echo ""
echo "Çalıştırma:"
echo "  cd ~/open-adas/build"
echo "  ./open-adas --camera 0 --model yolov4-tiny"
echo ""
echo "TensorRT FP16 ile:"
echo "  ./open-adas --camera 0 --model yolov5s_trt_fp16.engine --tensorrt"
echo ""
echo "MQTT köprüsü ile:"
echo "  python3 ~/car_edge_ai_vision/adas_home_assistant_bridge.py &"
echo "  python3 ~/car_edge_ai_vision/adas_hmi_display_config.py"
echo ""
echo "🚀 TensorRT FP16: ~30ms/frame (30 FPS) — gerçek zamanlı ADAS"
echo "⚡ FP32 (TensorRT yok): ~200ms/frame (5 FPS) — sürüş için yetersiz"
echo ""

# -----------------------------------------------------------------------------
# 7. systemd Service (Otomatik Başlatma)
# -----------------------------------------------------------------------------
echo "🔧 systemd service oluşturuluyor..."
sudo tee /etc/systemd/system/adas-vision.service > /dev/null << 'EOF'
[Unit]
Description=Jarvis Edge-AI Vision & ADAS
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/jarvis/car_edge_ai_vision/adas_hmi_display_config.py
WorkingDirectory=/home/jarvis/open-adas/build
Restart=always
User=jarvis
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable adas-vision
sudo systemctl start adas-vision

echo "✅ ADAS Vision servisi aktif (otomatik başlatma)"
echo "Durum: sudo systemctl status adas-vision"
echo ""
echo "Modül 24: Jarvis Edge-AI Vision & ADAS mimarisi hazır!"