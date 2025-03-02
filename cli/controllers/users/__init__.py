import json
import typer
import requests
from cli.helpers import authenticate, handle_response, sanitize_fullname, validate_role
from cli.views.users import users_list_view, user_show_view
from cli.views.shared import message_show_view
from email_validator import validate_email, EmailNotValidError
from typing import Optional
from typing_extensions import Annotated
from cli.rbac import authorize

app = typer.Typer()


@app.callback()
def authorize_commands(ctx: typer.Context):
    authorize(ctx)


@app.command()
def create(
    fullname: Annotated[
        str, typer.Option("--fullname", "-n", prompt=True, help="The user full name")
    ],
    email: Annotated[
        str, typer.Option("--email", "-e", prompt=True, help="The user email")
    ],
    phone: Annotated[
        str, typer.Option("--phone", "-ph", prompt=True, help="The user phone number")
    ],
    department: Annotated[
        str,
        typer.Option(
            "--department",
            "-d",
            prompt="Choose a department",
            help="The user department. Valid options are 'admin', 'sales' or 'support'",
        ),
    ],
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            prompt=True,
            help="The user password",
            confirmation_prompt=True,
            hide_input=True,
        ),
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
    department = validate_role(department)
    new_user = {
        "fullname": fullname,
        "email": email,
        "phone": phone,
        "role": department,
        "password": password,
    }
    token = authenticate()
    response = requests.post(
        "http://localhost:5000/users",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(new_user),
    )
    data = handle_response(response)
    message_show_view({"Success": "User Created"})
    user_show_view(data)


@app.command()
def list(
    department: Annotated[
        Optional[str],
        typer.Option(
            help="Optionally give a department to filter results. Options are 'admin', 'sales' or 'support'"
        ),
    ] = None,
):
    active_filters = ""
    if department:
        dept = validate_role(department)
        active_filters += f"?dept={dept}"

    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/users{active_filters}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    users_list_view(data)


@app.command()
def show(id: Annotated[int, typer.Argument()]):
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/users/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    user_show_view(data)


@app.command()
def update(
    id: Annotated[int, typer.Option("--id", "-i", prompt=True, help="The user id")],
    fullname: Annotated[
        Optional[str],
        typer.Option("--fullname", "-n", help="The user full name to update"),
    ] = None,
    email: Annotated[
        Optional[str], typer.Option("--email", "-e", help="The user email to update")
    ] = None,
    phone: Annotated[
        Optional[str],
        typer.Option("--phone", "-ph", help="The user phone number to update"),
    ] = None,
    department: Annotated[
        Optional[str],
        typer.Option(
            "--department",
            "-d",
            help="The user department. Valid options are 'admin', 'sales' or 'support'",
        ),
    ] = None,
    password: Annotated[
        Optional[str],
        typer.Option(
            "--password",
            "-p",
            help="The user password to update",
            confirmation_prompt=True,
            hide_input=True,
        ),
    ] = None,
):
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
    payload["role"] = validate_role(department) if department else None
    payload["phone"] = phone if phone else None
    payload["password"] = password if password else None
    update_user = {}
    for key in payload:
        if payload[key] is not None:
            update_user[key] = payload[key]
    if update_user.keys():
        token = authenticate()
        response = requests.put(
            f"http://localhost:5000/users/{id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(update_user),
        )
        data = handle_response(response)
        message_show_view({"Success": "User Updated"})
        user_show_view(data)
    else:
        message_show_view({"Error": "Nothing to update"})


@app.command()
def delete(id: Annotated[int, typer.Argument()]):
    token = authenticate()
    user = requests.get(
        f"http://localhost:5000/users/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(user)
    user_show_view(data)
    typer.confirm(
        "Do you really want to delete this user? There is no going back", abort=True
    )
    response = requests.delete(
        f"http://localhost:5000/users/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    message_show_view(data)
