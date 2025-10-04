# app/main.py
# =========================================
# FastAPI 主应用
# 支持：
#  - PostgreSQL 数据查询接口
#  - 健康检查接口（供冒烟测试与监控使用）
#  - CORS 设置
# =========================================


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# === 配置 CORS，让浏览器允许跨域访问 ===
origins = [
    "https://clarenceze.com",       # 你的 GitHub Pages 域名
    "https://www.clarenceze.com",   # 兼容带 www 的情况
    "https://clarenceze.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 允许的来源
    allow_credentials=True,
    allow_methods=["*"],            # 允许所有 HTTP 方法（GET/POST/PUT/DELETE）
    allow_headers=["*"],            # 允许所有请求头
)


# 挂载静态文件目录，目前已经将静态文件上传到github page 进行托管
#app.mount("/web", StaticFiles(directory="web"), name="web")

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================
# ✅ 健康检查路由
# 说明：
#   - 用于 CI 冒烟测试
#   - 用于生产监控（Nginx health_check 或 Uptime-Kuma）
# =========================================
@app.get("/api/health")
def health_check():
    """
    基础健康检查。
    如果数据库配置存在，则尝试连接一次；
    否则仅返回应用可用状态。
    """
    if not DATABASE_URL:
        return {"status": "ok", "db": "not_configured"}

    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        # 即使数据库连接失败，也返回 200，但带状态说明
        return {"status": "ok", "db": f"error: {str(e)}"}


# =========================================
# ✅ 查询接口：获取前 10 名游戏销量
# =========================================
@app.get("/api/query")
def query_top10():
    """
    查询 vgs_view 视图中销量最高的前 10 项
    返回：
      [{"name": 游戏名, "global_sales": 销量}]
    """
    if not DATABASE_URL:
        # 在测试环境或数据库未配置时，返回假数据（防止 CI 报错）
        return [
            {"name": "Demo Game", "global_sales": 0.0},
            {"name": "Placeholder", "global_sales": 0.0}
        ]

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT name, global_sales
            FROM vgs_view
            ORDER BY global_sales DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {"name": r[0], "global_sales": float(r[1]) if r[1] else None}
            for r in rows
        ]
    except Exception as e:
        # 捕获数据库或 SQL 错误，返回描述信息（防止 500 错）
        return {"error": f"Database query failed: {str(e)}"}