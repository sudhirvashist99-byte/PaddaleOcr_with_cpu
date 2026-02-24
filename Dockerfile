FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    poppler-utils \
    libglib2.0-0 \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paddlepaddle==2.6.2 \
    -f https://www.paddlepaddle.org.cn/whl/linux/cpu/avx/stable.html

RUN pip install --no-cache-dir \
    paddleocr==2.7.0.3 \
    shapely==2.0.3 \
    pyclipper \
    decorator \
    astor \
    opt_einsum \
    httpx \
    PyMuPDF==1.20.2 \
    opencv-python-headless \
    numpy==1.26.4 \
    tqdm

CMD ["/bin/bash"]
