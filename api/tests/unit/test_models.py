from datetime import datetime, timedelta
import pytest
from app import create_app
from app.models import User, Client, Contract, Event, Role, ContractStatus


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


def test_new_user():
    user = User(
        fullname="Billy",
        email="billy@test.com",
        phone="+336123456789",
        role=Role.SALES,
        password="test",
    )
    assert user.email == "billy@test.com"
    assert user.role is not None
    assert user.role == Role.SALES


def test_new_client():
    user = User(
        fullname="Billy",
        email="billy@test.com",
        phone="+336123456789",
        role=Role.SALES,
        password="test",
    )
    client = Client(
        fullname="Joe",
        email="joe@test.com",
        phone="+33123456789",
        company="Test inc",
        sales_contact=user,
    )
    assert client.fullname == "Joe"
    assert client.sales_contact.role == Role.SALES


def test_new_contract():
    user = User(
        fullname="Billy",
        email="billy@test.com",
        phone="+336123456789",
        role=Role.SALES,
        password="test",
    )
    client = Client(
        fullname="Joe",
        email="joe@test.com",
        phone="+33123456789",
        company="Test inc",
        sales_contact=user,
    )
    contract = Contract(
        client=client, sales_contact=client.sales_contact, total_amount=1234.56
    )
    assert contract.remaining_amount == 1234.56
    assert contract.status == ContractStatus.PENDING


def test_new_event():
    user = User(
        fullname="Billy",
        email="billy@test.com",
        phone="+336123456789",
        role=Role.SALES,
        password="test",
    )
    support = User(
        fullname="Jimbob",
        email="jimbob@test.com",
        phone="+336123456789",
        role=Role.SUPPORT,
        password="test",
    )
    client = Client(
        fullname="Joe",
        email="joe@test.com",
        phone="+33123456789",
        company="Test inc",
        sales_contact=user,
    )
    contract = Contract(
        client=client, sales_contact=client.sales_contact, total_amount=1234.56
    )
    event = Event(
        title="My event",
        contract=contract,
        client=client,
        sales_contact=client.sales_contact,
        support_contact=support,
        event_start=datetime.today(),
        event_end=datetime.today() + timedelta(5),
        location="Cool venue",
        attendees=99,
        notes="Lorem Ipsum",
    )
    assert event.contract.client == event.client
    assert event.client.fullname == "Joe"
    assert event.sales_contact.fullname == "Billy"
    assert event.sales_contact.role == Role.SALES
    assert event.support_contact.fullname == "Jimbob"
    assert event.support_contact.role == Role.SUPPORT
