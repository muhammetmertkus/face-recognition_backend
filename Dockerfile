FROM python:3.9-slim

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli Python paketlerini kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Başlatma scriptini ekle ve çalıştırılabilir yap - Railway için özel izin ayarları
COPY start.sh .
RUN chmod 755 start.sh && \
    ls -la start.sh && \
    cat start.sh

# Uygulama kodunu kopyala
COPY . .

# Port ayarla - DEFAULT PORT tanımla
ENV PORT=8000

# Çalıştırma komutu - Doğrudan bash kullanarak çalıştır
CMD ["/bin/bash", "start.sh"] 