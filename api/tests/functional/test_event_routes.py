import base64
import pytest
import sqlalchemy as sa
from datetime import datetime
from config import TestConfig
from app import create_app, db
from app.models import User, Client, Event, Contract, Role, ContractStatus
from mock import (
    users as mock_users,
    clients as mock_clients,
    contracts as mock_contracts,
    events as mock_events,
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
        date_format = "%Y-%m-%d %H:%M:%S"
        for event in mock_events:
            db.session.add(
                Event(
                    title=event[0],
                    contract_id=event[1],
                    client_id=event[2],
                    sales_contact_id=event[3],
                    support_contact_id=event[4],
                    event_start=datetime.strptime(event[5], date_format),
                    event_end=datetime.strptime(event[6], date_format),
                    location=event[7],
                    attendees=event[8],
                    notes=event[9],
                )
            )
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


# Event views


# index [auth]
def test_event_index(client):
    token = get_token(client, "support")
    response = client.get("/events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 3


# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
