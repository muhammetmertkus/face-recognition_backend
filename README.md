# Yüz Tanıma Backend API

Bu proje, Flask kullanılarak geliştirilmiş bir yüz tanıma ve yoklama sistemi backend API'sidir. Öğrencilerin yüzlerini tanıyarak veya duygularını analiz ederek yoklama almayı sağlar.

## Özellikler

- Kullanıcı (Admin, Öğretmen, Öğrenci) rolleri ve kimlik doğrulama (JWT)
- Öğrenci, Öğretmen ve Ders Yönetimi (CRUD işlemleri)
- Yüz fotoğrafı yükleme ve yüz tanıma kodlamalarını kaydetme
- Derslere öğrenci kaydetme
- Fotoğraf veya kamera görüntüsü üzerinden yoklama alma
    - Yüz tanıma ile öğrenci tespiti
    - Duygu analizi (isteğe bağlı)
    - Yaş ve cinsiyet tahmini (isteğe bağlı)
- Yoklama kayıtlarını görme ve yönetme
- API dokümantasyonu (Flasgger ile Swagger UI)

## Teknolojiler

- Python 3.9+
- Flask
- Flask-JWT-Extended
- Pydantic (Veri doğrulama için)
- face_recognition (Yüz tanıma için)
- deepface (Duygu, yaş, cinsiyet analizi için)
- Pillow (Resim işleme için)
- Gunicorn (WSGI sunucusu)
- Flasgger (API dokümantasyonu)

## Kurulum ve Çalıştırma (Yerel)

1.  **Depoyu klonlayın:**
    ```bash
    git clone https://github.com/muhammetmertkus/face-recognition_backend.git
    cd face-recognition_backend
    ```

2.  **Gerekli sistem kütüphanelerini yükleyin:**
    `face_recognition` ve `dlib` için `cmake` ve C++ derleyicisi gereklidir.
    *   **Ubuntu/Debian:**
        ```bash
        sudo apt-get update
        sudo apt-get install build-essential cmake
        sudo apt-get install libopenblas-dev liblapack-dev
        sudo apt-get install libx11-dev libgtk-3-dev # dlib GUI için (opsiyonel ama önerilir)
        ```
    *   **macOS:**
        ```bash
        brew install cmake
        brew install openblas lapack
        ```
    *   **Windows:** CMake'i [resmi web sitesinden](https://cmake.org/download/) yükleyin ve Visual Studio C++ build tools'u kurun. `dlib` kurulumu Windows'ta daha karmaşık olabilir, WSL (Windows Subsystem for Linux) kullanmak daha kolay bir alternatif olabilir.

3.  **Sanal ortam oluşturun ve aktifleştirin:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

4.  **Python bağımlılıklarını yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *Not: `dlib` kurulumu uzun sürebilir.*

5.  **Çevre değişkenlerini ayarlayın:**
    Proje kök dizininde `.env` adında bir dosya oluşturun ve aşağıdaki değişkenleri tanımlayın:
    ```dotenv
    FLASK_APP=run.py
    FLASK_ENV=development # veya production
    SECRET_KEY=cok_gizli_bir_anahtar # Güçlü bir gizli anahtar kullanın
    JWT_SECRET_KEY=baska_cok_gizli_bir_anahtar # Güçlü bir JWT anahtarı kullanın
    # İsteğe bağlı: Veri dosyalarının ve yüklemelerin yolu
    # DATA_FOLDER=data
    # FACE_UPLOAD_FOLDER=uploads/faces
    # ATTENDANCE_UPLOAD_FOLDER=uploads/attendance
    ```

6.  **Veri ve yükleme klasörlerini oluşturun (eğer .env'de belirtilmediyse varsayılan olarak):**
    ```bash
    mkdir data
    mkdir uploads
    mkdir uploads/faces
    mkdir uploads/attendance
    ```

7.  **Uygulamayı çalıştırın:**
    ```bash
    flask run
    ```
    Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışacaktır.

## API Dokümantasyonu

Uygulama çalışırken Swagger UI arayüzüne `http://127.0.0.1:5000/apidocs` adresinden erişilebilir.

## Railway ile Dağıtım

Bu proje Railway üzerinde çalışacak şekilde yapılandırılmıştır:

- `Procfile`: Uygulamayı `gunicorn` ile başlatır.
- `runtime.txt`: Kullanılacak Python versiyonunu belirtir.
- `requirements.txt`: Gerekli Python paketlerini listeler.

Railway'e dağıtım yapmak için:

1.  Projeyi GitHub'a yükleyin.
2.  Railway'de yeni bir proje oluşturun ve GitHub deposunu bağlayın.
3.  Railway, `Procfile`'ı algılayacak ve uygulamayı otomatik olarak dağıtacaktır.
4.  Gerekli çevre değişkenlerini (örn. `SECRET_KEY`, `JWT_SECRET_KEY`) Railway proje ayarlarından ekleyin.
5.  Kalıcı depolama gerekiyorsa (yüklenen fotoğraflar, veri dosyaları için), Railway Volume servisini yapılandırın ve uygulamanın bu birimi kullanmasını sağlayın (muhtemelen `DATA_FOLDER`, `FACE_UPLOAD_FOLDER` gibi çevre değişkenlerini Railway Volume yoluna ayarlayarak).

## Katkıda Bulunma

Katkılarınız memnuniyetle karşılanır! Lütfen bir issue açın veya pull request gönderin...
