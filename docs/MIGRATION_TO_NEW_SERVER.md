# 全栈项目迁移至新虚拟机技术指导

本文档描述如何将 **fullstack-mvp** 从旧服务器完整迁移到一台新的 Linux 虚拟机（如阿里云 ECS），并与仓库中**实际使用**的部署方式一致。

> **说明**：根目录 `README.md` 中的「根目录 docker-compose、宿主机 Nginx 脚本」等与当前仓库不完全一致。生产部署请以 **`deploy/prod/docker-compose.prod.yml`** 与 **`.env.prod`** 为准。

---

## 一、架构与组件（迁移时要一起考虑）

| 组件 | 实现方式 | 说明 |
|------|----------|------|
| 应用 | Docker 镜像 `clarenceze/fullstack-mvp:latest` | 由 GitHub Actions CI2 构建并推送到 Docker Hub |
| 数据库 | 容器 `postgres:16`，数据在 Docker 卷 `prod_db_data` | 不应对外暴露 5432 |
| HTTPS / 反代 | `nginxproxy/nginx-proxy` + `nginxproxy/acme-companion` | 自动申请/续签 Let’s Encrypt，**非**宿主机 certbot 脚本 |
| 对外域名 | 当前 compose 中写死为 `api.clarenceze.com` | 换域名需改 `docker-compose.prod.yml` 中 `VIRTUAL_HOST` / `LETSENCRYPT_HOST` |
| 前端 | 静态站点托管在 GitHub Pages（见 `app/main.py` 注释与 CORS） | API 换域名时，需同步改 CORS 与前端请求的 API 地址 |

---

## 二、新虚拟机前置条件

### 2.1 系统与软件

1. 操作系统建议：**Ubuntu 22.04 LTS** 或同类长期支持版本。
2. 安装 **Docker Engine** 与 **Docker Compose 插件**（`docker compose` 子命令）。
3. 将用于部署的 Linux 用户加入 `docker` 组（若不用 root 直接操作 Docker）：
   - `sudo usermod -aG docker <用户名>` 后重新登录生效。

### 2.2 网络与安全组

1. 云厂商安全组 / 本机防火墙放行：**TCP 80、443**（证书签发与 HTTPS 必需）。
2. **不要**将 PostgreSQL 端口映射到公网。
3. 若使用 SSH 部署（含 GitHub Actions）：放行你的 **SSH 端口**（默认 22），并仅对你信任的 IP 开放（可选但推荐）。

### 2.3 域名 DNS

1. 若继续使用 **`api.clarenceze.com`**：在 DNS 中将该主机名的 **A 记录** 指向**新虚拟机公网 IP**。
2. 切换前可将 DNS **TTL 调小**，便于快速生效与回滚。
3. 证书签发要求：Let’s Encrypt 校验时，**公网能通过域名访问到新机的 80 端口**。

---

## 三、在新机上的目录与文件

### 3.1 获取代码

```bash
# 示例：与现有 CD 工作流一致时使用 /root；也可改为 /home/ubuntu 等，但需同步修改 GitHub Actions 中的路径
sudo git clone https://github.com/clarenceze/fullstack-mvp.git /root/fullstack-mvp
```

若不用 root，将 `/root` 换为你的主目录，并记住后文所有路径需一致。

### 3.2 生产环境变量 `deploy/prod/.env.prod`

在 **`/root/fullstack-mvp/deploy/prod/`**（或你的等价路径）创建 **`.env.prod`**，**不要提交到 Git**。

需与 `docker-compose.prod.yml` 中引用变量一致，至少包括：

| 变量 | 含义 |
|------|------|
| `POSTGRES_DB` | 数据库名 |
| `POSTGRES_USER` | 数据库用户 |
| `POSTGRES_PASSWORD` | 数据库密码 |
| `DATABASE_URL` | 应用连接串，容器内主机名必须为 **`db`**，例如：`postgresql://用户:密码@db:5432/库名` |
| `APP_PORT` | 应用端口相关配置（与 compose 中一致即可） |
| `GOOGLE_API_KEY` | 若应用使用 Google API |
| `LETSENCRYPT_EMAIL` | 证书通知邮箱 |

从旧机迁移时：**用安全通道复制旧机的 `.env.prod`**（如 scp、密码管理器），在新机上按需微调 `DATABASE_URL` 中的主机名（保持为 `db`）。

### 3.3 持久化目录（与 compose 挂载一致）

在 **`deploy/prod`** 下创建供 nginx-proxy / acme 使用的目录（若不存在）：

```bash
cd /root/fullstack-mvp/deploy/prod
mkdir -p certs vhost html logs acme
```

---

## 四、启动生产栈

在 **`deploy/prod`** 目录执行：

```bash
cd /root/fullstack-mvp/deploy/prod
docker compose -f docker-compose.prod.yml --env-file .env.prod pull
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

检查容器：

```bash
docker ps
docker logs prod_app --tail 50
docker logs prod_ssl --tail 50
```

健康检查（DNS 已指向新机且证书签发成功后）：

```bash
curl -sS https://api.clarenceze.com/api/health
```

---

## 五、数据库与 `init_db.py` 行为（迁移数据必读）

1. 容器 **`prod_app` 每次启动**会执行 `python scripts/init_db.py`（失败则打印警告并继续启动）。
2. **`app/scripts/init_db.py` 会 `DROP TABLE` 后从镜像内 CSV 全量导入**。注释里「已存在则跳过」与脚本实际逻辑不完全一致：**成功执行脚本意味着会重建表并导入 CSV**。
3. **若你只需默认演示数据**：新机空卷启动即可，由镜像内 CSV 自动灌库。
4. **若旧库有必须保留的修改数据**：
   - 在旧机对 PostgreSQL 做 **`pg_dump`**（逻辑备份），将备份文件传到新机；
   - 在新机先启动 compose，待 `prod_db` 健康后，将备份 **恢复到** 对应库；
   - 评估是否仍要在每次启动时运行 `init_db.py`（否则会再次清空并导入 CSV）。如需长期保留自定义数据，通常要在镜像/compose 层调整启动命令（属后续改造，不在本文「仅迁移」最小步骤内）。

---

## 六、不依赖 Docker Hub、仅本地构建（可选）

若新机暂时无法拉取 Hub 或需调试本地代码，可使用同目录下的 **`docker-compose.dev.yml`**（在 `deploy/prod` 内、使用 `build: ../../app` 的那份），仍以 `--env-file .env.prod` 启动，命令中将 `-f docker-compose.prod.yml` 换为 `-f docker-compose.dev.yml`。

正式环境与 CI/CD 仍以 **`docker-compose.prod.yml` + 镜像** 为准。

---

## 七、GitHub Actions CD 指向新机

仓库 **`.github/workflows/cd.yml`** 通过 SSH 在服务器上执行：

- 工作目录：**`/root/fullstack-mvp/deploy/prod`**
- 命令：`docker compose -f docker-compose.prod.yml --env-file .env.prod` 的 `down` / `pull` / `up -d`
- 健康检查 URL：**`https://api.clarenceze.com/api/health`**

迁移后请在 GitHub **Repository secrets** 中更新：

- **`SERVER_HOST`**：新虚拟机公网 IP 或 SSH 用域名
- 若 SSH 用户或密钥变更：同步更新 **`SERVER_USER`**、**`SSH_PRIVATE_KEY`**

若你把代码放在非 `/root/fullstack-mvp`，需**修改 workflow 中的 `cd` 路径**，与实机一致。

---

## 八、前端与 CORS

`app/main.py` 中 CORS 允许的来源包括 `https://clarenceze.com`、`https://www.clarenceze.com`、`https://clarenceze.github.io`。

若你更换 **API 域名**或 **前端站点域名**，需要：

1. 修改 compose 中 `VIRTUAL_HOST` / `LETSENCRYPT_HOST`（或对应环境配置）；
2. 修改 FastAPI 中 `allow_origins` 并重新构建/推送镜像；
3. 更新 GitHub Pages（或静态托管）上前端里请求的 **API Base URL**。

---

## 九、建议切换流程（减少停机）

1. 新机完成：Docker、克隆仓库、`.env.prod`、`mkdir` 持久化目录。
2. **暂不修改**公网 DNS，或先用本机 `hosts` 将 `api.clarenceze.com` 指向新机 IP 做联调（证书校验需真实 DNS 时以正式 DNS 为准）。
3. 在新机 `pull` + `up -d`，确认 `prod_db`、`prod_app`、`prod_nginx`、`prod_ssl` 均为运行状态。
4. 将 DNS A 记录切到新 IP，等待传播后确认 HTTPS 与 `/api/health`。
5. 更新 GitHub **`SERVER_HOST`** 等 Secrets，触发一次手动 workflow 或等待下次 CD 验证。
6. 旧机观察无流量后下线；**保留数据库备份**一段时间。

---

## 十、故障排查简表

| 现象 | 可能原因 |
|------|----------|
| 证书一直失败 | DNS 未指向新机、80 未放行、域名与 `LETSENCRYPT_HOST` 不一致 |
| `prod_app` 反复重启 | `DATABASE_URL` 错误、数据库未就绪、缺少依赖环境变量 |
| 前端跨域失败 | 浏览器来源不在 `allow_origins` 或 API 地址错误 |
| `pull` 镜像失败 | 网络/Docker Hub 限制；可临时改用本地 `build` 的 compose 文件 |

---

## 十一、文档与仓库一致性

- 生产真相源：**`deploy/prod/docker-compose.prod.yml`** + **`.env.prod`** + **`.github/workflows/cd.yml`**。
- 若更新根目录 `README.md`，建议将「快速部署」章节改为指向本文或上述路径，避免后续误用旧流程。

---

**文档版本**：与仓库 `deploy/prod/docker-compose.prod.yml`（nginx-proxy + acme-companion + Docker Hub 镜像）对齐撰写。若 compose 变更，请同步修订本节与操作命令。
