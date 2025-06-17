from fastapi import status
from sqlmodel import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def test_create_user(client, test_db):
    user_data = {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "testpassword123",
        "role": "user"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    assert "password" not in data

def test_get_user(client, test_user, user_token_headers):
    response = client.get(f"/api/v1/users/{test_user.id}", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["role"] == test_user.role

def test_get_user_unauthorized(client, test_user):
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user(client, test_user, user_token_headers):
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com"
    }
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]

def test_delete_user(client, test_user, admin_token_headers):
    response = client.delete(
        f"/api/v1/users/{test_user.id}",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_users(client, admin_token_headers):
    response = client.get("/api/v1/users/", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_list_users_unauthorized(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 