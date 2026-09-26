@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
start "Chatbot Sunucusu" cmd /k uvicorn chatbot_platform.interface.api.main:app --port 8000
echo Sunucu baslatiliyor, lutfen bekleyin...
timeout /t 4 /nobreak >nul
start "Internet Tuneli (ngrok)" cmd /k ngrok http --url=curry-landscape-condone.ngrok-free.dev 8000
start "" http://localhost:8000/static/widget.html

echo.
echo ============================================================
echo  Chatbot ile sohbet etmek icin: http://localhost:8000/static/widget.html
echo  Bilgi yonetimi (ekle/duzenle/sil) icin: http://localhost:8000/static/admin.html
echo  Internetten erisim (Meta webhook): https://curry-landscape-condone.ngrok-free.dev
echo ============================================================
echo.
echo Bu pencereyi kapatabilirsiniz. Durdurmak icin acilan
echo "Chatbot Sunucusu" ve "Internet Tuneli" pencerelerini kapatin.
echo Bilgisayar acik ve bu iki pencere acik oldugu surece sistem calisir.
echo.
pause
