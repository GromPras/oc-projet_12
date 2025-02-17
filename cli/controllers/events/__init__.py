from typing import Optional
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response
from cli.views.events import events_list_view

app = typer.Typer()


@app.command()
def list(
    filter: Annotated[
        Optional[str],
        typer.Option(
            help="Filter the results: Options are 'assigned' for support users who want to see results assigned to them or 'no-support' to display results with no support users assigned"
        ),
    ] = None,
):
    filters = {"assigned": "current-user", "no-support": "none"}
    active_filter = ""
    if filter and filter in filters.keys():
        active_filter = f"?support={filters[filter]}"
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/events{active_filter}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    events_list_view(data)


@app.command()
def show(id: int):
    token = authenticate()
    response = requests.get(
        f"http://localhost:5000/events/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(handle_response(response))


@app.command()
def delete(id: int):
    token = authenticate()
    response = requests.delete(
        f"http://localhost:5000/events/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(handle_response(response))
