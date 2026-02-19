# 二手家电回收价格监控平台

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0-brightgreen)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

一个现代化的二手家电回收价格监控平台，提供实时价格跟踪、以旧换新政策展示和AI智能问答功能。

## ✨ 核心功能

- 🔍 **价格监控** - 三级菜单选择，实时价格追踪，7天趋势图展示
- 📱 **智能搜索** - 产品和政策模糊搜索，快速定位目标信息  
- 🤖 **AI问答** - DeepSeek驱动，专业解答以旧换新政策问题
- 📄 **政策管理** - 支持文字内容和PDF附件上传
- 🎨 **现代UI** - 响应式设计，流畅交互体验

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 20+
- MySQL 8.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/labixiaoshan6666/recycle-platform.git
cd recycle-platform
```

2. **配置数据库**
```bash
# 创建数据库
mysql -u root -p
> CREATE DATABASE recycle_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
> EXIT;
```

3. **配置环境变量**
```bash
# 后端配置
cd recycle_platform/backend
cp .env.example .env
# 编辑 .env，修改数据库密码等配置

# 爬虫配置
cd ../../monitor_price
cp .env.example .env
# 编辑 .env，修改数据库密码
```

4. **启动后端**
```bash
cd recycle_platform/backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r ../../requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. **启动前端**
```bash
# 新终端
cd recycle_platform/frontend
npm install
npm run dev
```

6. **访问应用**
- 前端: http://localhost:5173
- 后台: http://localhost:8000/admin

## 📁 项目结构

```
pre_sitproject/
├── recycle_platform/          # 主应用
│   ├── backend/               # Django后端
│   │   ├── backend/          # 配置目录
│   │   ├── recycle/          # 主应用
│   │   └── .env.example      # 环境变量模板
│   └── frontend/             # Vue前端
│       ├── src/
│       └── package.json
├── monitor_price/            # 价格爬虫
│   ├── monitor_price/
│   │   ├── spiders/         # 爬虫脚本
│   │   └── settings.py      # 爬虫配置
│   └── .env.example         # 环境变量模板
├── requirements.txt         # Python依赖
└── README.md               # 项目说明
```

## 🔌 主要API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/types/` | GET | 获取产品类型列表 |
| `/api/brands/` | GET | 获取品牌列表 |
| `/api/models/` | GET | 获取产品型号列表 |
| `/api/price-trend/` | GET | 获取价格趋势数据 |
| `/api/policies/` | GET | 获取政策列表 |
| `/api/ai-chat/` | POST | AI智能问答 |

详细文档请查看 `recycle_platform/README.md`

## 🛠️ 技术栈

**后端**
- Django 4.2.7 - Web框架
- MySQL 8.0 - 数据库
- Scrapy - 数据爬取

**前端**
- Vue 3 - UI框架
- Vite - 构建工具
- Axios - HTTP客户端
- ECharts - 图表库

## 📝 配置说明

### 后端环境变量 (.env)

```env
# Django配置
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*

# 数据库配置
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=recycle_db
MYSQL_USER=recycle_user
MYSQL_PASSWORD=your_password

# AI配置（可选）
DEEPSEEK_API_KEY=your_api_key
```

### 爬虫环境变量 (.env)

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=recycle_db
MYSQL_USER=recycle_user
MYSQL_PASSWORD=your_password
```

## 🔧 常用命令

```bash
# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic

# 运行爬虫
cd monitor_price
python run_daily_crawl.py
```

## 📦 生产部署

### 部署方式选择

| 方式 | 文档 | 适用场景 | 耗时 |
|------|------|----------|------|
| 🎯 **宝塔面板** | [BAOTA_DEPLOY.md](./BAOTA_DEPLOY.md) | 腾讯云/阿里云 + 宝塔 | 30分钟 |
| ⚡ **快速部署** | [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) | 快速上手 | 5-30分钟 |
| 🚀 **完整部署** | [DEPLOYMENT.md](./DEPLOYMENT.md) | 手动配置服务器 | 30-60分钟 |

### 快速命令

**本地开发（Windows）**：
```bash
start.bat
```

**本地开发（macOS/Linux）**：
```bash
./recycle_platform/start.sh
```

**宝塔面板部署**：
查看 [宝塔部署指南](./BAOTA_DEPLOY.md)

**服务器自动部署**：
```bash
sudo bash deploy.sh
```


 
**最后更新**: 2026-02-14
