from typer.testing import CliRunner

from .main import app

runner = CliRunner()


def test_user_list():
    result = runner.invoke(app, ["users", "list"], input="testadmin@test.com\ntest")
    assert result.exit_code == 0
    assert "Users" in result.stdout


def test_clients_list():
    result = runner.invoke(app, ["clients", "list"], input="testadmin@test.com\ntest")
    assert result.exit_code == 0
    assert "Clients" in result.stdout


def test_contracts_list():
    result = runner.invoke(app, ["contracts", "list"], input="testadmin@test.com\ntest")
    assert result.exit_code == 0
    assert "Contracts" in result.stdout


def test_contracts_list_with_filters():
    result = runner.invoke(
        app, ["contracts", "list" "--pending"], input="testadmin@test.com\ntest"
    )
    assert result.exit_code == 0
    assert "Contracts" in result.stdout
    result = runner.invoke(
        app, ["contracts", "list" "--owing"], input="testadmin@test.com\ntest"
    )
    assert result.exit_code == 0
    assert "Contracts" in result.stdout


def test_events_list():
    result = runner.invoke(app, ["events", "list"], input="testadmin@test.com\ntest")
    assert result.exit_code == 0
    assert "Events" in result.stdout
