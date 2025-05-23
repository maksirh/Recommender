def test_register_and_login(client):
    reg = client.post("/register", json={
        "full_name": "Tester",
        "username": "tester",
        "email": "t@example.com",
        "password": "123456"
    })
    assert reg.status_code == 200
    uid = reg.json()["id"]

    login = client.post("/login", json={
        "email": "t@example.com",
        "password": "123456"
    })
    assert login.status_code == 200
    assert login.json()["token"] == uid
