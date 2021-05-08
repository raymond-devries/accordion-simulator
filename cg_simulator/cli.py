import typer

from cg_simulator.core import console

app = typer.Typer()


@app.command()
def simulate():
    console.print("[red]CLI is not implemented yet")
