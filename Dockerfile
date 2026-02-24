FROM python:3.10-slim

WORKDIR /workspace

# ------------------------------------------------------------
# System Dependencies (NO GUI / NO OpenGL)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    gcc \
    g++ \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Install PaddlePaddle CPU
# ------------------------------------------------------------
RUN pip install --no-cache-dir paddlepaddle==2.6.2 \
    -f https://www.paddlepaddle.org.cn/whl/linux/cpu/avx/stable.html

# ------------------------------------------------------------
# Install PaddleOCR WITHOUT automatic dependencies
# (We control them manually)
# ------------------------------------------------------------
RUN pip install --no-cache-dir paddleocr==2.7.0.3 --no-deps

# ------------------------------------------------------------
# Install Required Dependencies Manually
# (Controlled / No GUI OpenCV)
# ------------------------------------------------------------
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    opencv-python-headless==4.6.0.66 \
    shapely==2.0.3 \
    pyclipper \
    decorator \
    astor \
    opt_einsum \
    httpx \
    PyMuPDF==1.20.2 \
    tqdm \
    scikit-image \
    scipy \
    imgaug \
    lmdb \
    lxml \
    openpyxl \
    pdf2docx \
    python-docx \
    pyyaml \
    rapidfuzz \
    visualdl \
    beautifulsoup4 \
    attrdict \
    fire \
    fonttools

CMD ["/bin/bash"]
