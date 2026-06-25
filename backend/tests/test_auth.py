def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "pw12345"})
    assert r.status_code == 201
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "pw12345"})
    assert r.status_code == 200 and "access_token" in r.json()


def test_duplicate_email(client):
    client.post("/auth/register", json={"email": "x@y.com", "password": "pw12345"})
    r = client.post("/auth/register", json={"email": "x@y.com", "password": "pw12345"})
    assert r.status_code == 409


def test_bad_login(client):
    r = client.post("/auth/login", json={"email": "no@one.com", "password": "nope1234"})
    assert r.status_code == 401
