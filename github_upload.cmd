@echo off
echo Railway Docker Çalıştırma İzni Sorunu Çözümü
echo ------------------------------------------

:: Git repo başlat (eğer ilk kez yapıyorsanız)
:: git init # Genellikle sadece bir kez gerekir

:: Dosyaları hazırla
git add .

:: İlk commit (Eğer bu ilk commit'iniz değilse bu kısmı atlayabilirsiniz)
:: git commit -m "İlk sürüm: Yüz Tanıma Backend API"

:: GitHub repo bağlantısı ekle (eğer ilk kez yapıyorsanız)
:: git remote add origin https://github.com/muhammetmertkus/face-recognition_backend.git

:: Ana dalı main olarak ayarla (eğer ilk kez yapıyorsanız)
:: git branch -M main

:: GitHub'a gönder (ilk kez yapıyorsanız)
:: git push -u origin main

:: --- Önceki Değişiklikleri Gönder (Gerekirse) ---
echo.
echo Mevcut degisiklikler gonderiliyor (varsa)...
git commit -m "chore: Cesitli guncellemeler"
git push

:: --- Data Klasörünü Ekleyip Gönder ---
echo.
echo Data klasoru GitHub'a ekleniyor...
git add data/
git add .gitignore  # .gitignore dosyasını da güncellediyseniz ekleyin
git commit -m "feat: Data klasorunu ve json dosyalarini ekle"
git push

echo.
echo İşlem tamamlandı!
echo Repository: https://github.com/muhammetmertkus/face-recognition_backend
echo.
echo Son Yapılan İşlem: Data klasörü GitHub'a eklendi.
echo **Unutmayın:** Eğer .gitignore dosyasında data klasörünü engelleyen bir kural vardıysa, bu komut dosyasını çalıştırmadan önce o kuralı kaldırmanız veya yorum satırı yapmanız gerekirdi.
echo.
echo Railway üzerinde yeniden dağıtım yapabilirsiniz: railway up
pause 