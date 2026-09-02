def test_create_task(client):
    client.post(
        "/auth/reg",
        json={
            "email": "taskuser@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "taskuser@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Learn FastAPI",
            "description": "Build a production-ready backend"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Build a production-ready backend"
    assert "id" in data

def test_get_all_tasks(client):
    client.post(
        "/auth/reg",
        json={
            "email": "gettasks@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "gettasks@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Testing task retrieval"
        }
    )

    response = client.get(
        "/task/all_tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"]
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Test Task"

def test_get_tasks_without_token(client):
    response = client.get("/task/all_tasks")

    assert response.status_code == 401

def test_user_cannot_access_another_users_task(client):
    # Create User A
    client.post(
        "/auth/reg",
        json={
            "email": "usera@example.com",
            "password": "password123"
        }
    )

    # Login User A
    login_a = client.post(
        "/auth/login",
        data={
            "username": "usera@example.com",
            "password": "password123"
        }
    )

    token_a = login_a.json()["access_token"]

    # User A creates a task
    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json={
            "title": "Private Task",
            "description": "Only User A should access this"
        }
    )

    task_id = task_response.json()["id"]

    # Create User B
    client.post(
        "/auth/reg",
        json={
            "email": "userb@example.com",
            "password": "password123"
        }
    )

    # Login User B
    login_b = client.post(
        "/auth/login",
        data={
            "username": "userb@example.com",
            "password": "password123"
        }
    )

    token_b = login_b.json()["access_token"]

    # User B tries to access User A's task
    response = client.get(
        f"/task/{task_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_user_cannot_update_another_users_task(client):
    # User A
    client.post(
        "/auth/reg",
        json={
            "email": "updatea@example.com",
            "password": "password123"
        }
    )

    login_a = client.post(
        "/auth/login",
        data={
            "username": "updatea@example.com",
            "password": "password123"
        }
    )

    token_a = login_a.json()["access_token"]

    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json={
            "title": "Original Title",
            "description": "Original description"
        }
    )

    task_id = task_response.json()["id"]

    # User B
    client.post(
        "/auth/reg",
        json={
            "email": "updateb@example.com",
            "password": "password123"
        }
    )

    login_b = client.post(
        "/auth/login",
        data={
            "username": "updateb@example.com",
            "password": "password123"
        }
    )

    token_b = login_b.json()["access_token"]

    # User B attempts to update User A's task
    response = client.patch(
        f"/task/{task_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        },
        json={
            "title": "Hacked Title"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_user_cannot_delete_another_users_task(client):
    # User A
    client.post(
        "/auth/reg",
        json={
            "email": "deletea@example.com",
            "password": "password123"
        }
    )

    login_a = client.post(
        "/auth/login",
        data={
            "username": "deletea@example.com",
            "password": "password123"
        }
    )

    token_a = login_a.json()["access_token"]

    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token_a}"
        },
        json={
            "title": "Protected Task",
            "description": "User B must not delete this"
        }
    )

    task_id = task_response.json()["id"]

    # User B
    client.post(
        "/auth/reg",
        json={
            "email": "deleteb@example.com",
            "password": "password123"
        }
    )

    login_b = client.post(
        "/auth/login",
        data={
            "username": "deleteb@example.com",
            "password": "password123"
        }
    )

    token_b = login_b.json()["access_token"]

    # User B attempts to delete User A's task
    response = client.delete(
        f"/task/delete/{task_id}",
        headers={
            "Authorization": f"Bearer {token_b}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_update_task(client):
    client.post(
        "/auth/reg",
        json={
            "email": "update@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "update@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Old Title",
            "description": "Old description"
        }
    )

    task_id = task_response.json()["id"]

    response = client.patch(
        f"/task/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "New Title",
            "description": "New description"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Title"
    assert data["description"] == "New description"

def test_delete_task(client):
    client.post(
        "/auth/reg",
        json={
            "email": "delete@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "delete@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Task To Delete",
            "description": "This task should disappear"
        }
    )

    task_id = task_response.json()["id"]

    response = client.delete(
        f"/task/delete/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Task deleted successfully"
    assert data["task_id"] == task_id

def test_register_weak_password(client):
    response = client.post(
        "/auth/reg",
        json={
            "email": "weak@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["msg"] == "Value error, Password must be at least 8 characters"

def test_register_invalid_email(client):
    response = client.post(
        "/auth/reg",
        json={
            "email": "not-an-email",
            "password": "password123"
        }
    )

    assert response.status_code == 422

def test_update_task_without_fields(client):
    client.post(
        "/auth/reg",
        json={
            "email": "emptyupdate@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "emptyupdate@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    task_response = client.post(
        "/task/create_task",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Testing empty update"
        }
    )

    task_id = task_response.json()["id"]

    response = client.patch(
        f"/task/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={}
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "No fields provided for update"

def test_invalid_token(client):
    response = client.get(
        "/task/all_tasks",
        headers={
            "Authorization": "Bearer this-is-not-a-real-token"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid or expired token"