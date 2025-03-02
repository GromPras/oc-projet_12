import json
from typing import Optional
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response, validate_contract_status
from cli.views.contracts import contracts_list_view, contract_show_view
from cli.controllers.clients import list as clients_list
from cli.views.shared import message_show_view
from cli.rbac import authorize

app = typer.Typer()


@app.callback()
def authorize_commands(ctx: typer.Context):
    authorize(ctx)


@app.command()
def create(
    ctx: typer.Context,
    total_amount: Annotated[
        float,
        typer.Option("--amount", help="The contract amount", prompt=True),
    ],
    client: Annotated[
        Optional[int], typer.Option("--client", help="The client id")
    ] = None,
):
    if not client:
        ctx.invoke(clients_list)
        client = typer.prompt("Please choose a client to create the contract")
    if client is int and total_amount is float or int:
        new_contract = {"client_id": client, "total_amount": total_amount}
        token = authenticate()
        response = requests.post(
            "http://localhost:5000/contracts",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(new_contract),
        )
        data = handle_response(response)
        message_show_view({"Success": "Contract Created"})
        contract_show_view(data)


@app.command()
def list(
    status: Annotated[
        Optional[str],
        typer.Option(
            help="Option to filter the results, values are: 'pending' or 'signed'"
        ),
    ] = None,
    owing: Annotated[
        Optional[bool],
        typer.Option(
            help="Filter the results to display contracts with remaining amount"
        ),
    ] = False,
):
    active_filters = ""
    if status:
        status = validate_contract_status(status)
        active_filters += f"?status={status}"
    if owing:
        active_filters += (
            "&remaining-amount=true" if status else "?remaining-amount=true"
        )
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/contracts{active_filters}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    contracts_list_view(data)


@app.command()
def show(id: int):
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/contracts/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    contract_show_view(data)


@app.command()
def update(
    ctx: typer.Context,
    id: Annotated[
        Optional[int], typer.Option("--id", "-i", help="The contract id")
    ] = None,
    total_amount: Annotated[
        Optional[float],
        typer.Option("--amount", help="The contract amount"),
    ] = None,
    remaining_amount: Annotated[
        Optional[float],
        typer.Option("--remaining", help="The contract amount still due"),
    ] = None,
    status: Annotated[
        Optional[str], typer.Option("--status", help="The status")
    ] = None,
):
    if not id:
        ctx.invoke(list)
        id = typer.prompt("Please choose a contract to update")
    payload = {}
    payload["total_amount"] = float(total_amount) if total_amount else None
    payload["remaining_amount"] = float(remaining_amount) if remaining_amount else None
    payload["status"] = validate_contract_status(status) if status else None
    update_contract = {}
    for key in payload:
        if payload[key] is not None:
            update_contract[key] = payload[key]
    if update_contract.keys():
        token = authenticate()
        response = requests.put(
            f"http://localhost:5000/contracts/{id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(update_contract),
        )
        data = handle_response(response)
        message_show_view({"Success": "Contract Updated"})
        contract_show_view(data)


@app.command()
def delete(id: int):
    token = authenticate()
    contract = requests.get(
        f"http://localhost:5000/contracts/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(contract)
    contract_show_view(data)
    typer.confirm(
        "Do you really want to delete this contract? There is no going back.",
        abort=True,
    )
    response = requests.delete(
        f"http://localhost:5000/contracts/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    message_show_view(data)
