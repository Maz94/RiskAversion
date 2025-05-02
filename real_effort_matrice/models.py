
from otree.api import *

import random
import numpy

class Constants(BaseConstants):
    name_in_url = 'real_effort_matrice'
    players_per_group = None
    num_rounds = 40
    max_rand =99
    min_rand = 9
    num_rows = 7
    num_cols = 7


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    rand_left = models.PositiveIntegerField()
    rand_right = models.PositiveIntegerField()
    solution = models.PositiveIntegerField()
    answer = models.PositiveIntegerField()
    answer_correct = models.PositiveIntegerField(initial=0)
    num_correct = models.PositiveIntegerField(initial=0)
    was_correct = models.BooleanField(initial=False)

    def initialize(self):
        self.num_correct = sum([p.answer_correct for p in self.in_all_rounds()])
        self.rand_left = random.randint(Constants.min_rand, Constants.max_rand)
        self.rand_right = random.randint(Constants.min_rand, Constants.max_rand)
        self.solution = self.rand_left + self.rand_right

        # Generate matrices
        m_left = [[random.randint(0, self.rand_left - 1) for _ in range(Constants.num_cols)] for _ in
                  range(Constants.num_rows)]
        m_right = [[random.randint(0, self.rand_right - 1) for _ in range(Constants.num_cols)] for _ in
                   range(Constants.num_rows)]

        # Set max value in a random cell
        m_left[random.randint(0, Constants.num_rows - 1)][random.randint(0, Constants.num_cols - 1)] = self.rand_left
        m_right[random.randint(0, Constants.num_rows - 1)][random.randint(0, Constants.num_cols - 1)] = self.rand_right

        # Store in participant.vars
        self.participant.vars['m_left'] = m_left
        self.participant.vars['m_right'] = m_right

    def compute_correct_answer(self):
        max_left = max(max(row) for row in self.participant.vars['m_left'])
        max_right = max(max(row) for row in self.participant.vars['m_right'])
        return max_left + max_right