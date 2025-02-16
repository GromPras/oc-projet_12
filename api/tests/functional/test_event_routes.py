import base64
import pytest
import sqlalchemy as sa
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
# create [auth, sales] => must be client_author && contract_status == 'signed'
# update [auth, admin, event_contact_support]
# destroy [auth, author]
