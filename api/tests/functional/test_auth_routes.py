import base64
import pytest
from app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


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
    assert {"token": ""} == response.json
