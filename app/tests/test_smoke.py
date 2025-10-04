# =========================================
# 文件路径: app/tests/test_smoke.py
# 功能: FastAPI 冒烟测试 (Smoke Test)
# 说明:
#   - 验证 FastAPI 应用能否成功启动
#   - 验证 /api/health 接口是否能正常返回
#   - 不依赖任何真实服务器 (无需 Uvicorn / Nginx)
# =========================================
# =========================================
import sys, os

# 获取项目根目录（fullstack-mvp）
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


from fastapi.testclient import TestClient
from app.main import app  # 导入 FastAPI 实例

# 创建一个测试客户端 (内存中模拟 HTTP 请求)
client = TestClient(app)

def test_health_check():
    """
    基础冒烟测试：
    模拟访问 /api/health ，
    期望:
      - 返回状态码 200
      - 返回 JSON 中 status == "ok"
    """
    response = client.get("/api/health")  # 模拟请求
    assert response.status_code == 200, "健康检查接口未正常响应"
    data = response.json()
    assert isinstance(data, dict), "返回内容不是 JSON 格式"
    assert data.get("status") == "ok", f"返回状态异常: {data}"
