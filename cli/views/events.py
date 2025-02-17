from rich.console import Console
from rich.table import Table
from cli.helpers import format_phone


def events_list_view(events):
    table = Table(title="Events", caption="See details for notes about the event")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Contract ID")
    table.add_column("Client")
    table.add_column("Sales Rep")
    table.add_column("Support Rep")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Location")

    for event in events:
        table.add_row(
            str(event["id"]),
            str(event["title"]),
            str(event["contract"]["id"]),
            str(event["client"]["fullname"]),
            str(event["sales_contact"]["fullname"]),
            str(
                event["support_contact"]["fullname"] if event["support_contact"] else ""
            ),
            str(event["event_start"]),
            str(event["event_end"]),
            str(event["location"]),
        )

    console = Console()
    console.print(table)
