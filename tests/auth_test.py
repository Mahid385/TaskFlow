def test_register_user(client):
    response = client.post(
        "/auth/reg",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "user_id" in data
    assert data["user_email"] == "test@example.com"

def test_register_duplicate_email(client):
    client.post(
        "/auth/reg",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/reg",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == "Email already registered"

def test_login_success(client):
    client.post(
        "/auth/reg",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/auth/reg",
        json={
            "email": "wrongpass@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Incorrect email or password"