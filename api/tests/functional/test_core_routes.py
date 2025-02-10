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
def test_unauthenticated_list_users(client):
    response = client.get("/users")
    assert response.status_code == 401
    # assert {
    #     "id": 1,
    #     "fullname": "Elladine Staterfield",
    #     "email": "estaterfield0@nsw.gov.au",
    #     "phone": "1301924404",
    #     "role": "sales",
    # } in response.json
    # assert {
    #     "password": "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433"
    # } not in response.json


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
