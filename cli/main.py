import os
from pathlib import Path

import typer

from .controllers.clients import app as clients_app
from .controllers.contracts import app as contracts_app
from .controllers.events import app as events_app
from .controllers.users import app as users_app
from .version import app as version_app

APP_NAME = "epicevent-cli"

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(clients_app, name="clients")
app.add_typer(contracts_app, name="contracts")
app.add_typer(events_app, name="events")
app.add_typer(users_app, name="users")


@app.command()
def logout():
    app_dir = typer.get_app_dir(APP_NAME)
    app_dir_path = Path(app_dir)
    app_dir_path.mkdir(parents=True, exist_ok=True)
    token_path: Path = Path(app_dir) / "token.txt"
    if token_path.is_file():
        try:
            os.remove(token_path)
            print("Logged out")
        except Exception:
            print("Error")
    else:
        print("You are not logged in")


if __name__ == "__main__":
    app()
