from . import models
from otree.api import *
from otree.api import Currency as c, currency_range
from .models import Constants
from django.conf import settings

class Instructions(Page):
    def is_displayed(self):
        # ✅ Get cumulative payoff from all apps
        total_payoff = round(float(self.player.participant.payoff), 2)  # ✅ Keeps decimals

        # ✅ Show only in round 1 AND if total payoff < 2
        return self.round_number == 1 and total_payoff < 20

    def before_next_page(self):
        self.participant.vars["played_this_app"] = True


class Sum(Page):
    form_model = 'player'
    form_fields = ['answer']

    def is_displayed(self):
        # ✅ Get total payoff from all apps, default to 0
        total = self.participant.vars.get("total_payoff", 0)
        return total <= 20

    def vars_for_template(self):
        # ✅ Only initialize task content once per round
        self.player.initialize()

        was_correct = None
        if self.round_number > 1:
            previous = self.player.in_round(self.round_number - 1)
            was_correct = previous.answer_correct == 1

        return {'was_correct': was_correct}

    def before_next_page(self):
        # Score answer
        is_correct = int(self.player.answer == self.player.solution)
        self.player.answer_correct = is_correct

        # Track number of correct answers in this app
        self.player.num_correct = sum(p.answer_correct for p in self.player.in_all_rounds())

        # Per-round payoff
        self.player.payoff = c(is_correct)

        # Manually track total payoff across apps
        previous_total = self.participant.vars.get("total_payoff", 0)
        new_total = previous_total + is_correct
        self.participant.vars["total_payoff"] = new_total

        # Set official participant payoff for export
        self.participant.payoff = c(new_total)


class Wait(WaitPage):
    pass



page_sequence = [Instructions, Sum]
