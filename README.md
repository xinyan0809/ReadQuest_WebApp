# 📚 ReadQuest

> 一款帮助你追踪阅读旅程的 Web 应用。记录正在读的书、制定阅读目标、查看进度，并和其他读者共享书单。

**🔗 线上体验：[readquest-webapp.vercel.app](https://readquest-webapp.vercel.app)**

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 📖 书目搜索 | 接入 [Open Library API](https://openlibrary.org/dev/docs/api)，实时搜索数百万册书籍 |
| 📋 阅读清单 | 将书籍加入「正在读」或「愿望清单」，随时管理书单 |
| 📊 进度追踪 | 按页数记录每本书的阅读进度，可视化展示完成百分比 |
| 🎯 阅读目标 | 设定「本月读 X 本书」等目标，完成后自动归档 |
| 🏆 成就徽章 | 完成特定里程碑（如读完 10 本书、添加 5 本愿望书）自动解锁徽章 |
| ⭐ 评分记录 | 读完一本书后打分（1–5 星），留存阅读记录 |
| 👥 社区动态 | 首页展示其他用户的最新阅读动态，发现好书 |
| 🔐 用户系统 | 注册、登录、记住登录状态（两周免登录） |

---

## 技术栈

- **后端**：Python · Django 4.x
- **数据库**：SQLite（开发） · 部署于 Vercel Serverless
- **静态文件**：WhiteNoise
- **前端**：HTML / CSS / JavaScript（原生，无前端框架）
- **外部 API**：Open Library Search API
- **部署**：Vercel（`@vercel/python`）

---

## 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/xinyan0809/ReadQuest_WebApp.git
cd ReadQuest_WebApp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库迁移
python manage.py migrate

# 4. 启动开发服务器
python manage.py runserver
```

访问 `http://127.0.0.1:8000`

---

## 项目结构

```
ReadQuest/
├── Project/          # Django 项目配置（settings, urls, wsgi）
├── readquest/        # 主应用
│   ├── models.py     # 数据模型：Book, Goal, ProgressRecord, Achievement...
│   ├── views.py      # 视图逻辑
│   ├── services.py   # Open Library API 封装
│   └── urls.py       # 路由配置
├── templates/        # HTML 模板
├── static/           # CSS / JS / 图片
└── requirements.txt
```

---

## 数据模型设计

```
User ──< ReadRecord >── Book   （多对多，通过中间表记录日期和评分）
User ──< currently_reading ── Book
User ──< wishlisted_by ── Book
User ──< Goal              （目标完成时自动从 current_goals 移入 completed_by）
User ──< ProgressRecord    （记录每本书当前读到第几页）
User ──< Achievement       （多对多，里程碑达成时解锁）
```

---

## 部署说明

项目部署在 Vercel Serverless 环境，针对其只读文件系统做了以下适配：

- 数据库路径切换至 `/tmp/db.sqlite3`（唯一可写目录）
- 应用冷启动时自动执行 `migrate` 和 `collectstatic`
- 通过 `VERCEL` 环境变量区分生产/开发配置
