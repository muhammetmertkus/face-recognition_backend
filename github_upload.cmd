@echo off
echo Docker Entegrasyonlu GitHub Yükleme Scripti
echo ------------------------------------------

:: Git repo başlat (eğer ilk kez yapıyorsanız)
git init

:: Dosyaları hazırla
git add .

:: İlk commit (Eğer bu ilk commit'iniz değilse bu kısmı atlayabilirsiniz)
git commit -m "İlk sürüm: Yüz Tanıma Backend API"

:: GitHub repo bağlantısı ekle (eğer ilk kez yapıyorsanız)
git remote add origin https://github.com/muhammetmertkus/face-recognition_backend.git

:: Ana dalı main olarak ayarla (eğer ilk kez yapıyorsanız)
git branch -M main

:: GitHub'a gönder (ilk kez yapıyorsanız)
git push -u origin main

:: Railway Docker çözümü için dosyaları ekle
git add Dockerfile .dockerignore railway.json
git commit -m "Railway dağıtımı için Docker çözümü eklendi"
git push

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
echo.
echo Railway'de projenizi güncelleyin. Docker entegrasyonu sayesinde dlib kurulum sorunu çözülecektir.
pause 