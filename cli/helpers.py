from pathlib import Path
import html
import requests
import typer
from .views.shared import message_show_view

APP_NAME = "epicevent-cli"
app_dir = typer.get_app_dir(APP_NAME)
app_dir_path = Path(app_dir)
app_dir_path.mkdir(parents=True, exist_ok=True)
token_path: Path = Path(app_dir) / "token.txt"


def log_user_in():
    token = None
    print("Log in:")
    username = typer.prompt("Username (email)")
    password = typer.prompt("Password", hide_input=True)

    response = requests.post("http://localhost:5000/tokens", auth=(username, password))
    if response.status_code == 200:
        token = response.json()["token"]
        with open(token_path, "w") as file:
            file.write(token)
        print("Logged in")

    return token


def authenticate():
    token = None
    if token_path.is_file():
        with open(token_path, "r") as file:
            token = file.read()
    else:
        token = log_user_in()

    return token


def handle_response(response):
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    elif response.status_code == 400:
        message_show_view({"Error": "Bad request"})
        raise typer.Exit()
    elif response.status_code == 401:
        message_show_view({"Error": "You don't have access"})
        raise typer.Exit()
    elif response.status_code == 403:
        message_show_view({"Error": "You are not authorized"})
        raise typer.Exit()
    elif response.status_code == 404:
        message_show_view({"Error": "Not Found"})
        raise typer.Exit()
    else:
        message_show_view({"Error": "Contact support"})
        raise typer.Exit()


def format_phone(phone: str):
    return f"{phone[:2]}-{phone[2:4]}-{phone[4:6]}-{phone[6:8]}-{phone[8:]}"


def sanitize_fullname(fullname: str):
    return html.escape(fullname).strip().title()


def validate_role(department: str):
    valid_roles = ["admin", "sales", "support"]
    dept = department.lower().strip()
    if dept not in valid_roles:
        message_show_view(
            {
                "Error": "Unknown department. Valid values are: 'admin', 'sales' and 'support'"
            }
        )
        raise typer.Exit()
    return dept


def validate_contract_status(status: str):
    valid_status = ["pending", "signed"]
    status = status.lower().strip()
    if status not in valid_status:
        message_show_view(
            {"Error": "Unknown status. Valid values are: 'pending' or 'signed'"}
        )
        raise typer.Exit()
    return status
