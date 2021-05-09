import numpy as np

from cg_simulator.core import (
    TOTAL_CARDS,
    get_shuffled_deck,
    print_current_state,
    rank_match,
    remove_card,
    shift,
    suit_match,
)


def _remove_slice(array, start, end):
    for i in range(start, end):
        remove_card(array, i)


def _play(array: np.array):
    index1 = 0
    card_checked = array[index1 + 3][TOTAL_CARDS]

    while card_checked:
        # print_current_state(array, 0, index1 + 3, index1)
        # input()
        index2 = index1 + 3

        if rank_match(array, index1, index2):
            _remove_slice(array, index1, index2 + 1)
            shift(array, index1, empty_space=4)
            index1 -= 4

        elif suit_match(array, index1, index2):
            _remove_slice(array, index1 + 1, index2)
            shift(array, index1 + 1, empty_space=2)
            index1 = max(0, index1 - 2)

        else:
            index1 += 1

        card_checked = array[index1 + 3][TOTAL_CARDS]


def simulate():
    deck = get_shuffled_deck()
    totals = np.ones((52, 1), np.uint8)
    game = np.append(deck, totals, 1)
    _play(game)
