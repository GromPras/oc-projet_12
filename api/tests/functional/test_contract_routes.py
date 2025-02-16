import base64
import json
import pytest
import sqlalchemy as sa
from config import TestConfig
from app import create_app, db
from app.models import User, Client, Event, Contract, Role, ContractStatus
from mock import (
    users as mock_users,
    clients as mock_clients,
    contracts as mock_contracts,
)


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
        for contract in mock_contracts:
            db.session.add(
                Contract(
                    client_id=contract[0],
                    sales_contact_id=contract[1],
                    total_amount=contract[2],
                    remaining_amount=contract[3],
                    status=contract[4],
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


# Contract views


# index [auth]
# TODO: test contract_list with events
def test_contracts_list(client):
    token = get_token(client, "sales")
    response = client.get("/contracts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 5


def test_contract_show(client):
    token = get_token(client, "sales")
    response = client.get("/contracts/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    json_contract = response.json
    client = json_contract.get("client")
    assert client["id"] == 1
    assert json_contract.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }
    assert json_contract.get("total_amount") == 4432.93
    assert json_contract.get("remaining_amount") == 1486.28
    assert json_contract.get("status") == ContractStatus.SIGNED.value


# create [auth, admin]
def test_contract_create(client):
    token = get_token(client, "admin")
    new_contract = {
        "client_id": 1,
        "sales_contact_id": 1,
        "total_amount": 999.99,
    }
    response = client.post(
        "/contracts",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(new_contract),
        content_type="application/json",
    )
    assert response.status_code == 201
    json_contract = response.json
    assert json_contract.get("remaining_amount") == 999.99
    assert json_contract.get("status") == ContractStatus.PENDING.value
    assert json_contract["client"].get("fullname") == "Gilburt Scarf"
    assert json_contract["client"].get("email") == "gscarf0@tuttocitta.it"
    assert json_contract["client"].get("phone") == "6195732158"
    assert json_contract["client"].get("company") == "Schulist-Hayes"
    assert json_contract.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }


# update [auth, admin]
def test_update_contract(client):
    token = get_token(client, "admin")
    update_contract = {"status": "signed"}
    response = client.put(
        "/contracts/3",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(update_contract),
        content_type="application/json",
    )

    assert response.status_code == 200
    json_contract = response.json
    assert json_contract.get("status") == ContractStatus.SIGNED.value
    assert json_contract["client"].get("fullname") == "Gilburt Scarf"
    assert json_contract["client"].get("email") == "gscarf0@tuttocitta.it"
    assert json_contract["client"].get("phone") == "6195732158"
    assert json_contract["client"].get("company") == "Schulist-Hayes"
    assert json_contract.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }


def test_update_contract_amount(client):
    token = get_token(client, "admin")
    update_contract = {"remaining_amount": 0}
    response = client.put(
        "/contracts/3",
        headers={"Authorization": f"Bearer {token}"},
        data=json.dumps(update_contract),
        content_type="application/json",
    )

    assert response.status_code == 200
    json_contract = response.json
    assert json_contract.get("total_amount") == 1603.67
    assert json_contract.get("remaining_amount") == 0.0
    assert json_contract["client"].get("fullname") == "Gilburt Scarf"
    assert json_contract["client"].get("email") == "gscarf0@tuttocitta.it"
    assert json_contract["client"].get("phone") == "6195732158"
    assert json_contract["client"].get("company") == "Schulist-Hayes"
    assert json_contract.get("sales_contact") == {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    }


# destroy [auth, author]


# Event views

# index [auth]
# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
