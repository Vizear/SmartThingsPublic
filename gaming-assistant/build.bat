@echo off
REM ═══════════════════════════════════════════════════════
REM  Altantis HUD — Build Script
REM  Run this from the gaming-assistant directory.
REM  Requires: pip install -r requirements.txt
REM ═══════════════════════════════════════════════════════

echo [HUD BUILD] Installing dependencies...
pip install -r requirements.txt

echo [HUD BUILD] Compiling to EXE...
pyinstaller ^
    --name "AltantisHUD" ^
    --onefile ^
    --windowed ^
    --icon NONE ^
    --hidden-import "anthropic" ^
    --hidden-import "mss" ^
    --hidden-import "PIL" ^
    --hidden-import "numpy" ^
    --hidden-import "PyQt6" ^
    --hidden-import "keyboard" ^
    --add-data "analyzer.py;." ^
    --add-data "monitor.py;." ^
    --add-data "popup.py;." ^
    --add-data "setup_dialog.py;." ^
    main.py

echo.
echo [HUD BUILD] Done! Find AltantisHUD.exe in the dist\ folder.
echo [HUD BUILD] Double-click it to run — it will appear in your system tray.
pause
