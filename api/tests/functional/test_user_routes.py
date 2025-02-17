import base64
import json
import pytest
from werkzeug.security import check_password_hash
from config import TestConfig
from app import create_app, db
from app.models import User
from mock import users as mock_users


@pytest.fixture()
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()
        for user in mock_users:
            db.session.add(
                User(
                    fullname=user[0],
                    email=user[1],
                    phone=user[2],
                    role=user[3],
                    password=user[4],
                )
            )
            db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


def get_token(client, role):
    username = None
    password = "test"
    if role == "admin":
        username = "qsanterh@plala.or.jp"
    if role == "sales":
        username = "estaterfield0@nsw.gov.au"
    if role == "support":
        username = "gwealthall1@indiegogo.com"
    if username is not None:
        response = client.post(
            "/tokens",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(bytes(username + ":" + password, "ascii")).decode(
                    "ascii"
                )
            },
        )
        return response.json["token"]


# User routes


# index [auth, admin]
def test_unauthenticated_list_users(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_authenticated_list_users_without_authorization(client):
    token = get_token(client, "sales")
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    token = get_token(client, "support")
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_authenticated_list_users(client):
    token = get_token(client, "admin")
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    } in response.json
    assert {
        "password": "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433"
    } not in response.json


def test_authenticated_show_user(client):
    token = get_token(client, "admin")
    response = client.get("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    } == response.json


# create [auth, admin]
def test_authenticated_create_user(client):
    token = get_token(client, "admin")
    new_user = {
        "fullname": "Test User",
        "email": "test@test.com",
        "phone": "0123456789",
        "role": "SALES",
        "password": "test",
    }
    response = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(new_user),
        content_type="application/json",
    )
    assert response.status_code == 201
    new_user_data = {
        "id": 6,
        "fullname": "Test User",
        "email": "test@test.com",
        "phone": "0123456789",
        "role": "sales",
    }
    assert new_user_data == response.json


# update [auth, admin]
def test_authorize_update_user(client):
    token = get_token(client, "admin")
    update_user = {"fullname": "test update"}
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(update_user),
        content_type="application/json",
    )
    assert response.status_code == 200
    json_user = response.json
    assert json_user.get("fullname") == "test update"


def test_update_user_password(client):
    token = get_token(client, "admin")
    new_user = {
        "fullname": "Test User",
        "email": "test@test.com",
        "phone": "0123456789",
        "role": "SALES",
        "password": "testnewpassword",
    }
    response = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(new_user),
        content_type="application/json",
    )
    update_user = {"password": "test"}
    response = client.put(
        "/users/6",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(update_user),
        content_type="application/json",
    )
    assert response.status_code == 200
    updated_user = db.get_or_404(User, 6)
    print(updated_user.check_password("test"))
    assert updated_user.check_password("test") == True


# destroy [auth, admin]
def test_authorize_destroy_user(client):
    token = get_token(client, "admin")
    response = client.delete("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response = response.json
    assert response.get("message") == "User removed"
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert len(response.json) == 4
