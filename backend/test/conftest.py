import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# 使用独立的测试数据库，避免污染真实 star_dream.db
TEST_DB = os.path.join(BACKEND_DIR, "test_auth.db")
os.environ["DATABASE_URL"] = "sqlite:///" + TEST_DB.replace("\\", "/")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
    # 释放数据库连接后再删除测试库文件，避免 Windows 文件占用
    from app.db import engine
    engine.dispose()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
