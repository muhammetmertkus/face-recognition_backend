@echo off
echo Docker Entegrasyonlu GitHub Yükleme Scripti (PORT Sorununa Çözüm)
echo ---------------------------------------------------------------

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

:: Railway Docker çözümü için dosyaları ekle (PORT sorunu çözümü ile birlikte)
git add Dockerfile .dockerignore railway.json start.sh
git commit -m "Railway dağıtımı için Docker çözümü eklendi (PORT sorunu giderildi)"
git push

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
echo.
echo Railway'de projenizi güncelleyin. Docker entegrasyonu sayesinde:
echo 1. dlib kurulum sorunu çözülecektir.
echo 2. PORT değişkeni sorunu düzeltildi.
pause 