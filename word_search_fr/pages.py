from otree.api import *
from .models import C, Group, Player, FoundWord, load_board, word_in_board
import random
import unicodedata


def normalize_word(word):
    nfkd_form = unicodedata.normalize('NFKD', word)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()


def place_word(grid, word, row, col, dx, dy):
    for i, ch in enumerate(word):
        x, y = row + i * dx, col + i * dy
        grid[x][y] = ch


def can_place_word(grid, word, row, col, dx, dy):
    dim = len(grid)
    for i, ch in enumerate(word):
        x, y = row + i * dx, col + i * dy
        if not (0 <= x < dim and 0 <= y < dim):
            return False
        if grid[x][y] not in ('', ch):
            return False
    return True


def generate_balanced_grid(word_list, dim, min_words=8, max_words=12):
    directions = [
        (0, 1),   # horizontal
        (1, 0),   # vertical
        (1, 1),   # diagonal down-right
        (-1, 1),  # diagonal up-right
        (0, -1),  # horizontal reversed
        (-1, 0),  # vertical reversed
        (-1, -1), # diagonal up-left
        (1, -1),  # diagonal down-left
    ]

    normalized_words = [normalize_word(w) for w in word_list if 3 <= len(w) <= dim and w.isalpha()]
    verbs = ["manger", "boire", "courir", "parler", "aimer", "penser", "regarder", "travailler", "jouer", "finir"]
    normalized_words += verbs

    attempt = 0
    while attempt < 10:
        grid = [['' for _ in range(dim)] for _ in range(dim)]
        words_to_place = random.sample(normalized_words, min(max_words, len(normalized_words)))
        inserted_words = []

        for word in words_to_place:
            word = word.upper()
            random.shuffle(directions)
            placed = False

            for dx, dy in directions:
                for _ in range(50):
                    row = random.randint(0, dim - 1)
                    col = random.randint(0, dim - 1)
                    if can_place_word(grid, word, row, col, dx, dy):
                        place_word(grid, word, row, col, dx, dy)
                        inserted_words.append(word)
                        placed = True
                        break
                if placed:
                    break

        if len(inserted_words) >= min_words:
            break
        attempt += 1

    letters = 'EEEEEEEAAAAAIIIOOUUNNRRSSSTTLCMPDGBFVHJQZ'
    for i in range(dim):
        for j in range(dim):
            if grid[i][j] == '':
                grid[i][j] = random.choice(letters)

    return [''.join(row) for row in grid], inserted_words

class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1


class WaitToStart(WaitPage):
    def after_all_players_arrive(self):
        board_rows, inserted = generate_balanced_grid(C.LEXICON, C.DIM)
        self.group.board = '\n'.join(board_rows)
        for p in self.group.get_players():
            p.participant.vars['inserted_words'] = inserted


class Play(Page):
    timeout_seconds = 3 * 60

    def vars_for_template(self):
        return dict(
            board=self.group.board.upper().split('\n'),
            inserted_words=self.participant.vars.get('inserted_words', [])
        )

    def js_vars(self):
        return dict(
            my_id=self.player.id_in_group,
            dim=C.DIM
        )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        board = group.board

        if 'word' in data:
            word = data['word'].lower()
            is_in_board = len(word) >= 3 and word_in_board(word, load_board(board))
            is_in_lexicon = is_in_board and word in C.LEXICON
            is_valid = is_in_board and is_in_lexicon
            already_found = is_valid and bool(FoundWord.filter(group=group, word=word))
            success = is_valid and not already_found

            news = dict(
                word=word,
                success=success,
                is_in_board=is_in_board,
                is_in_lexicon=is_in_lexicon,
                already_found=already_found,
                id_in_group=player.id_in_group,
            )

            if success:
                FoundWord.create(group=group, word=word, player=player)
                player.score += 1
        else:
            news = {}

        scores = [[p.id_in_group, p.score] for p in group.get_players()]
        found_words = [fw.word for fw in FoundWord.filter(group=group)]

        return {0: dict(news=news, scores=scores, found_words=found_words)}
class Results(Page):
    def vars_for_template(self):
        base_payoff = self.player.score * 0.5
        opponent = self.player.get_others_in_group()[0]
        bonus = 2 if self.player.score > opponent.score else 0.0
        total = base_payoff + bonus

        # ✅ Set this app's payoff
        self.player.payoff = total

        # ✅ Add this app's payoff to the running total in participant.vars
        previous_total = self.participant.vars.get("total_payoff", 0)
        new_total = previous_total + float(self.player.payoff)
        self.participant.vars["total_payoff"] = new_total

        # ✅ Sync with official oTree total
        self.participant.payoff = new_total

        return dict(
            final_score=self.player.score,
            opponent_score=opponent.score,
            base_payoff=base_payoff,
            bonus=bonus,
            total_payoff= float(self.player.payoff)
        )

page_sequence = [Instructions,WaitToStart, Play, Results]

