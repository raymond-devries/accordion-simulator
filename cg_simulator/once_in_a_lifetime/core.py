import numpy as np
from numba import njit

from cg_simulator.core import (
    TOTAL_CARDS,
    get_shuffled_deck,
    print_current_state,
    rank_match,
    remove_card,
    shift,
    suit_match,
)


@njit
def _remove_slice(array, start, end):
    for i in range(start, end):
        remove_card(array, i)


@njit
def _play(array: np.array):
    index1 = 0
    card_checked = array[index1 + 3][TOTAL_CARDS]

    while card_checked and index1 + 3 < 52:
        index2 = index1 + 3

        if rank_match(array, index1, index2):
            _remove_slice(array, index1, index2 + 1)
            shift(array, index1, empty_space=4)
            index1 = max(0, index1 - 4)

        elif suit_match(array, index1, index2):
            _remove_slice(array, index1 + 1, index2)
            shift(array, index1 + 1, empty_space=2)
            index1 = max(0, index1 - 2)

        else:
            index1 += 1

        card_checked = array[index1 + 3][TOTAL_CARDS]

    return np.sum(array, 0)[TOTAL_CARDS]


@njit
def simulate():
    deck = get_shuffled_deck()
    totals = np.ones((52, 1), np.uint8)
    game = np.append(deck, totals, 1)
    game_results = _play(game)
    return game_results


@njit
def simulate_multiple(n=10):
    results = np.zeros(n, np.uint8)
    for i in range(n):
        results[i] = simulate()
