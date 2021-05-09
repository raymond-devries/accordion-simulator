from typing import Optional

import numpy as np
from numba import njit

from cg_simulator.core import (
    SUIT,
    SUIT_STYLES,
    TOTAL_CARDS,
    VALUE,
    console,
    get_shuffled_deck,
    move_card,
    print_current_state,
    rank_or_suit_match,
    shift,
)


@njit
def _compare_replace(array, index) -> tuple[int, bool]:
    if index >= 3:
        if rank_or_suit_match(array, index, index - 3):
            move_card(array, index - 3, index)
            shift(array, index)
            return index - 3, True
    if index > 0:
        if rank_or_suit_match(array, index, index - 1):
            move_card(array, index - 1, index)
            shift(array, index)
            return index - 1, True

    return index, False


@njit
def _move_from_old_to_new(
    old_array: np.array, new_array: np.array, old_index: int, new_index: int
):
    new_array[new_index][VALUE] = old_array[old_index][VALUE]
    new_array[new_index][SUIT] = old_array[old_index][SUIT]
    new_array[new_index][TOTAL_CARDS] = 1


def _check_validity(array) -> bool:
    index = 51
    while index >= 0:
        if array[index][TOTAL_CARDS] == 0:
            index -= 1
            continue

        if index > 0 and rank_or_suit_match(array, index, index - 1):
            return False
        if index >= 3 and rank_or_suit_match(array, index, index - 3):
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
    game = np.zeros((52, 3), np.uint8)
    deck = get_shuffled_deck()
    _move_from_old_to_new(deck, game, 0, 0)
    game_index = 1
    for i in range(1, 52):
        _move_from_old_to_new(deck, game, i, game_index)
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
        deck = get_shuffled_deck()
    _move_from_old_to_new(deck, game, 0, 0)
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
        _move_from_old_to_new(deck, game, i, game_index)
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
