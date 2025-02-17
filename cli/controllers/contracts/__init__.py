from typing import Optional
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response
from cli.views.contracts import contracts_list_view

app = typer.Typer()


@app.command()
def list(
    pending: Annotated[
        Optional[bool],
        typer.Option(
            help="Filter the results to display pending contracts only 'owing' to display results with remaining amount"
        ),
    ] = False,
    owing: Annotated[
        Optional[bool],
        typer.Option(
            help="Filter the results to display contracts with remaining amount"
        ),
    ] = False,
):
    active_filters = ""
    if pending:
        active_filters += "?status=pending"
    if owing:
        active_filters += (
            "&remaining-amount=true" if pending else "?remaining-amount=true"
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
    print(handle_response(response))


@app.command()
def delete(id: int):
    token = authenticate()
    response = requests.delete(
        f"http://localhost:5000/contracts/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(handle_response(response))
