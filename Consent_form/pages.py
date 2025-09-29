from otree.api import Currency as c, currency_range
from ._builtin import Page
from .models import Player

class ConsentForm(Page):
    form_model = 'player'
    form_fields = ['consent_given']

    def error_message(self, values):
        if self.participant.vars.get("withdrawn", False):
            return None  # Skip validation if withdrawn

        if not values.get('consent_given'):
            return "Vous devez cocher cette case pour confirmer votre engagement."

    def before_next_page(self):
        if self.participant.vars.get("withdrawn", False):
            self.player.withdrawn = True


page_sequence = [ConsentForm]
