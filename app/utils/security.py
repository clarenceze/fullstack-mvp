# app/utils/security.py
import re

def validate_sql(sql: str) -> tuple[bool, str, str]:
    """
    🧱 SQL 安全審查函數
    ---------------------
    功能：
        1️⃣ 僅允許 SELECT 語句
        2️⃣ 限制查詢資料表為 vgs_view
        3️⃣ 自動補上 LIMIT 子句（若缺少）
        4️⃣ 拒絕出現敏感關鍵字（DROP、ALTER、UPDATE、INSERT...）
    
    參數：
        sql (str): 由 LLM 生成的 SQL 語句（例如 SELECT ... FROM vgs_view ...）

    返回：
        (passed, result, tag)
        - passed (bool): 是否通過安全審查
        - result (str): 通過時返回修正後 SQL，否則返回錯誤原因
        - tag (str): 用於日誌標籤（如 "pass"、"reject_non_select"）
    """

    # === 🔹 預處理：去除多餘空格與結尾分號 ===
    sql = sql.strip().rstrip(";")

    # === 1️⃣ 僅允許 SELECT ===
    if not sql.lower().startswith("select"):
        return False, "❌ 拒絕執行：僅允許 SELECT 語句。", "reject_non_select"

    # === 2️⃣ 限制查詢表：僅允許 vgs_view ===
    # 若 Prompt 出錯產生了其他表名，直接拒絕
    if re.search(r"\b(from|join)\b\s+(?!vgs_view\b)", sql, re.IGNORECASE):
        return False, "❌ 拒絕執行：僅允許查詢資料表 vgs_view。", "reject_wrong_table"

    # === 3️⃣ 拒絕敏感關鍵字 ===
    forbidden = ["update", "delete", "insert", "drop", "alter", "create", "truncate"]
    for kw in forbidden:
        if re.search(rf"\b{kw}\b", sql, re.IGNORECASE):
            return False, f"❌ 拒絕執行：檢測到敏感關鍵字 `{kw.upper()}`。", "reject_keyword"

    # === 4️⃣ 若無 LIMIT，自動補上 LIMIT 20 ===
    if not re.search(r"\blimit\b", sql, re.IGNORECASE):
        sql += " LIMIT 20"

    # === ✅ 通過審查 ===
    return True, sql, "pass"
