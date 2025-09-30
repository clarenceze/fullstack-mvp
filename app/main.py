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

@app.get("/api/query")
def query_top10():
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
    return [{"name": r[0], "global_sales": float(r[1]) if r[1] else None} for r in rows]
