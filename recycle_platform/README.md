# 二手家电回收价格监控平台

## 📱 项目概述

一个现代化的二手家电回收价格监控平台，提供实时价格跟踪和以旧换新政策展示功能。

**核心功能**：
- ✨ **价格监控** - 三级菜单（类型→品牌→型号）支持，实时价格数据，7天折线图趋势
- 🔍 **智能搜索** - 回收产品和政策模糊搜索，快速定位目标信息
- 🤖 **AI问答** - DeepSeek驱动的智能助手，专业解答以旧换新政策问题
- 📄 **政策管理** - 支持文字内容和PDF附件，后台便捷上传管理
- 🎨 **现代UI** - 响应式设计，流畅交互体验，深色主题支持准备

**技术栈**：
- **后端**: Django 4.2.7 + MySQL 8.0 + Python 3.8+
- **前端**: Vue 3 + Vite + Axios + ECharts
- **数据库**: MySQL 8.0（utf8mb4 字符集）

---

## 🚀 快速开始

### 前置要求

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 检查 Node.js 版本（需要 16+）
node --version

# 检查 MySQL 版本（需要 8.0+）
mysql --version
```

### 一键部署（开发环境）

```bash
# 1. 后端设置
cd backend

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r ../requirements.txt

# 配置环境变量
copy ..\\.env.example ..\\.env
# 编辑 .env，修改数据库配置和DeepSeek API密钥

# 初始化数据库
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 导入示例数据
python ..\\init_data.py

# 启动后端
python manage.py runserver

# 2. 前端设置（新终端）
cd frontend
npm install
npm run dev

# 3. 打开浏览器
# 前端: http://localhost:5173
# 后台: http://localhost:8000/admin
```

---

## 📊 数据库设计

### 核心表结构

#### `recycle_recycleproduct` - 回收产品表

```sql
CREATE TABLE recycle_recycleproduct (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  brand VARCHAR(50) NOT NULL,
  model VARCHAR(100) NOT NULL,
  avg_price DECIMAL(10,2) NOT NULL,
  scrape_date DATE NOT NULL,
  price_history JSON,
  created_at DATETIME AUTO_INCREMENT,
  INDEX idx_category_brand_model (category, brand, model),
  INDEX idx_scrape_date (scrape_date)
);
```

**示例数据**:
```json
{
  "id": 1,
  "product_code": "PHONE001",
  "name": "Apple iPhone 14 Pro Max",
  "category": "手机",
  "brand": "Apple",
  "model": "iPhone 14 Pro Max",
  "avg_price": "5800.00",
  "scrape_date": "2024-02-07",
  "price_history": [
    {"date": "2024-02-01", "price": 5650.00},
    {"date": "2024-02-02", "price": 5700.00},
    ...7日数据...
  ]
}
```

#### `recycle_policy` - 以旧换新政策表

```sql
CREATE TABLE recycle_policy (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  content LONGTEXT,
  attachment VARCHAR(255),
  publish_date DATE NOT NULL,
  INDEX idx_publish_date (publish_date)
);
```

### 数据库初始化

```bash
# 创建数据库
mysql -u root -p
> CREATE DATABASE recycle_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
> EXIT;

# Django 迁移
cd backend
python manage.py makemigrations
python manage.py migrate

# 导入示例数据
python ../init_data.py
```

---

## 🔌 API 接口文档

### 1. 获取家电类型

```http
GET /api/types/
```

**响应**:
```json
["手机", "电脑", "平板电脑"]
```

### 2. 获取品牌列表

```http
GET /api/brands/?category=手机
```

**参数**: `category` - 产品类型

**响应**:
```json
["Apple", "Huawei", "Samsung"]
```

### 3. 获取产品型号

```http
GET /api/models/?category=手机&brand=Apple
```

**参数**: 
- `category` - 产品类型
- `brand` - 产品品牌

**响应**:
```json
["iPhone 14 Pro Max", "iPhone 13", "iPhone 12"]
```

### 4. 获取价格趋势（核心接口）

```http
GET /api/price-trend/?category=手机&brand=Apple&model=iPhone%2014%20Pro%20Max
```

**参数**:
- `category` - 产品类型
- `brand` - 产品品牌  
- `model` - 产品型号

**响应**:
```json
{
  "product": {
    "id": 1,
    "product_code": "PHONE001",
    "name": "Apple iPhone 14 Pro Max",
    "category": "手机",
    "brand": "Apple",
    "model": "iPhone 14 Pro Max",
    "avg_price": 5800.00,
    "scrape_date": "2024-02-07"
  },
  "history": [
    {"date": "2024-02-01", "price": 5650.00},
    {"date": "2024-02-02", "price": 5700.00},
    ...7条记录...
  ]
}
```

### 5. 获取政策列表

```http
GET /api/policies/
```

**可选参数**: `keyword` - 搜索关键词

**响应**:
```json
[
  {
    "id": 1,
    "title": "2024年全国以旧换新补贴政策",
    "content": "根据国务院...",
    "publish_date": "2024-02-07",
    "attachment_url": "/media/policies/policy_2024.pdf"
  }
]
```

### 6. AI问答接口（新增）

```http
POST /api/ai-chat/
```

**请求体**:
```json
{
  "question": "什么是以旧换新政策？",
  "history": [
    {
      "role": "user",
      "content": "之前的问题",
      "timestamp": "14:30:25"
    }
  ]
}
```

**响应**:
```json
{
  "answer": "以旧换新政策是指...",
  "model": "deepseek-chat"
}
```

**配置说明**: 查看 [AI问答快速开始](./AI_QA_QUICKSTART.md)

---

## 📁 项目结构

```
project/
├── backend/                    # Django 后端
│   ├── recycle/               # 主应用
│   │   ├── models.py          # 数据模型（产品、政策）
│   │   ├── views.py           # API 视图
│   │   ├── urls.py            # 路由配置
│   │   ├── admin.py           # 后台管理配置
│   │   └── migrations/        # 数据库迁移
│   ├── backend/               # 项目配置
│   │   ├── settings.py        # Django 设置
│   │   ├── urls.py            # 主路由
│   │   └── wsgi.py            # WSGI 配置
│   ├── manage.py              # Django 命令工具
│   └── init_data.py           # 数据初始化脚本
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── App.vue            # 主应用组件
│   │   ├── main.js            # 入口文件
│   │   ├── api.js             # API 客户端
│   │   ├── style.css          # 全局样式
│   │   ├── components/        # 组件目录
│   │   └── assets/            # 静态资源
│   ├── package.json           # 依赖配置
│   ├── vite.config.js         # Vite 配置
│   └── index.html             # HTML 模板
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明
└── DEPLOYMENT.md              # 详细部署指南
```

---

## 🔧 常用命令

### 后端命令

```bash
# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver

# 数据导出/导入
python manage.py dumpdata recycle > data.json
python manage.py loaddata data.json

# 进入 Shell
python manage.py shell
```

### 前端命令

```bash
# 开发
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview

# 清除缓存
npm cache clean --force
```

---

## 🐛 问题排查

### 数据库连接失败

```bash
# 1. 检查 MySQL 是否运行
mysql -u root -p

# 2. 验证 .env 配置
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=recycle_db

# 3. 重启 MySQL 服务
# Windows:
net stop MySQL80
net start MySQL80
```

### CORS 错误

```bash
# 编辑 .env，确保包含前端地址
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 重启后端服务
python manage.py runserver
```

### 依赖安装失败

```bash
# 清除缓存后重装
npm cache clean --force
npm install --legacy-peer-deps

# 或升级 pip
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📦 生产部署

详见 [DEPLOYMENT.md](./DEPLOYMENT.md) 文档，包含：
- ✅ Gunicorn + Nginx 配置
- ✅ SSL 证书设置
- ✅ 性能优化建议
- ✅ 监控和日志配置

### 快速部署步骤

```bash
# 1. 后端构建
cd backend
gunicorn -w 4 backend.wsgi:application

# 2. 前端构建
cd frontend
npm run build

# 3. Nginx 配置
# 将 frontend/dist 部署到静态目录
# 配置反向代理到后端
```

---

## 🎨 功能演示

### 🤖 AI智能问答 (v1.2.0 新增)

**功能特性**：
- 🤖 基于DeepSeek大模型，专业解答政策问题
- 💬 支持多轮对话，保留上下文记忆
- ⚡ 快速响应，秒级回复
- 🎨 美观的对话界面设计
- 📱 完美支持移动端

**使用方法**：
1. 滚动到页面底部"AI智能问答"区域
2. 在输入框中输入您的问题
3. 点击"发送"按钮或按Enter键
4. AI将快速回复您的问题

**示例问题**：
- 什么是以旧换新政策？
- 如何参与以旧换新活动？
- 以旧换新有哪些补贴？
- 哪些产品可以参与以旧换新？

**配置指南**：
- 📖 [快速开始指南](./AI_QA_QUICKSTART.md) - 5分钟快速配置
- 📚 [详细配置文档](./AI_QA_SETUP.md) - 完整配置说明

---

### 🔍 智能搜索 (v1.1.0 新增)

**回收产品搜索**：
- 在"价格监控"模块顶部输入关键词（品牌、型号、类型等）
- 支持模糊搜索，快速定位目标产品
- 点击搜索结果自动跳转到价格趋势图

**政策搜索**：
- 在"以旧换新政策"模块顶部输入关键词
- 搜索政策标题和内容
- 即时过滤政策列表

**搜索特性**：
- ⚡ 快速响应（<500ms）
- 🎯 模糊匹配，智能识别
- 📱 移动端友好界面
- 🔄 实时更新结果

**详细说明**: 查看 [搜索功能使用指南](./SEARCH_GUIDE.md)

---

### 价格监控

1. 选择**家电类型**（手机、电脑、平板等）
2. 选择**品牌**（Apple、Huawei、Samsung 等）
3. 选择**型号**（iPhone 14、Mate 50 Pro 等）
4. 实时显示**7天价格趋势图**

**图表特性**：
- 平滑曲线展示价格变化
- 鼠标悬停显示具体数值
- 自适应响应式布局
- 实时更新标签

### 政策阅读

1. 左侧列出所有**以旧换新政策**
2. 点击政策显示**详细内容**
3. 支持**在线 PDF 预览**
4. 支持**下载附件**

---

## 📝 环境变量配置

复制 `.env.example` 为 `.env`，根据需要修改：

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=true                    # 开发: true, 生产: false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=recycle_db
MYSQL_USER=root
MYSQL_PASSWORD=password

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173

# DeepSeek AI (可选，用于AI问答功能)
DEEPSEEK_API_KEY=sk-your-api-key-here
```

**AI问答配置**：如需启用AI问答功能，请查看 [AI_QA_QUICKSTART.md](./AI_QA_QUICKSTART.md)

---

## 📚 文档导航

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 详细部署指南（生产环境）
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - 项目完成总结
- **[DATABASE.md](./DATABASE.md)** - 数据库设计和管理
- **[AI_QA_QUICKSTART.md](./AI_QA_QUICKSTART.md)** - 🤖 AI问答快速开始（新增）
- **[AI_QA_SETUP.md](./AI_QA_SETUP.md)** - 🤖 AI问答详细配置（新增）
- **[SEARCH_GUIDE.md](./SEARCH_GUIDE.md)** - 🔍 搜索功能使用指南
- **[SEARCH_FEATURE.md](./SEARCH_FEATURE.md)** - 🔍 搜索功能技术文档
- **[SEARCH_TEST_CHECKLIST.md](./SEARCH_TEST_CHECKLIST.md)** - 🔍 搜索功能验证清单
- **[QUICK_START.md](./QUICK_START.md)** - 快速开始指南
- **[FILES_CHECKLIST.md](./FILES_CHECKLIST.md)** - 文件清单

---

## 📄 许可证

MIT License

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2026-02-13  
**版本**: 1.2.0

## 🆕 更新日志

### v1.2.0 (2026-02-13)
- 🤖 新增AI智能问答功能（DeepSeek集成）
- 💬 支持多轮对话和上下文记忆
- 🎨 优化AI问答界面设计
- 📱 完善移动端AI问答体验
- 📝 添加AI问答配置文档

### v1.1.0 (2024-02-11)
- ✨ 新增回收产品搜索功能
- ✨ 新增政策内容搜索功能
- 🎨 优化搜索界面设计
- 📱 完善移动端响应式适配
- 📝 添加详细搜索功能文档

### v1.0.0 (2024-02-07)
- 🎉 初始版本发布
- ✨ 价格监控功能
- 📄 政策管理功能
- 🎨 现代化 UI 设计
