from rich.console import Console
from rich.table import Table


def message_show_view(data):
    table = Table(title="Message")
    table.add_column("Type")
    table.add_column("Message")

    keys = data.keys()
    for key in keys:
        table.add_row(
            str(key),
            str(data[key]),
        )

    console = Console()
    console.print(table)
