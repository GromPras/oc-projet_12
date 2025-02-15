import base64
import json
import pytest
from config import TestConfig
from app import create_app, db
from app.models import User, Client, Event, Contract, Role


@pytest.fixture()
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()
        mock_users = [
            [
                "Elladine Staterfield",
                "estaterfield0@nsw.gov.au",
                "1301924404",
                Role.SALES,
                "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
            ],
            [
                "Gare Wealthall",
                "gwealthall1@indiegogo.com",
                "1072455114",
                Role.SUPPORT,
                "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
            ],
            [
                "Querida Santer",
                "qsanterh@plala.or.jp",
                "4715820827",
                Role.ADMIN,
                "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
            ],
        ]
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


# Client routes

# index [auth]
# create [auth, sales]
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
