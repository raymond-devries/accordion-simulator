from dask import bag as dask_bag
from core import SimulatorCore, console
from typing import Optional
from rich.progress import track
from dask.distributed import Client


def run_simulation(cost_per_deck: float,
                   earned_per_card: float,
                   print_game: bool = False, interactive: bool = False,
                   save_csv: Optional[str] = False,
                   deck_csv: Optional[str] = None,
                   ) -> dict:
    print_game = print_game or interactive
    total_cards = SimulatorCore().simulate(print_game, interactive, save_csv, deck_csv)
    gross = total_cards * earned_per_card
    net = gross - cost_per_deck
    if print_game:
        net_color = "red" if net < 0 else "green"
        console.print(f"You earned ${gross: ,.2f} [blue]({total_cards} cards x "
                      f"${earned_per_card: ,})[/blue] from the game")
        console.print(f"Making your net total: [{net_color}]${net: ,.2f}[/{net_color}]")

    return {
        "total_cards": total_cards,
        "gross": gross,
        "net": net
    }


def run_multiple_simulations(cost_per_deck: float, earned_per_card: float,
                             simulations: int = 10, print_results: bool = False,
                             print_games: bool = False, use_dask: bool = False,
                             dask_address: Optional[str] = None,
                             dask_bag_partition_size: int = 10000,
                             custom_dask_client: Optional[Client] = None) -> dict:
    if use_dask:
        if custom_dask_client is not None:
            client = custom_dask_client
            if dask_address:
                console.print(
                    f"[red]Since a custom dask client was provided, the dask address "
                    f"of[/red] {dask_address} [red]is being ignored[/red]")
        else:
            client = Client(dask_address)
        console.print(client)
        client.upload_file('core.py')

        if print_games:
            console.print("[red]Printing games is disabled when using dask.[/red]")
            console.print("[blue]Final results will still be printed[/blue]")

        def simulate(*_):
            return SimulatorCore().simulate()

        bag = dask_bag.from_sequence(range(simulations),
                                     partition_size=dask_bag_partition_size)
        results = bag.map(simulate).compute()

    else:
        simulator = SimulatorCore()
        results = [simulator.simulate(print_games) for _ in
                   track(range(simulations), "Running Simulations",
                         disable=print_games)]

    total_cards = sum(results)

    gross_total = total_cards * earned_per_card
    net_total = gross_total - cost_per_deck * simulations

    gross_average = gross_total / simulations
    net_average = net_total / simulations

    if print_results or print_games:
        net_color = "red" if net_total < 0 else "green"
        console.rule("[b]RESULTS[/b]")
        console.print(f"You played {simulations: ,} games")
        console.print(f"Total gross earnings: [green]${gross_total: ,.2f}[/green]")
        console.print(
            f"Total net earnings: [{net_color}]${net_total: ,.2f}[/{net_color}]")
        console.print(
            f"Average gross earnings: [green]${gross_average: ,.2f}[/green]")
        console.print(
            f"Average net earnings: [{net_color}]${net_average: ,.2f}[/{net_color}]")

    return {
        "results": results,
        "gross_total": gross_total,
        "net_total": net_total,
        "gross_average": gross_average,
        "net_average": net_average
    }
