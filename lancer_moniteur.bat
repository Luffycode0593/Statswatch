@echo off
echo ========================================
echo    Moniteur Système - PC Stats
echo ========================================
echo.
echo Installation des dependances...
pip install -r requirements.txt
echo.
echo Lancement de l'application...
python system_monitor.py
pause 