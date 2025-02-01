import pytest
from app import create_app
from app.models import User, Client


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


def test_new_user():
    user = User(fullname='Billy', email='billy@test.com', phone='+336123456789', role='sales', password='test')
    assert user.email == 'billy@test.com'
    assert user.role is not None
    assert user.role == 'sales'


def test_new_client():
    user = User(fullname='Billy', email='billy@test.com', phone='+336123456789', role='sales', password='test')
    client = Client(fullname='Joe', email='joe@test.com', phone='+33123456789', company='Test inc', sales_contact=user)
    assert client.fullname == 'Joe'
    assert client.sales_contact.role == 'sales'
