from http import HTTPStatus
from app.schemas.user_schema import UserPublicSchema


def test_create_user(client):
    response = client.post(
        "/api/signup",
        json={
            "username": "testusername",
            "email": "testemail@test.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "testusername",
        "email": "testemail@test.com",
    }


def test_create_user_with_existing_username(client, user):
    response = client.post(
        "/api/signup",
        json={
            "username": user.username,
            "email": user.email,
            "password": "newpassword",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "User with this username already exists."}


def test_create_user_with_existing_email(client, user):
    response = client.post(
        "/api/signup",
        json={
            "username": "newusername",
            "email": user.email,
            "password": "newpassword",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "User with this email already exists."}


def test_get_users(client, user):
    user_schema = UserPublicSchema.model_validate(user)
    response = client.get("/api/users")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema.model_dump(mode="json")]}


def test_update_user(client, user, token):
    response = client.put(
        f"/api/users/{user.id}",
        json={"username": "updatedusername", "email": "newemail@test.com", "password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": user.id, "username": "updatedusername", "email": "newemail@test.com"}


def test_update_user_with_existing_username(client, user, another_user, token):
    response = client.put(
        f"/api/users/{user.id}",
        json={"username": user.username, "email": another_user.email, "password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "User with this username already exists."}


def test_update_user_with_existing_email(client, user, another_user, token):
    response = client.put(
        f"/api/users/{user.id}",
        json={"username": "newusername", "email": user.email, "password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "User with this email already exists."}


def test_update_user_with_wrong_user(client, another_user, token):
    response = client.put(
        f"/api/users/{another_user.id}",
        json={"username": "updatedusername", "email": "email@example.com", "password": "mynewpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not allowed to update this user."}


def test_delete_user(client, user, token):
    response = client.delete(f"/api/users/{user.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_with_wrong_user(client, another_user, token):
    response = client.delete(f"/api/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not allowed to delete this user."}
