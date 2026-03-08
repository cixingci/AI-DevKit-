@echo off
echo Starting AI DevKit Backend...
cd /d G:\program\5.AI_pro_edit\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
pause
