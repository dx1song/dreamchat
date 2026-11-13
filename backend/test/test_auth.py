import uuid


def _rand(prefix="u"):
    return prefix + uuid.uuid4().hex[:8]


def _register(client, username, password="123456", email=None):
    email = email or username + "@example.com"
    return client.post("/api/auth/register", json={
        "username": username,
        "password": password,
        "email": email,
    })


# ===== 注册 =====

def test_register_success(client):
    username = _rand()
    resp = _register(client, username)
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["username"] == username


def test_register_duplicate_username(client):
    username = _rand()
    _register(client, username)
    resp = _register(client, username, email=username + "2@example.com")
    data = resp.json()
    assert data["code"] == 40001
    assert data["message"] == "用户名已存在"


def test_register_duplicate_email(client):
    email = _rand("e") + "@example.com"
    _register(client, _rand(), email=email)
    resp = _register(client, _rand(), email=email)
    data = resp.json()
    assert data["code"] == 40001
    assert data["message"] == "邮箱已被注册"


def test_register_invalid_username(client):
    resp = _register(client, "ab", email="x@example.com")
    data = resp.json()
    assert data["code"] == 40001
    assert "用户名" in data["message"]


def test_register_password_too_short(client):
    resp = _register(client, _rand(), password="123", email="x@example.com")
    data = resp.json()
    assert data["code"] == 40001
    assert "密码" in data["message"]


def test_register_invalid_email(client):
    resp = _register(client, _rand(), email="invalid-email")
    data = resp.json()
    assert data["code"] == 40001
    assert "邮箱" in data["message"]


# ===== 登录 =====

def test_login_success(client):
    username = _rand()
    _register(client, username)
    resp = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["token"]
    assert data["data"]["token_type"] == "Bearer"


def test_login_wrong_password(client):
    username = _rand()
    _register(client, username)
    resp = client.post("/api/auth/login", json={"username": username, "password": "wrongpass"})
    data = resp.json()
    assert data["code"] == 40102
    assert data["message"] == "用户名或密码错误"


def test_login_empty_username(client):
    resp = client.post("/api/auth/login", json={"username": "", "password": "123456"})
    data = resp.json()
    assert data["code"] == 40001
    assert data["message"] == "用户名不能为空"


def test_login_remember_me(client):
    username = _rand()
    _register(client, username)
    resp = client.post("/api/auth/login", json={"username": username, "password": "123456", "remember_me": True})
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["token"]
