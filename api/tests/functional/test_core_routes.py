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


# User routes


# index [auth, admin]
def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert {
        "id": 1,
        "fullname": "Elladine Staterfield",
        "email": "estaterfield0@nsw.gov.au",
        "phone": "1301924404",
        "role": "sales",
    } in response.json
    assert {
        "password": "$2a$04$3lpNcHoe2iAt9dv5OsYLKuwvc1WzrDuzPRYV8zLbuMojXTVTkrHUS"
    } not in response.json


# create [auth, admin]
# update [auth, admin]
# destroy [auth, admin]


# Client views

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
