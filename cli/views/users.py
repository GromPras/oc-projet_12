from rich.console import Console
from rich.table import Table
from cli.helpers import format_phone


def users_list_view(users):
    table = Table(title="Users")
    table.add_column("ID")
    table.add_column("Full Name")
    table.add_column("Email")
    table.add_column("Phone #")
    table.add_column("Role")

    for user in users:
        table.add_row(
            str(user["id"]),
            str(user["fullname"]),
            str(user["email"]),
            format_phone(str(user["phone"])),
            str(user["role"]),
        )

    console = Console()
    console.print(table)


def user_show_view(user):
    table = Table(title="User")
    table.add_column("ID")
    table.add_column("Full Name")
    table.add_column("Email")
    table.add_column("Phone #")
    table.add_column("Role")

    table.add_row(
        str(user["id"]),
        str(user["fullname"]),
        str(user["email"]),
        format_phone(str(user["phone"])),
        str(user["role"]),
    )

    console = Console()
    console.print(table)
