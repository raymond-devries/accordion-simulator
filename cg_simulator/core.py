from typing import Optional

import numpy as np
from numba import njit
from rich.console import Console

VALUE = 0
SUIT = 1
TOTAL_CARDS = 2

PRETTY_VALUES = {
    0: "A",
    1: "2",
    2: "3",
    3: "4",
    4: "5",
    5: "6",
    6: "7",
    7: "8",
    8: "9",
    9: "10",
    10: "J",
    11: "Q",
    12: "K",
}

PRETTY_SUITS = {0: "♣", 1: "♦", 2: "♥", 3: "♠"}

SUIT_STYLES = {
    0: "bold black on bright_white",
    1: "bold dark_red on bright_white",
    2: "bold dark_red on bright_white",
    3: "bold black on bright_white",
}

console = Console()

new_deck = np.array([(face, suit) for face in range(13) for suit in range(4)], np.uint8)


def print_current_state(
    game,
    game_index,
    card_being_checked: Optional[int] = None,
    last_stacked: Optional[int] = None,
):
    total = game[0][TOTAL_CARDS]
    index = 0
    board = []

    while total > 0:
        value = PRETTY_VALUES[game[index][VALUE]]
        suit = PRETTY_SUITS[game[index][SUIT]]
        style = SUIT_STYLES[game[index][SUIT]]
        total = game[index][TOTAL_CARDS]
        selection = ""
        stacked = ""
        if card_being_checked == index:
            selection = "[default on blue] [/default on blue]"
        if last_stacked == index:
            stacked = "[default on red] [/default on red]"
        board.append(
            f"{stacked}{selection}"
            f"[{style}] {value}{suit} [/{style}]"
            f"{selection}{stacked}"
            f"([green]{total}[/green])"
        )
        index += 1
        total = game[index][TOTAL_CARDS]

    console.print(" ".join(board))
    console.print(f"Number of active cards: {game_index + 1}")


@njit
def _compare(array: np.array, index1: int, index2: int) -> bool:
    return (
        array[index1][VALUE] == array[index2][VALUE]
        or array[index1][SUIT] == array[index2][SUIT]
    )


@njit
def _move_card(array: np.array, old_index: int, new_index: int):
    array[old_index][VALUE] = array[new_index][VALUE]
    array[old_index][SUIT] = array[new_index][SUIT]
    array[old_index][TOTAL_CARDS] += array[new_index][TOTAL_CARDS]

    array[new_index][VALUE] = 0
    array[new_index][SUIT] = 0
    array[new_index][TOTAL_CARDS] = 0


@njit
def _shift(array, index):
    card_total = array[index + 1][TOTAL_CARDS]

    while card_total > 0:
        _move_card(array, index, index + 1)
        index += 1
        card_total = array[index + 1][TOTAL_CARDS]


@njit
def _compare_replace(array, index) -> tuple[int, bool]:
    if index >= 3:
        if _compare(array, index, index - 3):
            _move_card(array, index - 3, index)
            _shift(array, index)
            return index - 3, True
    if index > 0:
        if _compare(array, index, index - 1):
            _move_card(array, index - 1, index)
            _shift(array, index)
            return index - 1, True

    return index, False


@njit
def _move_deck_card_to_game(
    old_array: np.array, new_array: np.array, deck_index: int, game_index: int
):
    new_array[game_index][VALUE] = old_array[deck_index][VALUE]
    new_array[game_index][SUIT] = old_array[deck_index][SUIT]
    new_array[game_index][TOTAL_CARDS] = 1


@njit
def _shuffle(array: np.array) -> np.array:
    np.random.shuffle(array)


def _check_validity(array) -> bool:
    index = 51
    while index >= 0:
        if array[index][TOTAL_CARDS] == 0:
            index -= 1
            continue

        if index > 0 and _compare(array, index, index - 1):
            return False
        if index >= 3 and _compare(array, index, index - 3):
            return False

        return True


@njit
def _combine(array, index, game_index):
    replace_index, replaced = _compare_replace(array, index)

    if not replaced:
        return game_index

    game_index = game_index - 1
    index = game_index
    target_index = replace_index

    while target_index <= index:
        replace_index, replaced = _compare_replace(array, index)
        if replaced:
            target_index = replace_index
            game_index -= 1
            index = game_index
        else:
            index -= 1

    return game_index


@njit
def simulate() -> int:
    deck = np.copy(new_deck)
    game = np.zeros((52, 3), np.uint8)
    _shuffle(deck)
    _move_deck_card_to_game(deck, game, 0, 0)
    game_index = 1
    for i in range(1, 52):
        _move_deck_card_to_game(deck, game, i, game_index)
        game_index = _combine(game, game_index, game_index) + 1

    return game[0][TOTAL_CARDS]


@njit
def multiple_simulations(n: int):
    results = np.zeros(n)
    for i in range(n):
        results[i] = simulate()

    return results


def combine_recursive(
    game: np.array,
    game_index: int,
    index: int,
    target_index: int,
    interactive: bool = False,
    last_stacked: Optional[int] = None,
) -> int:
    if interactive:
        print_current_state(
            game,
            game_index,
            card_being_checked=index,
            last_stacked=last_stacked,
        )
        input("Press enter to continue")
        print()
    replace_index, replaced = _compare_replace(game, index)

    if replaced:
        game_index -= 1
        return combine_recursive(
            game, game_index, game_index, replace_index, interactive, replace_index
        )
    elif replace_index > target_index:
        return combine_recursive(
            game, game_index, index - 1, target_index, interactive, last_stacked
        )

    return last_stacked, game_index


def simulate_recursive(
    print_game: bool = False,
    interactive: bool = False,
    save_csv: Optional[str] = False,
    deck_csv: Optional[str] = None,
):
    game = np.zeros((52, 3), np.uint8)
    if deck_csv is not None:
        deck = np.genfromtxt(deck_csv, delimiter=",")
    else:
        deck = np.copy(new_deck)
        _shuffle(deck)
    _move_deck_card_to_game(deck, game, 0, 0)
    game_index = 1

    if interactive:
        console.rule("[b blue]Welcome to interactive mode![/b blue]")
        console.print(
            f"[b blue] In this mode the program stops every time it "
            f"evaluates a card for a match.[/b blue]"
        )
        console.print(
            f"[b blue] The card/stack being evaluated for a match is surrounded by "
            f"blue bars like so:[/b blue]"
            f"[default on blue] [/default on blue]"
            f"[{SUIT_STYLES[2]}] A♥ [/{SUIT_STYLES[2]}]"
            f"[default on blue] [/default on blue]"
        )
        console.print(
            "[b blue] The number of cards in a stack including the top "
            "card is indicated by the green number, for example:[/b blue]"
            "([green]4[/green])"
        )
        console.print(
            f"[b blue] The last stack to have a card/stack placed on it is "
            f"surrounded by red bars like so:[/b blue] "
            f"[default on red] [/default on red]"
            f"[{SUIT_STYLES[2]}] A♥ [/{SUIT_STYLES[2]}]"
            f"[default on red] [/default on red]"
        )
        input("Press enter to continue\n")

    last_stacked = None
    for i in range(1, 52):
        _move_deck_card_to_game(deck, game, i, game_index)
        if interactive:
            console.print(f"[u]Cards left in deck: {51 - i}[u]")
        last_stacked, game_index = combine_recursive(
            game, game_index, game_index, game_index, interactive, last_stacked
        )
        game_index += 1

    game_index -= 1

    if print_game:
        print_current_state(game, game_index)

    if save_csv:
        if isinstance(save_csv, str):
            np.savetxt(save_csv, deck, delimiter=",")
        else:
            ValueError("save_csv must be False or str type")

    return game[0][TOTAL_CARDS]
