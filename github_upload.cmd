@echo off
echo GitHub'a Yukleme Scripti
echo ---------------------

:: Git repo başlat
git init

:: Dosyaları hazırla
git add .

:: İlk commit
git commit -m "İlk sürüm: Yüz Tanıma Backend API"

:: GitHub repo bağlantısı ekle
git remote add origin https://github.com/muhammetmertkus/face-recognition_backend.git

:: Ana dalı main olarak ayarla
git branch -M main

:: GitHub'a gönder
git push -u origin main

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
pause 