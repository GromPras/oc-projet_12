import base64
import json
import pytest
from config import TestConfig
from app import create_app, db
from app.models import User, Client, Event, Contract, Role
from mock import users as mock_users, clients as mock_clients


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
        for client in mock_clients:
            db.session.add(
                Client(
                    fullname=client[0],
                    email=client[1],
                    phone=client[2],
                    company=client[3],
                    sales_contact_id=client[4],
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


# Client routes


# index [auth]
def test_list_clients_unauthenticated(client):
    response = client.get("/clients")
    assert response.status_code == 401


def test_list_clients(client):
    token = get_token(client, "sales")
    response = client.get("/clients", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 5


# create [auth, sales]
def test_create_client_with_authorization(client):
    token = get_token(client, "sales")
    new_client = {
        "fullname": "Test User",
        "email": "test@test.com",
        "phone": "0123456789",
        "company": "Test company",
    }
    response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(new_client),
        content_type="application/json",
    )
    assert response.status_code == 201
    json_client = response.json
    assert json_client.get("fullname") == "Test User"
    assert json_client.get("email") == "test@test.com"
    assert json_client.get("phone") == "0123456789"
    assert json_client.get("company") == "Test company"
    assert json_client.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }


def test_create_client_without_authorization(client):
    token = get_token(client, "admin")
    new_client = {
        "fullname": "Test User",
        "email": "test@test.com",
        "phone": "0123456789",
        "company": "Test company",
    }
    response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(new_client),
        content_type="application/json",
    )
    assert response.status_code == 403


# update [auth, author]
# destroy [auth, author]


# Contract views

# index [auth]
# create [auth, admin]
# update [auth, admin]
# destroy [auth, author]


# Event views

# index [auth]
# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
