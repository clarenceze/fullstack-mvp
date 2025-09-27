# 🎮 Fullstack-MVP: Video Game Sales Dashboard

这是一个基于 **FastAPI + PostgreSQL + Nginx** 的全栈最小可行产品 (MVP)。  
前端通过一个按钮调用后端 API，动态展示全球销量前 10 的游戏。

---

## 🚀 功能
- 后端：FastAPI 提供 `/api/query` 接口，返回数据库查询结果
- 数据库：PostgreSQL 存储 Kaggle 游戏销售数据
- 前端：原生 HTML + JS，点击按钮加载表格
- 部署：Nginx 作为反向代理 + 静态文件托管

---

## 📂 项目结构
fullstack-mvp/
├── app/ # FastAPI 应用
│ ├── main.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── scripts/init_db.py
├── data/ # 数据文件
│ └── vgsales.csv
├── web/ # 前端静态文件
│ └── index.html
├── nginx/clarenceze.com.conf # Nginx 配置文件（示例）
├── docker-compose.yml # 后端 + 数据库编排
└── README.md


---

## ⚡ 部署步骤

### 1. 克隆仓库
```bash
git clone https://github.com/<yourname>/fullstack-mvp.git
cd fullstack-mvp

2. 初始化数据库（仅第一次执行）
docker compose run app python app/scripts/init_db.py

3. 启动服务
docker compose up -d

4. 部署 Nginx 配置

将配置文件复制到 Nginx 目录并重载：

cp nginx/clarenceze.com.conf /etc/nginx/conf.d/
nginx -s reload

5. 访问服务

前端页面: http://clarenceze.com

API 接口: http://clarenceze.com/api/query

🛠️ 技术栈

FastAPI

PostgreSQL

Docker / Docker Compose

Nginx

原生 HTML + JavaScript
