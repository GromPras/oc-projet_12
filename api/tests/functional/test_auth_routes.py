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
    response = client.post(
        "/tokens",
        data={
            "username": "estaterfield0@nsw.gov.au",
            "password": "$2a$04$3lpNcHoe2iAt9dv5OsYLKuwvc1WzrDuzPRYV8zLbuMojXTVTkrHUS",
        },
    )
    assert response.status_code == 200
    assert {"token": ""} in response.json
