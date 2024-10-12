# tests/test_routes.py
def test_create_user(client):
    response = client.post('/api/users', json={
        "username": "salif",
        "email": "salif@example.com",
        "password": "salif123"
    })
    assert response.status_code == 201
    assert response.json["username"] == "salif"

def test_login_user(client):
    # Créer un utilisateur
    client.post('/api/users', json={
        "username": "salif",
        "email": "salif@example.com",
        "password": "salif123"
    })

    # Essayer de se connecter
    response = client.post('/api/login', json={
        "email": "salif@example.com",
        "password": "salif123"
    })
    assert response.status_code == 200
    assert "token" in response.json
