@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
start "Chatbot Sunucusu" cmd /k uvicorn chatbot_platform.interface.api.main:app --port 8000
echo Sunucu baslatiliyor, lutfen bekleyin...
timeout /t 4 /nobreak >nul
start "" http://localhost:8000/static/widget.html

echo.
echo ============================================================
echo  Chatbot ile sohbet etmek icin: http://localhost:8000/static/widget.html
echo  Bilgi yonetimi (ekle/duzenle/sil) icin: http://localhost:8000/static/admin.html
echo ============================================================
echo.
echo Bu pencereyi kapatabilirsiniz. Sunucuyu durdurmak icin
echo acilan "Chatbot Sunucusu" penceresini kapatin.
echo.
pause
