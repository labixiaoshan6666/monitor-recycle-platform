#!/bin/bash

# 二手家电回收价格监控平台 - 快速启动脚本 (macOS/Linux)
# 功能: 自动启动后端和前端服务

echo ""
echo "========================================"
echo "二手家电回收价格监控平台"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8 以上版本"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js 16 以上版本"
    exit 1
fi

echo "[✓] Python 已安装"
echo "[✓] Node.js 已安装"
echo ""

# 检查虚拟环境
if [ ! -d "backend/.venv" ]; then
    echo "[创建] 创建 Python 虚拟环境..."
    cd backend
    python3 -m venv .venv
    cd ..
fi

# 激活虚拟环境并安装依赖
echo "[安装] 安装 Python 依赖..."
source backend/.venv/bin/activate
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[错误] 安装 Python 依赖失败"
    exit 1
fi

echo "[✓] Python 依赖已安装"
echo ""

# 检查数据库迁移
echo "[检查] 检查数据库迁移..."
cd backend
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "[警告] 数据库迁移出现问题，请检查 MySQL 配置"
fi
cd ..

echo ""
echo "========================================"
echo "启动服务"
echo "========================================"
echo ""

# 启动后端
echo "[启动] 后端服务启动中 (8000)..."
source backend/.venv/bin/activate
cd backend
python manage.py runserver &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "[启动] 前端服务启动中 (5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "服务已启动"
echo "========================================"
echo ""
echo "前端: http://localhost:5173"
echo "后台: http://localhost:8000/admin"
echo "API:  http://localhost:8000/api"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 捕获信号，优雅关闭
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 等待进程
wait
