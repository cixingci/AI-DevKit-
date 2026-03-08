@echo off
echo ================================
echo 启动 AI DevKit 后端服务
echo ================================
echo.

cd /d "G:\program\5.AI_pro_edit\backend"

echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 检查依赖包...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo 依赖包未安装，正在安装...
    pip install -r requirements.txt
)

echo.
echo 启动后端服务 (按Ctrl+C停止)...
echo 地址: http://localhost:8888
echo API文档: http://localhost:8888/docs
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

pause
