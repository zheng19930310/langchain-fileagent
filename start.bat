@echo off
echo ========================================
echo   Langchain FileAgent 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python环境，请先安装Python 3.9或更高版本
    pause
    exit /b 1
)
echo [成功] Python环境正常
echo.

echo [2/4] 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
)
echo [成功] 依赖包已安装
echo.

echo [3/4] 检查环境配置...
if not exist .env (
    echo [提示] 未找到.env文件，复制示例配置...
    copy .env.example .env
    echo [警告] 请编辑.env文件，填入你的OpenAI API Key
    pause
)
echo [成功] 环境配置就绪
echo.

echo [4/4] 启动应用...
echo 提示: 应用将运行在 http://localhost:8082
echo API文档: http://localhost:8082/docs
echo.

python main.py

pause
