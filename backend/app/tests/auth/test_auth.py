from http import HTTPStatus

from freezegun import freeze_time
from jwt import decode
from app.core import settings
from app.core.security import create_access_token

settings = settings.Settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def test_jwt():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    result = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert result["sub"] == data["sub"]
    assert result["exp"] is not None


def test_get_token(client, user):
    response = client.post(
        "/access_token",
        data={
            "username": user.username,
            "password": user.clean_password,
        },
    )
    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_token_expired_after_time(client, user):
    with freeze_time("2023-10-01 00:00:00"):
        response = client.post(
            "/access_token",
            data={
                "username": user.username,
                "password": user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]
    with freeze_time("2023-10-01 00:31:00"):
        response = client.put(
            f"/users/{user.id}",
            json={"username": "wrong", "email": "wrong@wrong.com", "password": "wrong"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_token_inexistent_user(client):
    response = client.post(
        "/access_token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


def test_token_wrong_password(client, user):
    response = client.post(
        "/access_token",
        data={
            "username": user.username,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


def test_refresh_token(client, user):
    response = client.post(
        "/access_token",
        data={"username": user.username, "password": user.clean_password},
    )
    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    response = client.post(
        "/refresh_token",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()


def test_refresh_token_with_invalid_token(client):
    response = client.post("/refresh_token", json={"refresh_token": "invalid"})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate refresh token"}


def test_token_expired_dont_refresh(client, user):
    with freeze_time("2023-10-01 00:00:00"):
        response = client.post(
            "/access_token",
            data={
                "username": user.username,
                "password": user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        refresh_token = response.json()["refresh_token"]
    with freeze_time("2023-10-01 01:00:00"):
        response = client.post(
            "/refresh_token",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate refresh token"}

