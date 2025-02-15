import base64
import json
import pytest
import sqlalchemy as sa
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


def test_show_client(client):
    token = get_token(client, "support")
    response = client.get("/clients/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    json_client = response.json
    assert json_client.get("fullname") == "Gilburt Scarf"
    assert json_client.get("email") == "gscarf0@tuttocitta.it"
    assert json_client.get("phone") == "6195732158"
    assert json_client.get("company") == "Schulist-Hayes"
    assert json_client.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }


def test_show_client_unauth(client):
    response = client.get("/clients/1", headers={"Authorization": f"Bearer test"})
    assert response.status_code == 401


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
def test_update_client_by_author(client):
    token = get_token(client, "sales")
    updated_client = {
        "fullname": "Test update",
    }
    response = client.put(
        "/clients/1",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(updated_client),
        content_type="application/json",
    )
    assert response.status_code == 200
    client = db.session.scalar(
        sa.select(Client).where(Client.id == 1).join(Client.sales_contact)
    )
    assert client.fullname == "Test update"


def test_update_client_unauthorize(client):
    token = get_token(client, "sales")
    updated_client = {
        "fullname": "Test update",
    }
    response = client.put(
        "/clients/2",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(updated_client),
        content_type="application/json",
    )
    assert response.status_code == 403
    client = db.session.scalar(
        sa.select(Client).where(Client.id == 2).join(Client.sales_contact)
    )
    assert client.fullname == "Rebeka Asken"


# destroy [auth, author]
def test_destroy_client(client):
    token = get_token(client, "sales")
    response = client.delete("/clients/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    clients = db.session.scalars(sa.select(Client)).all()
    assert len(clients) == 4


def test_destroy_client_unauthorized(client):
    token = get_token(client, "sales")
    response = client.delete("/clients/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    clients = db.session.scalars(sa.select(Client)).all()
    assert len(clients) == 5
