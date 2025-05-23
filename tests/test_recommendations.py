def _register(client):
    r = client.post("/register", json={
        "full_name": "User",
        "username": "u",
        "email": "u@ex.com",
        "password": "pw"
    }).json()
    return r["id"]

def test_recommendations_flow(client):
    token = _register(client)
    # отримати список товарів
    items = client.get(f"/items?token={token}").json()
    # оцінити перший елемент
    iid = items[0]["id"]
    rate = client.post(f"/rate?token={token}", json={"item_id": iid, "rating": 5})
    assert rate.status_code == 200

    recs = client.get(f"/recommendations?token={token}")
    assert recs.status_code == 200
    assert len(recs.json()) > 0
