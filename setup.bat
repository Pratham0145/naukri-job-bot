@echo off
echo ============================================
echo   Naukri Auto Job Applier — Windows Setup
echo ============================================
echo.

echo [1/3] Installing Python dependencies...
pip install playwright flask flask-cors

echo.
echo [2/3] Installing Playwright Chromium browser...
python -m playwright install chromium

echo.
echo [3/3] Creating required folders...
if not exist "all resumes\default" mkdir "all resumes\default"
if not exist "all excels" mkdir "all excels"
if not exist "logs" mkdir "logs"

echo.
echo ============================================
echo   Setup complete!
echo.
echo   Next steps:
echo   1. Add your resume PDF to: all resumes\default\resume.pdf
echo   2. Edit config\secrets.py  — add your Naukri email + password
echo   3. Edit config\personals.py — add your details
echo   4. Edit config\search.py   — set your job keywords
echo   5. Run:  python runBot.py
echo   6. View applied jobs:  python app.py  then open localhost:5000
echo ============================================
pause
