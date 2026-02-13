@echo off
REM 二手家电回收价格监控平台 - 快速启动脚本 (Windows)
REM 功能: 自动启动后端和前端服务

echo.
echo ========================================
echo 二手家电回收价格监控平台
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8 以上版本
    pause
    exit /b 1
)

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16 以上版本
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo [✓] Node.js 已安装
echo.

REM 检查虚拟环境
if not exist "backend\.venv" (
    echo [创建] 创建 Python 虚拟环境...
    cd backend
    python -m venv .venv
    cd ..
)

REM 激活虚拟环境并安装依赖
echo [安装] 安装 Python 依赖...
call backend\.venv\Scripts\activate
pip install -q -r requirements.txt

if errorlevel 1 (
    echo [错误] 安装 Python 依赖失败
    pause
    exit /b 1
)

echo [✓] Python 依赖已安装
echo.

REM 检查是否需要迁移数据库
echo [检查] 检查数据库迁移...
cd backend
python manage.py migrate --noinput
if errorlevel 1 (
    echo [警告] 数据库迁移出现问题，请检查 MySQL 配置
)
cd ..

echo.
echo [✓] 启动准备完毕
echo.
echo ========================================
echo 启动服务
echo ========================================
echo.

REM 启动后端
echo [启动] 后端服务启动中...
start "后端服务 - Django (8000)" cmd /k "cd backend && call .venv\Scripts\activate && python manage.py runserver"

REM 等待后端启动
timeout /t 3 /nobreak

REM 启动前端
echo [启动] 前端服务启动中...
start "前端服务 - Vue 3 (5173)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 服务已启动
echo ========================================
echo.
echo 前端: http://localhost:5173
echo 后台: http://localhost:8000/admin
echo API:  http://localhost:8000/api
echo.
echo 按 Ctrl+C 停止服务
echo.
pause
