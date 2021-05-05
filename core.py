import numpy as np
from rich.console import Console
from typing import Optional

VALUE = 0
SUIT = 1
TOTAL_CARDS = 2

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

PRETTY_SUITS = {
    0: '♣',
    1: '♦',
    2: '♥',
    3: '♠'
}

SUIT_STYLES = {
    0: "bold black on bright_white",
    1: "bold dark_red on bright_white",
    2: "bold dark_red on bright_white",
    3: "bold black on bright_white"
}

console = Console()


class SimulatorCore:
    def __init__(self):
        self.deck = np.array([(face, suit) for face in range(13) for suit in range(4)])
        self.game = np.zeros((52, 3), np.uint8)

        self.game_index = 0
        self.game_number = 0
        self.game_results = None

    def shuffle_cards(self):
        np.random.shuffle(self.deck)

    def move_deck_card_to_game(self, deck_index: int, game_index: int):
        self.game[game_index][VALUE] = self.deck[deck_index][VALUE]
        self.game[game_index][SUIT] = self.deck[deck_index][SUIT]
        self.game[game_index][TOTAL_CARDS] = 1

    def move_game_card(self, old_card_index: int, new_card_index: int):
        self.game[old_card_index][VALUE] = self.game[new_card_index][VALUE]
        self.game[old_card_index][SUIT] = self.game[new_card_index][SUIT]
        self.game[old_card_index][TOTAL_CARDS] += self.game[new_card_index][TOTAL_CARDS]

        self.game[new_card_index][VALUE] = 0
        self.game[new_card_index][SUIT] = 0
        self.game[new_card_index][TOTAL_CARDS] = 0

    def compare_cards(self, index1: int, index2: int) -> bool:
        return self.game[index1][VALUE] == self.game[index2][VALUE] or \
               self.game[index1][SUIT] == self.game[index2][SUIT]

    def compare_replace(self, index) -> tuple[int, bool]:
        if index >= 3:
            if self.compare_cards(index, index - 3):
                self.move_game_card(index - 3, index)
                self.shift(index)
                return index - 3, True
        if index > 0:
            if self.compare_cards(index, index - 1):
                self.move_game_card(index - 1, index)
                self.shift(index)
                return index - 1, True

        return index, False

    def shift(self, index: int):
        card_total = self.game[index + 1][TOTAL_CARDS]

        while card_total > 0:
            self.move_game_card(index, index + 1)
            index += 1
            card_total = self.game[index + 1][TOTAL_CARDS]

        self.game_index -= 1

    def print_current_state(self, card_being_checked: Optional[int] = None,
                            last_stacked: Optional[int] = None):
        total = self.game[0][TOTAL_CARDS]
        index = 0
        board = []

        while total > 0:
            value = PRETTY_VALUES[self.game[index][VALUE]]
            suit = PRETTY_SUITS[self.game[index][SUIT]]
            style = SUIT_STYLES[self.game[index][SUIT]]
            total = self.game[index][TOTAL_CARDS]
            selection = ""
            stacked = ""
            if card_being_checked == index:
                selection = "[default on blue] [/default on blue]"
            if last_stacked == index:
                stacked = "[default on red] [/default on red]"
            board.append(f"{stacked}{selection}"
                         f"[{style}] {value}{suit} [/{style}]"
                         f"{selection}{stacked}"
                         f"([green]{total}[/green])")
            index += 1
            total = self.game[index][TOTAL_CARDS]

        console.print(" ".join(board))
        console.print(f"Number of active cards: {self.game_index + 1}")

    def combine(self, index: int, target_index: int, interactive: bool = False,
                last_stacked: Optional[int] = None) -> int:
        if interactive:
            self.print_current_state(card_being_checked=index,
                                     last_stacked=last_stacked)
            input("Press enter to continue")
            print()
        replace_index, replaced = self.compare_replace(index)
        if replaced:
            return self.combine(self.game_index, replace_index, interactive,
                                replace_index)
        elif replace_index > target_index:
            return self.combine(index - 1, target_index, interactive, last_stacked)

        return last_stacked

    def check_validity(self) -> bool:
        index = 51
        while index >= 0:
            if self.game[index][TOTAL_CARDS] == 0:
                index -= 1
                continue

            if index > 0 and self.compare_cards(index, index - 1):
                return False
            if index >= 3 and self.compare_cards(index, index - 3):
                return False

            return True

    def simulate(self, print_game: bool = False, interactive: bool = False,
                 save_csv: Optional[str] = False,
                 deck_csv: Optional[str] = None):
        if deck_csv is not None:
            self.deck = np.genfromtxt(deck_csv, delimiter=",")
        else:
            self.shuffle_cards()
        self.move_deck_card_to_game(0, 0)
        self.game_index = 1

        if interactive:
            console.rule("[b blue]Welcome to interactive mode![/b blue]")
            console.print(
                f"[b blue] In this mode the program stops every time it "
                f"evaluates a card for a match.[/b blue]")
            console.print(
                f"[b blue] The card/stack being evaluated for a match is surrounded by "
                f"blue bars like so:[/b blue]"
                f"[default on blue] [/default on blue]"
                f"[{SUIT_STYLES[2]}] A♥ [/{SUIT_STYLES[2]}]"
                f"[default on blue] [/default on blue]")
            console.print("[b blue] The number of cards in a stack including the top "
                          "card is indicated by the green number, for example:[/b blue]"
                          "([green]4[/green])")
            console.print(
                f"[b blue] The last stack to have a card/stack placed on it is "
                f"surrounded by red bars like so:[/b blue] "
                f"[default on red] [/default on red]"
                f"[{SUIT_STYLES[2]}] A♥ [/{SUIT_STYLES[2]}]"
                f"[default on red] [/default on red]")
            input("Press enter to continue\n")

        last_stacked = None
        for i in range(1, 52):
            self.move_deck_card_to_game(i, self.game_index)
            if interactive:
                console.print(f"[u]Cards left in deck: {51 - i}[u]")
            last_stacked = self.combine(self.game_index, self.game_index, interactive,
                                        last_stacked)
            self.game_index += 1

        self.game_index -= 1

        if print_game:
            self.print_current_state()

        if save_csv:
            if isinstance(save_csv, str):
                np.savetxt(save_csv, self.deck, delimiter=",")
            else:
                ValueError("save_csv must be False or str type")

        return self.game[0][TOTAL_CARDS]
