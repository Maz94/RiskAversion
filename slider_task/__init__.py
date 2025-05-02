from otree.api import *


author = 'D. Dubois'

doc = """
Slider Task
"""


class C(BaseConstants):
    NAME_IN_URL = 'slt'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TIME_LIMIT = 120  # seconds
    REQUIRED_SUCCESS = 2
    PAYOFF_SUCCESS = 100


class Subsession(BaseSubsession):
    def vars_for_admin_report(self):
        players_infos = list()

        for p in self.get_players():
            players_infos.append(
                dict(
                    code=p.participant.code,
                    label=p.participant.label,
                    nb_success=p.num_successful_sliders
                )
            )
        return dict(players_infos=players_infos)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_successful_sliders = models.IntegerField(initial=0)
    payoff_ecu = models.IntegerField(initial=0)

    def compute_payoff(self):
        if self.num_successful_sliders >= C.REQUIRED_SUCCESS:
            self.payoff_ecu = C.PAYOFF_SUCCESS
        self.payoff = cu(self.payoff_ecu)

        # ✅ Retrieve cumulative total payoff from previous tasks
        previous_total = self.participant.vars.get("total_payoff", 0)

        # ✅ Update cumulative total by adding this task's payoff
        self.participant.vars["total_payoff"] = previous_total + float(self.payoff)

        txt_final = (f"Il fallait valider {C.REQUIRED_SUCCESS} grilles, et vous en avez validé "
                     f"{self.num_successful_sliders}. <br/>")
        if self.num_successful_sliders >= C.REQUIRED_SUCCESS:
            txt_final += f"Vous pouvez continuer l'expérience, avec une dotation de {self.payoff_ecu} ECU."
        else:
            txt_final += f"Vous ne pouvez pas poursuivre l'expérience."

        self.participant.vars["slider_task"] = dict(
            txt_final=txt_final,
            payoff_ecu=self.payoff_ecu,
            payoff=self.payoff,
            total_payoff=self.participant.vars["total_payoff"]  # ✅ Store cumulative payoff
        )


# ======================================================================================================================
#
# -- PAGES
#
# ======================================================================================================================
def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    txt = f"{minutes} minutes"
    if seconds > 0:
        txt += f" et {seconds} secondes"
    return txt

def common_vars(player: Player):
    return dict(
        time_limit=format_time(C.TIME_LIMIT),
        fill_auto=player.session.config.get("fill_auto", False),
    )


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {**common_vars(player)}


class Slider(Page):
    timeout_seconds = C.TIME_LIMIT
    form_model = "player"
    form_fields = ["num_successful_sliders"]

    @staticmethod
    def vars_for_template(player: Player):
        return {**common_vars(player)}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # il ne faut pas mettre de timeout_happened car il y a un timer
        player.compute_payoff()


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {**common_vars(player)}


page_sequence = [Instructions, Slider, Results]