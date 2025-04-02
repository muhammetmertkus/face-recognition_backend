@echo off
echo Railway Docker Çalıştırma İzni Sorunu Çözümü
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

:: Şifre sıfırlama API güncelleme (Kimlik doğrulama gerektirmeyen sürüm)
git add app/routes/password_reset.py password_reset.md app/__init__.py
git commit -m "Şifre sıfırlama API kimlik doğrulama gerektirmeyecek şekilde güncellendi"
git push

:: Railway Docker çalıştırma izni sorununu çözmek için dosyaları güncelleme
git add Dockerfile start.sh railway.json .dockerignore
git commit -m "Railway start.sh çalıştırma izni sorunu çözüldü: bash ile çalıştırma ve chmod 755 izinleri eklendi"
git push

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
echo.
echo Yapılan güncellemeler:
echo 1. Şifre sıfırlama API kimlik doğrulama olmadan kullanılabilir hale getirildi
echo 2. Railway'de Container Failed to Start sorunu çözüldü:
echo    - Dockerfile'da start.sh için chmod 755 izni eklendi
echo    - CMD komutu /bin/bash start.sh olarak değiştirildi 
echo    - railway.json dosyası oluşturuldu ve startCommand: bash start.sh eklendi
echo    - Bu değişiklikler Railway'in start.sh dosyasını çalıştırabilmesini sağlar
echo 3. start.sh dosyasına log mesajı eklendi
echo.
echo Railway üzerinde yeniden dağıtım yapın: railway up
pause 