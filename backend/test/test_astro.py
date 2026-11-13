import json
import uuid

import pytest

MOCK_REPORT = {
    "personality": "测试性格分析",
    "fortune": {
        "career": {"level": "★★★★☆", "desc": "事业测试"},
        "love": {"level": "★★★☆☆", "desc": "感情测试"},
        "health": {"level": "★★★★☆", "desc": "健康测试"},
        "wealth": {"level": "★★★☆☆", "desc": "财运测试"},
    },
    "lucky_color": "珊瑚红",
    "lucky_number": "7",
    "advice": ["建议1", "建议2"],
}


@pytest.fixture
def token(client):
    username = "astro_" + uuid.uuid4().hex[:8]
    client.post("/api/auth/register", json={
        "username": username, "password": "123456", "email": username + "@example.com",
    })
    resp = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    return resp.json()["data"]["token"]


def _payload(**kw):
    base = {
        "birth_date": "1995-04-05", "gender": "男", "relationship": "单身",
        "job": "软件工程师", "focuses": ["性格", "事业"],
    }
    base.update(kw)
    return base


def test_analyze_success(client, token, monkeypatch):
    monkeypatch.setattr("app.routers.astro.chat", lambda messages, **kw: json.dumps(MOCK_REPORT, ensure_ascii=False))
    resp = client.post("/api/astro/analyze", json=_payload(), headers={"Authorization": "Bearer " + token})
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["zodiac"] == "白羊座"
    assert data["data"]["report"]["lucky_color"] == "珊瑚红"
    assert data["data"]["record_id"]


def test_analyze_unauthorized(client):
    resp = client.post("/api/astro/analyze", json=_payload())
    assert resp.json()["code"] == 40101


def test_invalid_birth_date(client, token):
    resp = client.post("/api/astro/analyze", json=_payload(birth_date="2010-01-01"),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_invalid_gender(client, token):
    resp = client.post("/api/astro/analyze", json=_payload(gender="未知"),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_empty_focuses(client, token):
    resp = client.post("/api/astro/analyze", json=_payload(focuses=[]),
                       headers={"Authorization": "Bearer " + token})
    assert resp.json()["code"] == 40001


def test_ai_failure(client, token, monkeypatch):
    def boom(messages, **kw):
        raise RuntimeError("AI error")
    monkeypatch.setattr("app.routers.astro.chat", boom)
    resp = client.post("/api/astro/analyze", json=_payload(), headers={"Authorization": "Bearer " + token})
    data = resp.json()
    assert data["code"] == 50001
    assert data["message"] == "生成失败，请稍后重试"
