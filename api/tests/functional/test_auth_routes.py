import base64
import pytest
from app import create_app, db
from config import TestConfig
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


def test_get_token(client):
    username = "estaterfield0@nsw.gov.au"
    password = "test"
    response = client.post(
        "/tokens",
        headers={
            "Authorization": "Basic "
            + base64.b64encode(bytes(username + ":" + password, "ascii")).decode(
                "ascii"
            )
        },
    )
    assert response.status_code == 200
    assert response.json["token"] is not ""
