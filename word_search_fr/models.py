from otree.api import *
import random
from pathlib import Path


doc = """Multiplayer word search game"""

def load_word_list():
    word_file = Path(__file__).parent / 'words.txt'
    return set(word_file.read_text(encoding='utf-8').split())

DIM = 10  # <- défini globalement ici
COORDS = [(x, y) for x in range(DIM) for y in range(DIM)]

class C(BaseConstants):
    NAME_IN_URL = 'word_search_fr'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    DIM = DIM
    NUM_SQUARES = DIM * DIM
    LEXICON = load_word_list()
    COORDS = COORDS  # ← ✅ on les injecte proprement ici

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    board = models.LongStringField()

class Player(BasePlayer):
    score = models.IntegerField(initial=0)
    earnings = models.CurrencyField(initial=0)

class FoundWord(ExtraModel):
    word = models.StringField()
    player = models.Link(Player)
    group = models.Link(Group)

# === Utility functions ===

def word_in_board(word, board):
    lengths = list(range(1, len(word) + 1))
    paths = {_: [] for _ in lengths}

    for i in range(C.DIM):
        for j in range(C.DIM):
            coord = (i, j)
            if board[coord] == word[0]:
                paths[1].append([coord])

    for length in lengths[1:]:
        target_char = word[length - 1]
        for path in paths[length - 1]:
            cur_x, cur_y = path[-1]
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_coord = (cur_x + dx, cur_y + dy)
                    if (
                        check_coord in C.COORDS
                        and board[check_coord] == target_char
                        and check_coord not in path
                    ):
                        paths[length].append(path + [check_coord])
    return bool(paths[len(word)])

def load_board(board_str):
    return dict(zip(C.COORDS, board_str.replace('\n', '').lower()))
