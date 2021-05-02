import numpy as np

VALUE = 0
SUIT = 1
TOTAL_CARDS = 2

PRETTY_SUITS = {
    0: '♣',
    1: '♦',
    2: '♥',
    3: '♠'
}

PRETTY_VALUES = {
    0: 'A',
    1: '2',
    2: '3',
    3: '4',
    4: '5',
    5: '6',
    6: '7',
    7: '8',
    8: '9',
    9: '10',
    10: 'J',
    11: 'Q',
    12: 'K'
}


class Simulator:
    def __init__(self, simulations: int):
        self.deck = np.array([(face, suit) for face in range(13) for suit in range(4)])
        self.game = np.zeros((52, 3), np.uint8)

        self.game_index = 0
        self.game_number = 0
        self.game_results = np.zeros(simulations)

    def shuffle_cards(self):
        np.random.shuffle(self.deck)

    def move_deck_card_to_game(self, deck_index, game_index):
        self.game[game_index][VALUE] = self.deck[deck_index][VALUE]
        self.game[game_index][SUIT] = self.deck[deck_index][SUIT]
        self.game[game_index][TOTAL_CARDS] = 1

    def move_game_card(self, old_card_index, new_card_index):
        self.game[old_card_index][VALUE] = self.game[new_card_index][VALUE]
        self.game[old_card_index][SUIT] = self.game[new_card_index][SUIT]
        self.game[old_card_index][TOTAL_CARDS] += 1

        self.game[new_card_index][VALUE] = 0
        self.game[new_card_index][SUIT] = 0
        self.game[new_card_index][TOTAL_CARDS] = 0

    def compare_cards(self, index1, index2) -> bool:
        return self.game[index1][VALUE] == self.game[index2][VALUE] or \
               self.game[index1][SUIT] == self.game[index2][SUIT]

    def compare_replace(self, index) -> int:
        if index >= 3:
            if self.compare_cards(index, index - 3):
                self.move_game_card(index - 3, index)
                self.shift(index)
                return index - 3
        if index > 0:
            if self.compare_cards(index, index - 1):
                self.move_game_card(index - 1, index)
                self.shift(index)
                return index - 1

        return index

    def shift(self, index):
        card_total = self.game[index + 1][TOTAL_CARDS]

        while card_total > 0:
            self.move_game_card(index, index + 1)
            index += 1
            card_total = self.game[index + 1][TOTAL_CARDS]

        self.game_index -= 1

    def print_game(self):
        total = self.game[0][TOTAL_CARDS]
        index = 0
        board = []

        while total > 0:
            board.append(PRETTY_VALUES[self.game[index][VALUE]] + PRETTY_SUITS[
                self.game[index][SUIT]])
            index += 1
            total = self.game[index][TOTAL_CARDS]

        print(board)
        print(f"Number of active cards: {self.game_index + 1}")

    def combine(self, index, target_index, interactive=False):
        if interactive:
            self.print_game()
            input("Press Enter to continue")
        replace_index = self.compare_replace(index)
        if replace_index < target_index:
            return self.combine(self.game_index, replace_index, interactive)
        elif replace_index > target_index:
            return self.combine(index - 1, target_index, interactive)

    def simulate(self, print_games=False, interactive=False):
        self.shuffle_cards()
        self.move_deck_card_to_game(0, 0)
        self.game_index = 1

        for i in range(1, 52):
            self.move_deck_card_to_game(i, self.game_index)
            self.combine(self.game_index, self.game_index, interactive)
            self.game_index += 1

        if print_games:
            self.print_game()


simulator = Simulator(100)
simulator.simulate(print_games=True)
