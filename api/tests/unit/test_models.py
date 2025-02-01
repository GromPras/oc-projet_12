import pytest
from app import create_app
from app.models import User, Role


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
