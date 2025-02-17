import typer

app = typer.Typer()


@app.command()
def version():
    print("EpicEvents CLI Version 0.1")
