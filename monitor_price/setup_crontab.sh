#!/bin/bash
# Linux 系统定时任务配置脚本
# 用途：设置每天早上6点自动运行爬虫

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  二手回收爬虫定时任务配置脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取项目目录（脚本所在目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/run_daily_crawl.py"

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}错误：找不到 run_daily_crawl.py${NC}"
    exit 1
fi

# 给脚本添加执行权限
chmod +x "$PYTHON_SCRIPT"
echo -e "${GREEN}✓${NC} 已添加执行权限"

# 检测 Python 路径
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python)
fi

if [ -z "$PYTHON_PATH" ]; then
    echo -e "${RED}错误：未找到 Python${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 路径: $PYTHON_PATH"

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"
echo -e "${GREEN}✓${NC} 日志目录: $SCRIPT_DIR/logs"

# 定时任务配置
CRON_JOB="0 6 * * * cd $SCRIPT_DIR && $PYTHON_PATH $PYTHON_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

# 检查是否已经存在相同的定时任务
if crontab -l 2>/dev/null | grep -q "$PYTHON_SCRIPT"; then
    echo -e "${YELLOW}⚠${NC}  定时任务已存在，正在更新..."
    # 删除旧任务
    crontab -l 2>/dev/null | grep -v "$PYTHON_SCRIPT" | crontab -
fi

# 添加新任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo -e "${GREEN}✓${NC} 定时任务已添加"
echo ""
echo -e "${YELLOW}定时任务详情：${NC}"
echo "  执行时间: 每天早上 6:00"
echo "  执行命令: $PYTHON_PATH $PYTHON_SCRIPT"
echo "  日志文件: $SCRIPT_DIR/logs/cron.log"
echo ""

# 显示当前所有定时任务
echo -e "${YELLOW}当前所有定时任务：${NC}"
crontab -l

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}配置完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}提示：${NC}"
echo "  1. 查看定时任务: crontab -l"
echo "  2. 编辑定时任务: crontab -e"
echo "  3. 删除所有任务: crontab -r"
echo "  4. 查看执行日志: tail -f $SCRIPT_DIR/logs/cron.log"
echo "  5. 手动测试运行: $PYTHON_PATH $PYTHON_SCRIPT"
echo ""
