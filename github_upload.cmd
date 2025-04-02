@echo off
echo Docker ve Şifre Sıfırlama API Güncellemesi
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

:: Şifre sıfırlama API güncelleme
git add app/routes/password_reset.py password_reset.md
git commit -m "Şifre sıfırlama API eklendi"
git push

:: Railway Docker çözümü için dosyaları güncelleme
git add Dockerfile requirements.txt .dockerignore railway.json start.sh
git commit -m "Railway dağıtımı için Docker çözümü güncellendi (dlib sorunları giderildi)"
git push

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
echo.
echo Güncellemeler:
echo 1. Şifre sıfırlama API eklendi
echo 2. Railway dlib kurulum sorunu çözüldü
echo 3. Production için dosyalar güncellendi
pause 