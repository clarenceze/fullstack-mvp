# app/main.py
# =========================================
# FastAPI 主应用
# 支持：
#  - PostgreSQL 数据查询接口
#  - 健康检查接口（供冒烟测试与监控使用）
#  - CORS 设置
# =========================================


from fastapi import FastAPI, Query   # ✅ 增加 Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from utils import validate_sql
import psycopg2
import time
import os
try:
    # ✅ CI 环境 (pytest 从仓库根目录运行)
    from app.seq2sql import generate_sql_from_nl
except ModuleNotFoundError:
    # ✅ Docker 运行环境 (/app 是工作目录)
    from seq2sql import generate_sql_from_nl
from utils.logger import setup_logger
logger = setup_logger("main")


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



# =========================================
# ✅ 新增接口：自然语言 → SQL 智能生成
# =========================================
@app.get("/api/query_llm")
def query_llm(question: str = Query(..., description="使用者的自然語言問題")):
    """
    調用 LLM (Gemini Seq2SQL)，將自然語言轉換為 SQL，
    通過安全審查後查詢資料庫，返回結果與審查日誌。
    """
    start_time = time.time()
    nl_query = question

    try:
        # === 1️⃣ 生成 SQL ===
        result = generate_sql_from_nl(nl_query)
        ai_sql = result.get("sql", "").strip()

        # === 2️⃣ 安全審查 ===
        passed, checked_sql, tag = validate_sql(ai_sql)
        if not passed:
            logger.warning(f"[{tag}] {nl_query} → {ai_sql} → {checked_sql}")
            raise HTTPException(status_code=400, detail=checked_sql)

        # === 3️⃣ 執行 SQL ===
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute(checked_sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        elapsed = round(time.time() - start_time, 3)
        logger.info(f"[PASS] {nl_query} | SQL={checked_sql} | rows={len(rows)} | time={elapsed}s")

        # === 4️⃣ 返回結果 ===
        return {
            "columns": columns,
            "data": rows,
            "sql": checked_sql,
            "elapsed": elapsed,
            "desc": result.get("desc", "")
        }

    except HTTPException:
        # 由 validate_sql 拋出，直接返回
        raise
    except Exception as e:
        logger.error(f"[ERROR] {nl_query} | err={str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ 系統錯誤：{str(e)}")