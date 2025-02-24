from rich.console import Console
from rich.table import Table
from cli.helpers import format_phone


def contracts_list_view(contracts):
    table = Table(title="Contracts")
    table.add_column("ID")
    table.add_column("Client")
    table.add_column("Sales Rep")
    table.add_column("Total")
    table.add_column("Due")
    table.add_column("Status")

    for contract in contracts:
        table.add_row(
            str(contract["id"]),
            str(contract["client"]["fullname"]),
            str(contract["sales_contact"]["fullname"]),
            str(contract["total_amount"]),
            str(contract["remaining_amount"]),
            str(contract["status"]),
        )

    console = Console()
    console.print(table)


def contract_show_view(contract):
    table = Table(title="Contract")
    table.add_column("ID")
    table.add_column("Client")
    table.add_column("Sales Rep")
    table.add_column("Total")
    table.add_column("Due")
    table.add_column("Status")

    table.add_row(
        str(contract["id"]),
        str(contract["client"]["fullname"]),
        str(contract["sales_contact"]["fullname"]),
        str(contract["total_amount"]),
        str(contract["remaining_amount"]),
        str(contract["status"]),
    )

    console = Console()
    console.print(table)
