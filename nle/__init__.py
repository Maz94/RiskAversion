import os
import random
import statistics
from pathlib import Path
from otree.api import *

app_name = Path(__file__).parent.name

doc = """
NEL - Number Line Estimation <br>
Siegler, R. S., & Opfer, J. E. (2003). The development of numerical estimation: Evidence for multiple 
representations of numerical quantity. Psychological Science, 14(3), 237-243.
"""


class C(BaseConstants):
    NAME_IN_URL = 'nle'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NB_TARGETS = 10
    NLE_TIME = 5
    CONSTANTE = 4  # Gain si cible exacte
    FACTEUR_DISTANCE = 0.1  # Gain = CONSTANTE - FACTEUR_DISTANCE * | cible - valeur sélectionnée |
    NLE_VALUES = [18.09, 85.03, 8.11, 77.09, 92.17, 14.64, 59.99, 93.17, 9.11, 17.76]


class Subsession(BaseSubsession):
    nle_values = models.StringField()


def creating_session(subsession: Subsession):
    subsession.nle_values = "-".join(map(str, C.NLE_VALUES))


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    nle_paid_game = models.IntegerField()

    # -- STANDARD
    nle_1 = models.FloatField()
    nle_2 = models.FloatField()
    nle_3 = models.FloatField()
    nle_4 = models.FloatField()
    nle_5 = models.FloatField()
    nle_6 = models.FloatField()
    nle_7 = models.FloatField()
    nle_8 = models.FloatField()
    nle_9 = models.FloatField()
    nle_10 = models.FloatField()
    nle_avg_distance = models.FloatField()
    nle_payoff = models.CurrencyField()

    def compute_nle_payoff(self):
        """Compute payoff for this task and update total payoff separately."""
        targets = C.NLE_VALUES
        differences = [abs(getattr(self, f"nle_{i}") - targets[i - 1]) for i in range(1, C.NB_TARGETS + 1)]
        self.nle_avg_distance = round(statistics.mean(differences), 2)
        self.nle_payoff = cu(C.CONSTANTE - C.FACTEUR_DISTANCE * self.nle_avg_distance)

        # ✅ Store this task's payoff separately
        self.payoff = self.nle_payoff

        # ✅ Retrieve previous total payoff from past tasks
        previous_total_payoff = self.participant.vars.get("total_payoff", 0)

        # ✅ Update cumulative total payoff
        new_total_payoff = previous_total_payoff + float(self.nle_payoff)
        self.participant.vars["total_payoff"] = new_total_payoff

        txt_final = (f"Votre distance moyenne entre la valeur cible et la position du curseur "
                     f"a été de {self.nle_avg_distance}. Votre gain pour cette tâche est de "
                     f"{self.nle_payoff}. Votre total cumulé sur toutes les tâches est désormais {new_total_payoff}.")

        self.participant.vars[app_name] = dict(txt_final=txt_final, payoff=self.nle_payoff)


# ======================================================================================================================
#
# -- PAGES
#
# ======================================================================================================================
class MyPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict()

    @staticmethod
    def js_vars(player: Player):
        return dict(
            fill_auto=player.session.config.get("fill_auto", False),
            **C.__dict__.copy()
        )


class Instructions(MyPage):
    pass


class Decision(MyPage):
    form_model = "player"
    form_fields = [f"nle_{i}" for i in range(1, C.NB_TARGETS + 1)]

    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        existing["nle_values"] = player.subsession.nle_values.split("-")
        return existing

    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        existing["nle_values"] = player.subsession.nle_values.split("-")
        return existing

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            for i in range(1, C.NB_TARGETS + 1):
                setattr(player, f"nle_{i}", round(random.uniform(0, 100), 2))
            player.participant._is_bot = True

        # ✅ Compute payoff and update total payoff
        player.compute_nle_payoff()


class Results(MyPage):
    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        targets = list(map(float, player.subsession.nle_values.split("-")))
        positions = [getattr(player, f"nle_{i}") for i in range(1, C.NB_TARGETS + 1)]
        distances = [round(abs(targets[i] - positions[i]), 2) for i in range(C.NB_TARGETS)]
        targets_numbers = list(zip(targets, positions, distances))

        # ✅ Retrieve the total payoff accumulated so far
        total_payoff = player.participant.vars.get("total_payoff", 0)

        existing["targets_numbers"] = targets_numbers
        existing["task_payoff"] = player.payoff  # ✅ Show only this task's payoff
        existing["total_payoff"] = total_payoff  # ✅ Display cumulative payoff
        return existing


page_sequence = [
    Instructions, Decision, Results
]
