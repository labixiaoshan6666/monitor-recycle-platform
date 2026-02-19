# Gunicorn 配置文件
# 
# 注意：如果使用宝塔面板部署，此文件会被忽略
# 宝塔会使用自己生成的配置：/www/server/pyproject_manager/versions/3.9/gunicorn_config.py
# 
# 此文件适用于：
# - 手动部署（不使用宝塔）
# - Docker部署
# - 使用 deploy.sh 自动部署脚本
# - 其他云平台部署

import multiprocessing
import os

# 服务器绑定地址
bind = '127.0.0.1:8000'

# 工作进程数
# 推荐：CPU核心数 * 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'sync'

# 每个工作进程处理的最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 超时时间（秒）
timeout = 300
keepalive = 2
graceful_timeout = 30

# 日志配置 - 使用相对路径，避免权限问题
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

accesslog = os.path.join(LOG_DIR, 'access.log')
errorlog = os.path.join(LOG_DIR, 'error.log')
loglevel = 'info'

# 进程命名
proc_name = 'recycle_platform'

# 是否后台运行
daemon = False

# 捕获输出
capture_output = True

# 预加载应用
preload_app = True
