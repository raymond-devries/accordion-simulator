from core import SimulatorCore, console
from typing import Optional
from rich.progress import track


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
                             print_games: bool = False):
    simulator = SimulatorCore()
    results = []
    for _ in track(range(simulations), "Running Simulations"):
        results.append(simulator.simulate(print_games))

    total_cards = sum(results)
    gross_total = total_cards * earned_per_card
    net_total = gross_total - cost_per_deck * simulations

    gross_average = gross_total / simulations
    net_average = net_total / simulations

    if print_results:
        net_color = "red" if net_total < 0 else "green"
        console.rule("[b]RESULTS[/b]")
        console.print(f"You played {simulations: ,} games")
        console.print(f"Total gross earnings: [green]${gross_total: ,.2f}[/green]")
        console.print(
            f"Total net earnings: [{net_color}]${net_total: ,.2f}[/{net_color}]")
        console.print(f"Average gross earnings: [green]${gross_average: ,.2f}[/green]")
        console.print(
            f"Average net earnings: [{net_color}]${net_average: ,.2f}[/{net_color}]")

    return {
        "results": results,
        "gross_total": gross_total,
        "net_total": net_total,
        "gross_average": gross_average,
        "net_average": net_average
    }
