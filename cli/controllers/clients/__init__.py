import typer
import requests
import typer
from cli.helpers import authenticate, handle_response
from cli.views.clients import clients_list_view

app = typer.Typer()


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
