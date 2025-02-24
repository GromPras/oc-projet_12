import json
from typing import Optional
from email_validator.exceptions_types import EmailNotValidError
from email_validator.validate_email import validate_email
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response, sanitize_fullname
from cli.views.clients import clients_list_view, client_show_view
from cli.views.shared import message_show_view

app = typer.Typer()


@app.command()
def create(
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
    new_client = {
        "fullname": fullname,
        "email": email,
        "phone": phone,
        "company": company,
    }
    token = authenticate()
    response = requests.post(
        "http://localhost:5000/clients",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(new_client),
    )
    data = handle_response(response)
    message_show_view({"Success": "Client Created"})
    client_show_view(data)


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
def update(
    ctx: typer.Context,
    id: Annotated[
        Optional[int], typer.Option("--id", "-i", help="The client id")
    ] = None,
    fullname: Annotated[
        Optional[str],
        typer.Option("--fullname", "-n", prompt=True, help="The client full name"),
    ] = None,
    email: Annotated[
        Optional[str],
        typer.Option("--email", "-e", prompt=True, help="The client email"),
    ] = None,
    phone: Annotated[
        Optional[str],
        typer.Option("--phone", "-ph", prompt=True, help="The client phone number"),
    ] = None,
    company: Annotated[
        Optional[str],
        typer.Option("--company", "-c", prompt=True, help="The company name"),
    ] = None,
):
    if not id:
        ctx.invoke(list)
        id = typer.prompt("Please choose client to update")
    payload = {}
    payload["fullname"] = sanitize_fullname(fullname) if fullname else None
    if email:
        try:
            email_info = validate_email(
                email, check_deliverability=False, test_environment=True
            )
            payload["email"] = email_info.normalized
        except EmailNotValidError as e:
            message_show_view({"Error": "Email format is wrong", "Details": str(e)})
            raise typer.Exit()
    else:
        payload["email"] = None
    payload["phone"] = phone if phone else None
    payload["company"] = company if company else None
    update_client = {}
    for key in payload:
        if payload[key] is not None:
            update_client[key] = payload[key]
    if update_client.keys():
        token = authenticate()
        response = requests.put(
            f"http://localhost:5000/clients/{id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(update_client),
        )
        data = handle_response(response)
        message_show_view({"Success": "Client Updated"})
        client_show_view(data)
    else:
        message_show_view({"Error": "Nothing to update"})


@app.command()
def delete(id: int):
    token = authenticate()
    client = requests.get(
        f"http://localhost:5000/clients/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(client)
    client_show_view(data)
    typer.confirm(
        "Do you really want to delete this client? There is no going back.", abort=True
    )
    response = requests.delete(
        f"http://localhost:5000/clients/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    message_show_view(data)
