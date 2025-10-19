# 🚀 Fullstack MVP Project

## 🧭 项目概述 (Overview)

本项目是一个基于 **FastAPI + PostgreSQL + Docker** 的全栈 Web 应用，  
实现了从 **后端 API 开发 → 容器化部署 → 自动化测试与安全扫描 → CI/CD 流程** 的完整工程闭环。  

特点：
- 🧩 模块化结构（后端、前端、数据、部署分层清晰）  
- 🔒 集成多层安全扫描与分支保护机制  
- 🚀 使用 GitHub Actions 实现 CI/CD 自动化  
- 🧱 可直接通过 Docker Compose 一键部署  

---

## ⚙️ 技术栈 (Tech Stack)

| 分类 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 后端框架 | FastAPI |
| 数据库 | PostgreSQL |
| 前端 | 原生 HTML / JS |
| 部署 | Docker, Docker Compose |
| Web Server | Nginx |
| CI/CD | GitHub Actions |
| 安全工具 | Bandit, Gitleaks, pip-audit, Hadolint |
| 操作系统 | Linux (CentOS / Ubuntu) |

---

## 🧱 项目目录结构 (Project Structure)

```bash
[root@iZt4nfqkaaz5ozov55zgrkZ fullstack-mvp]# tree
.
├── app
│   ├── data
│   ├── Dockerfile
│   ├── __init__.py
│   ├── main.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── main.cpython-311.pyc
│   ├── requirements.txt
│   ├── scripts
│   │   ├── init_db.py
│   │   └── __pycache__
│   │       └── init_db.cpython-311.pyc
│   ├── tests
│   │   ├── __pycache__
│   │   │   └── test_smoke.cpython-311-pytest-8.4.2.pyc
│   │   └── test_smoke.py
│   └── web
├── data
│   └── vgsales.csv
├── deploy
│   ├── certbot-renew.service
│   ├── certbot-renew.sh
│   ├── certbot-renew.timer
│   └── deploy_nginx.sh
├── docker-compose.yml
├── docs
│   ├── CNAME
│   └── index.html
├── download_data.py
├── nginx
│   └── api.conf
├── README.md
└── web
    └── index.html

模块说明
| 目录                       | 说明                          |
| ------------------------ | --------------------------- |
| `app/`                   | 后端应用主目录（FastAPI 逻辑、测试、依赖文件） |
| `app/main.py`            | FastAPI 入口文件                |
| `app/tests/`             | Pytest 自动化测试                |
| `app/scripts/init_db.py` | 数据库初始化脚本                    |
| `data/`                  | 数据文件（如 vgsales.csv）         |
| `deploy/`                | Nginx + SSL 自动部署与证书续签脚本     |
| `nginx/`                 | Nginx 配置文件目录                |
| `web/`                   | 静态前端页面                      |
| `docker-compose.yml`     | 一键部署配置文件                    |
| `docs/`                  | GitHub Pages 文件夹        |
| `README.md`              | 项目说明文档                      |




🚀 快速部署 (Quick Deployment)

1️⃣ 克隆项目
git clone https://github.com/<your-username>/fullstack-mvp.git
cd fullstack-mvp


2️⃣ 创建环境变量文件
cp .env.example .env

编辑 .env 文件，填写数据库凭证：
POSTGRES_USER=appuser
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=appdb
DATABASE_URL=postgresql://appuser:${POSTGRES_PASSWORD}@db:5432/appdb


3️⃣ 构建与启动容器
docker-compose up -d --build


4️⃣ 验证运行状态
http://localhost:8000/docs


🌐 Nginx 自动化部署与 HTTPS 证书配置 (Nginx Deployment & SSL)
📦 一键部署脚本
项目已内置自动化脚本 deploy/deploy_nginx.sh，可一键完成：
🔧 安装 Nginx
📁 创建站点配置目录
🔗 软链接配置到 /etc/nginx/sites-enabled/
🔒 自动申请/续签 SSL 证书（Certbot）
✅ 重启 Nginx 服务

🧰 使用方法
cd deploy
sudo bash deploy_nginx.sh
#!/bin/bash
set -e

DOMAIN="yourdomain.com"
EMAIL="you@example.com"
NGINX_CONF="/etc/nginx/sites-available/fullstack-mvp"
NGINX_LINK="/etc/nginx/sites-enabled/fullstack-mvp"



查看状态：

sudo systemctl list-timers | grep certbot


⚙️ 环境变量说明 (Environment Variables)

| 变量名                 | 描述       | 示例                                            |
| ------------------- | -------- | --------------------------------------------- |
| `POSTGRES_USER`     | 数据库用户名   | appuser                                       |
| `POSTGRES_PASSWORD` | 数据库密码    | securepass                                    |
| `POSTGRES_DB`       | 数据库名     | appdb                                         |
| `DATABASE_URL`      | 数据库连接字符串 | postgresql://appuser:securepass@db:5432/appdb |
| `LOG_LEVEL`         | 日志级别     | INFO                                          |
| `APP_ENV`           | 环境类型     | development / production                      |


🔒 安全策略 (Security Policy)
本地安全

.env 文件存储敏感信息，已加入 .gitignore

生产环境禁用 DEBUG=True

CI 安全扫描
工具	功能
Bandit	源码安全扫描
Gitleaks	密钥泄露检测
pip-audit	依赖漏洞检测
Hadolint	Dockerfile 规范检测
分支保护

✅ 禁止直接 push main

✅ 必须通过 Pull Request

✅ 所有 PR 必须通过 CI 检查


🧪 自动化测试与 CI/CD
| 工作流                             | 触发条件             | 功能                  |
| ------------------------------- | ---------------- | ------------------- |
| CI1 - Test & Security Scan      | push / PR → main | 冒烟测试 + 安全扫描         |
| CI2 - Build & Push Docker Image | CI1 成功后          | 构建并推送镜像到 Docker Hub |


🧱 项目维护建议
🧪 每次改动前新建分支
🧰 定期运行 pip-audit
🪵 保留至少 7 天日志
🌐 定期检查 SSL 证书续签状态

📄 License
This project is licensed under the MIT License.
See LICENSE
 for details.


 📚 作者信息 (Author)
Author: Hu Rongze (clarence)
Institute: National Taiwan University – Graduate Institute of Biomedical Electronics and Bioinformatics
GitHub: clarenceze

test for prod CD