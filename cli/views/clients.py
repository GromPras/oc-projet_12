from rich.console import Console
from rich.table import Table
from cli.helpers import format_phone


def clients_list_view(clients):
    table = Table(title="Clients")
    table.add_column("ID")
    table.add_column("Full Name")
    table.add_column("Email")
    table.add_column("Phone #")
    table.add_column("Company")
    table.add_column("Sales Rep")

    for client in clients:
        table.add_row(
            str(client["id"]),
            str(client["fullname"]),
            str(client["email"]),
            format_phone(str(client["phone"])),
            str(client["company"]),
            str(client["sales_contact"]["fullname"]),
        )

    console = Console()
    console.print(table)


def client_show_view(client):
    table = Table(title="Client")
    table.add_column("ID")
    table.add_column("Full Name")
    table.add_column("Email")
    table.add_column("Phone #")
    table.add_column("Company")
    table.add_column("Sales Rep")

    table.add_row(
        str(client["id"]),
        str(client["fullname"]),
        str(client["email"]),
        format_phone(str(client["phone"])),
        str(client["company"]),
        str(client["sales_contact"]["fullname"]),
    )

    console = Console()
    console.print(table)
