from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import psycopg2
import os

app = FastAPI()

# 挂载静态文件目录
app.mount("/web", StaticFiles(directory="web"), name="web")

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
