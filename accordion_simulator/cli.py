import typer
from accordion_simulator.core import console

app = typer.Typer()


@app.command()
def simulate():
    console.print("[blue]CLI simulation command")
