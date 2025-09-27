# 使用 Python 3.11 的轻量版镜像作为基础镜像（体积小，适合部署）
FROM python:3.11-slim

# 设置容器内的工作目录为 /app，后续命令都在此目录执行
WORKDIR /app

# 安装系统依赖：
# - build-essential：编译 C 扩展需要（很多 Python 包依赖）
# - libpq-dev：PostgreSQL 客户端头文件/库（psycopg2 需要）
# - curl：调试或下载的小工具
# --no-install-recommends：只装最小依赖，避免镜像“变胖”
# 安装后清理 apt 缓存，进一步减小镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# 仅复制 requirements.txt 进入镜像，利用 Docker 层缓存提升构建速度
COPY requirements.txt .

# 安装 Python 依赖；--no-cache-dir 不保留 pip 缓存，减小镜像
RUN pip install --no-cache-dir -r requirements.txt

# 再把项目源代码复制进镜像（包括 /app/scripts、/app/web 等）
COPY . /app

# 暴露容器内的 8000 端口（真正的端口映射在 docker-compose.yml 里做）
EXPOSE 8000


# 容器启动时运行 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]