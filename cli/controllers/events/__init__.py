import json
from typing import Optional
from typing_extensions import Annotated
import typer
import requests
import typer
from cli.helpers import authenticate, handle_response
from cli.views.events import events_list_view, event_show_view
from cli.controllers.contracts import list as contracts_list
from cli.controllers.users import list as users_list
from cli.views.shared import message_show_view
from cli.rbac import authorize

app = typer.Typer()


@app.callback()
def authorize_commands(ctx: typer.Context):
    authorize(ctx)


@app.command()
def create(
    ctx: typer.Context,
    title: Annotated[
        str, typer.Option("--title", "-t", help="The event title", prompt=True)
    ],
    event_start: Annotated[
        str,
        typer.Option(
            "--start",
            help="The start date with format: YYYY-mm-dd HH:MM:SS",
            prompt=True,
        ),
    ],
    event_end: Annotated[
        str,
        typer.Option(
            "--end", help="The end date with format: YYYY-mm-dd HH:MM:SS", prompt=True
        ),
    ],
    location: Annotated[
        str, typer.Option("--location", "-l", help="Location of the event", prompt=True)
    ],
    attendees: Annotated[
        int, typer.Option("--attendees", "-a", help="Number of attendees", prompt=True)
    ],
    notes: Annotated[
        Optional[str], typer.Option("--notes", "-n", help="Notes about the event")
    ] = None,
    contract: Annotated[
        Optional[int], typer.Option("--contract", "-c", help="The contract id")
    ] = None,
):
    token = authenticate()
    if not contract:
        ctx.invoke(contracts_list, "signed")
        contract = int(typer.prompt("Please choose a contract for this event"))
    new_event = {
        "title": title,
        "contract_id": contract,
        "event_start": event_start,
        "event_end": event_end,
        "location": location,
        "attendees": attendees,
        "notes": notes if notes else None,
    }
    response = requests.post(
        "http://localhost:5000/events",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(new_event),
    )
    data = handle_response(response)
    message_show_view({"Success": "Event Created"})
    event_show_view(data)


@app.command()
def list(
    filter: Annotated[
        Optional[str],
        typer.Option(
            "--filter",
            "-f",
            help="Filter the results: Options are 'assigned' for support users who want to see results assigned to them or 'no-support' to display results with no support users assigned",
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
    data = handle_response(response)
    event_show_view(data)


@app.command()
def add_support(
    ctx: typer.Context,
    id: Annotated[
        Optional[int], typer.Option("--id", "-i", help="The event id")
    ] = None,
    support: Annotated[
        Optional[int],
        typer.Option("--support", "-s", help="The id of the support user"),
    ] = None,
):
    token = authenticate()
    if id is None:
        ctx.invoke(list, "no-support")
        id = int(typer.prompt("Please choose an event to add support to"))

    if support is None:
        ctx.invoke(users_list, "support")
        support = int(typer.prompt("Please choose a user to add as support"))

    response = requests.put(
        f"http://localhost:5000/events/{id}/add-support",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"support_contact_id": support}),
    )
    data = handle_response(response)
    message_show_view({"Success": "Support Added"})
    event_show_view(data)


@app.command()
def update(
    ctx: typer.Context,
    id: Annotated[
        Optional[int], typer.Option("--id", "-i", help="The event id")
    ] = None,
    title: Annotated[
        Optional[str], typer.Option("--title", "-t", help="The event title")
    ] = None,
    event_start: Annotated[
        Optional[str],
        typer.Option(
            "--start",
            help="The start date with format: YYYY-mm-dd HH:MM:SS",
        ),
    ] = None,
    event_end: Annotated[
        Optional[str],
        typer.Option(
            "--end",
            help="The end date with format: YYYY-mm-dd HH:MM:SS",
        ),
    ] = None,
    location: Annotated[
        Optional[str],
        typer.Option(
            "--location",
            "-l",
            help="Location of the event",
        ),
    ] = None,
    attendees: Annotated[
        Optional[int],
        typer.Option(
            "--attendees",
            "-a",
            help="Number of attendees",
        ),
    ] = None,
    notes: Annotated[
        Optional[str], typer.Option("--notes", "-n", help="Notes about the event")
    ] = None,
):
    token = authenticate()
    if not id:
        ctx.invoke(list, "assigned")
        id = int(typer.prompt("Please choose an event to update"))
    payload = {}
    payload["title"] = title if title else None
    payload["event_start"] = event_start if event_start else None
    payload["event_end"] = event_end if event_end else None
    payload["location"] = location if location else None
    payload["attendees"] = attendees if attendees else None
    payload["notes"] = notes if notes else None

    update_event = {}
    for key in payload:
        if payload[key] is not None:
            update_event[key] = payload[key]
    if update_event.keys():
        response = requests.put(
            f"http://localhost:5000/events/{id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(update_event),
        )
        data = handle_response(response)
        message_show_view({"Success": "Event Updated"})
        event_show_view(data)


@app.command()
def delete(id: int):
    token = authenticate()
    event = requests.get(
        f"http://localhost:5000/events/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(event)
    event_show_view(data)
    typer.confirm(
        "Do you really want to delete this event? There is no going back.", abort=True
    )
    response = requests.delete(
        f"http://localhost:5000/events/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = handle_response(response)
    message_show_view(data)
