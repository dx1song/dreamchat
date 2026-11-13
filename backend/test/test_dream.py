import json
import uuid

import pytest

MOCK_REPORT = {
    "dream_keyword": "梦见蛇",
    "core_meaning": "测试核心寓意",
    "interpretations": [{"focus": "事业", "content": "事业解读测试"}],
    "advice": ["建议1", "建议2", "建议3"],
    "verdict": "好梦",
}


@pytest.fixture
def token(client):
    username = "dream_" + uuid.uuid4().hex[:8]
    client.post("/api/auth/register", json={
        "username": username, "password": "123456", "email": username + "@example.com",
    })
    resp = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    return resp.json()["data"]["token"]


def _payload(**kw):
    base = {
        "dream_content": "梦见自己在一片星空下奔跑，前方有一条发光的大蛇",
        "dream_time": "昨晚", "gender": "男", "age": "26-35",
        "job": "教师", "focuses": ["事业"],
    }
    base.update(kw)
    return base


def test_analyze_success(client, token, monkeypatch):
    monkeypatch.setattr("app.routers.dream.chat", lambda messages, **kw: json.dumps(MOCK_REPORT, ensure_ascii=False))
    resp = client.post("/api/dream/analyze", json=_payload(), headers={"Authorization": "Bearer " + token})
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["dream_keyword"] == "梦见蛇"
    assert data["data"]["report"]["verdict"] == "好梦"
    assert data["data"]["record_id"]


def test_analyze_unauthorized(client):
    resp = client.post("/api/dream/analyze", json=_payload())
    assert resp.json()["code"] == 40101


def test_dream_content_too_short(client, token):
    resp = client.post("/api/dream/analyze", json=_payload(dream_content="太短"),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_invalid_dream_time(client, token):
    resp = client.post("/api/dream/analyze", json=_payload(dream_time="上个月"),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_empty_focuses(client, token):
    resp = client.post("/api/dream/analyze", json=_payload(focuses=[]),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_ai_failure(client, token, monkeypatch):
    def boom(messages, **kw):
        raise RuntimeError("AI error")
    monkeypatch.setattr("app.routers.dream.chat", boom)
    resp = client.post("/api/dream/analyze", json=_payload(), headers={"Authorization": "Bearer " + token})
    data = resp.json()
    assert data["code"] == 50001
    assert data["message"] == "生成失败，请稍后重试"
