# ============================================================
# app/seq2sql.py
# ------------------------------------------------------------
# 功能：封装 Gemini 调用逻辑，将自然语言转换为 SQL 查询。
# 特性：
#   ✅ 自动加载 .env
#   ✅ 自动读取 prompt.md
#   ✅ 详细日志输出
#   ✅ 异常捕获 + 安全 JSON 解析
# ============================================================

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

# ------------------------------------------------------------
# ✅ 初始化日志
# ------------------------------------------------------------
logger = logging.getLogger("seq2sql")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# ------------------------------------------------------------
# ✅ 主函数：将自然语言转为 SQL
# ------------------------------------------------------------
def generate_sql_from_nl(user_query: str):
    """
    使用 Gemini API 生成 SQL 查询。
    参数：
        user_query (str): 使用者自然语言问题
    返回：
        dict: {"sql": "...", "desc": "..."} 或 {"error": "..."}
    """

    # 1️⃣ 加载 .env 环境变量
    try:
        env_path = Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"✅ 已加载环境变量：{env_path}")
        else:
            logger.warning(f"⚠️ 未找到 .env 文件：{env_path}")
    except Exception as e:
        logger.error(f"❌ 加载 .env 文件失败: {e}")

    # 2️⃣ 读取 API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ GOOGLE_API_KEY 未配置，请检查 .env 文件。")
        return {"error": "GOOGLE_API_KEY not found"}

    # 3️⃣ 初始化 Gemini 客户端
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"❌ 初始化 Gemini 客户端失败: {e}")
        return {"error": "Gemini client initialization failed"}

    # 4️⃣ 读取 Prompt 文件
    prompt_path = Path(__file__).resolve().parent / "prompt.md"
    if not prompt_path.exists():
        logger.error(f"❌ 找不到 prompt.md 文件：{prompt_path}")
        return {"error": "Prompt file not found"}

    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # 5️⃣ 组合内容
    content = f"{system_prompt}\n\n使用者問題：{user_query}"
    logger.info(f"🧠 生成請求內容：{user_query}")

    # 6️⃣ 调用 Gemini API
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=content,
        )
    except ClientError as e:
        logger.error(f"❌ Gemini API 调用失败: {e}")
        return {"error": f"Gemini API error: {e}"}
    except Exception as e:
        logger.error(f"❌ 未知错误：{e}")
        return {"error": f"Unknown error: {e}"}

    # 7️⃣ 输出解析
    raw_output = response.text.strip()
    logger.info(f"📩 原始模型输出：{raw_output}")

    # 尝试解析 JSON 输出
    try:
        result = json.loads(raw_output)
        if not isinstance(result, dict):
            raise ValueError("Parsed JSON 不是对象类型")
        # 确保键存在
        if "sql" not in result or "desc" not in result:
            raise KeyError("输出缺少 sql 或 desc 字段")
        return result
    except json.JSONDecodeError:
        logger.warning("⚠️ 模型输出不是严格 JSON，尝试修复格式...")
        # 尝试简单修复（去除 Markdown 代码块包裹）
        fixed = raw_output.replace("```json", "").replace("```", "").strip()
        try:
            result = json.loads(fixed)
            return result
        except Exception:
            logger.error("❌ JSON 解析失败，返回原始文本")
            return {"sql": None, "desc": raw_output}
    except Exception as e:
        logger.error(f"❌ 输出解析失败: {e}")
        return {"error": f"Failed to parse model output: {e}"}


# ------------------------------------------------------------
# ✅ 调试入口（可独立运行）
# ------------------------------------------------------------
if __name__ == "__main__":
    test_query = "找出 2015 年後在 PS4 平台銷量最高的前 10 款遊戲"
    result = generate_sql_from_nl(test_query)
    print("\n🎯 測試結果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
