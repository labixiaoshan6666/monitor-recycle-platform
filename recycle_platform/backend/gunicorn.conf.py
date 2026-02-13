# Gunicorn 配置文件
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

# 日志配置
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# 进程命名
proc_name = 'recycle_platform'

# 是否后台运行
daemon = False

# 捕获输出
capture_output = True

# 预加载应用
preload_app = True
