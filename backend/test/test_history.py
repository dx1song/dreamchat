import json
import uuid

import pytest

ASTRO_REPORT = {
    "personality": "测试性格",
    "fortune": {
        "career": {"level": "★★★★☆", "desc": "x"},
        "love": {"level": "★★★☆☆", "desc": "x"},
        "health": {"level": "★★★★☆", "desc": "x"},
        "wealth": {"level": "★★★☆☆", "desc": "x"},
    },
    "lucky_color": "珊瑚红",
    "lucky_number": "7",
    "advice": ["a", "b"],
}

DREAM_REPORT = {
    "dream_keyword": "梦见蛇",
    "core_meaning": "测试",
    "interpretations": [{"focus": "事业", "content": "x"}],
    "advice": ["a", "b", "c"],
    "verdict": "好梦",
}


def _register_login(client, prefix):
    username = prefix + uuid.uuid4().hex[:8]
    client.post("/api/auth/register", json={
        "username": username, "password": "123456", "email": username + "@example.com",
    })
    resp = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    return resp.json()["data"]["token"]


@pytest.fixture
def token(client):
    return _register_login(client, "hist_")


def _h(token):
    return {"Authorization": "Bearer " + token}


def _create_records(client, token, monkeypatch):
    """mock AI，创建 1 条星座 + 1 条解梦记录，验证分析后关联当前用户落库。"""
    monkeypatch.setattr("app.routers.astro.chat", lambda m, **kw: json.dumps(ASTRO_REPORT, ensure_ascii=False))
    monkeypatch.setattr("app.routers.dream.chat", lambda m, **kw: json.dumps(DREAM_REPORT, ensure_ascii=False))
    client.post("/api/astro/analyze", json={
        "birth_date": "1995-04-05", "gender": "男", "relationship": "单身",
        "job": "工程师", "focuses": ["性格"],
    }, headers=_h(token))
    client.post("/api/dream/analyze", json={
        "dream_content": "梦见一条发光的大蛇在星空下奔跑", "dream_time": "昨晚",
        "gender": "男", "age": "26-35", "job": "教师", "focuses": ["事业"],
    }, headers=_h(token))


# ===== 列表 =====

def test_list_astro(client, token, monkeypatch):
    _create_records(client, token, monkeypatch)
    resp = client.get("/api/history?type=astro&page=1&size=20", headers=_h(token))
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["zodiac"] == "白羊座"


def test_list_dream(client, token, monkeypatch):
    _create_records(client, token, monkeypatch)
    resp = client.get("/api/history?type=dream&page=1&size=20", headers=_h(token))
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["dream_keyword"] == "梦见蛇"


def test_list_empty(client, token):
    resp = client.get("/api/history?type=astro", headers=_h(token))
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


# ===== 详情 =====

def test_detail_astro(client, token, monkeypatch):
    _create_records(client, token, monkeypatch)
    rid = client.get("/api/history?type=astro", headers=_h(token)).json()["data"]["items"][0]["id"]
    resp = client.get(f"/api/history/{rid}?type=astro", headers=_h(token))
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["type"] == "astro"
    assert data["data"]["report"]["lucky_color"] == "珊瑚红"


def test_detail_not_found(client, token):
    resp = client.get("/api/history/99999?type=astro", headers=_h(token))
    assert resp.json()["code"] == 40401


# ===== 删除 / 清空 =====

def test_delete_record(client, token, monkeypatch):
    _create_records(client, token, monkeypatch)
    rid = client.get("/api/history?type=astro", headers=_h(token)).json()["data"]["items"][0]["id"]
    resp = client.delete(f"/api/history/{rid}?type=astro", headers=_h(token))
    assert resp.json()["code"] == 0
    assert client.get("/api/history?type=astro", headers=_h(token)).json()["data"]["total"] == 0


def test_clear_all(client, token, monkeypatch):
    _create_records(client, token, monkeypatch)
    resp = client.delete("/api/history?type=dream", headers=_h(token))
    assert resp.json()["code"] == 0
    assert client.get("/api/history?type=dream", headers=_h(token)).json()["data"]["total"] == 0


# ===== 鉴权 / 校验 / 数据隔离 =====

def test_unauthorized(client):
    assert client.get("/api/history?type=astro").json()["code"] == 40101


def test_invalid_type(client, token):
    resp = client.get("/api/history?type=xxx", headers=_h(token))
    assert resp.json()["code"] == 40001


def test_data_isolation(client, monkeypatch):
    t1 = _register_login(client, "iso1_")
    t2 = _register_login(client, "iso2_")
    monkeypatch.setattr("app.routers.astro.chat", lambda m, **kw: json.dumps(ASTRO_REPORT, ensure_ascii=False))
    client.post("/api/astro/analyze", json={
        "birth_date": "1995-04-05", "gender": "男", "relationship": "单身",
        "job": "工程师", "focuses": ["性格"],
    }, headers=_h(t1))

    # 用户2查不到用户1的记录
    assert client.get("/api/history?type=astro", headers=_h(t2)).json()["data"]["total"] == 0
    # 用户2删用户1的记录 -> 404
    rid = client.get("/api/history?type=astro", headers=_h(t1)).json()["data"]["items"][0]["id"]
    resp = client.delete(f"/api/history/{rid}?type=astro", headers=_h(t2))
    assert resp.json()["code"] == 40401
