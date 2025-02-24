from typing import Optional
from email_validator.exceptions_types import EmailNotValidError
from email_validator.validate_email import validate_email
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response, sanitize_fullname
from cli.views.clients import clients_list_view
from cli.views.shared import message_show_view
from cli.controllers.users import list as users_list

app = typer.Typer()


@app.command()
def create(
    ctx: typer.Context,
    fullname: Annotated[
        str, typer.Option("--fullname", "-n", prompt=True, help="The client full name")
    ],
    email: Annotated[
        str, typer.Option("--email", "-e", prompt=True, help="The client email")
    ],
    phone: Annotated[
        str, typer.Option("--phone", "-ph", prompt=True, help="The client phone number")
    ],
    company: Annotated[
        str, typer.Option("--company", "-c", prompt=True, help="The company name")
    ],
    sales_contact: Annotated[
        Optional[int],
        typer.Option(
            "--sales-contact",
            "-s",
            help="The id of the client's sales representant",
        ),
    ] = None,
):
    fullname = sanitize_fullname(fullname)
    try:
        email_info = validate_email(
            email, check_deliverability=False, test_environment=True
        )
        email = email_info.normalized
    except EmailNotValidError as e:
        message_show_view({"Error": "Email format is wrong", "Details": str(e)})
        raise typer.Exit()
    authenticate()
    if not sales_contact:
        ctx.invoke(users_list)
        sales_contact = typer.prompt("Select a sales representant")
    print(sales_contact)
    print("Creating Client")


@app.command()
def list():
    token = authenticate()
    response = requests.get(
        "http://localhost:5000/clients", headers={"Authorization": f"Bearer {token}"}
    )
    data = handle_response(response)
    clients_list_view(data)


@app.command()
def show(id: int):
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/clients/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(handle_response(response))


@app.command()
def delete(id: int):
    token = authenticate()
    response = requests.delete(
        f"http://localhost:5000/clients/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(handle_response(response))
