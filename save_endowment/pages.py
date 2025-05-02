from .models import Player, generate_random_alias  # ✅ Import the function

from otree.api import *
from .models import get_endowment_from_db  # ✅ Import DB function


class EnterAlias(Page):
    form_model = 'player'
    form_fields = ['alias_code']

    def error_message(player, values):
        alias = values.get('alias_code')

        if not alias:
            return "Veuillez entrer un alias (entre 4 et 6 caractères) ou en générer un de manière aléatoire."
        if not (4 <= len(alias) <= 6):
            return "L'alias doit contenir entre 4 et 6 caractères."

        # ✅ Check if alias is already in use
        for p in player.session.get_participants():
            if p.vars.get('alias_code') == alias and p.code != player.participant.code:
                return "Cet alias est déjà utilisé. Veuillez en choisir un autre."

        # ✅ Store alias
        player.participant.vars['alias_code'] = alias
        player.alias_code = alias
        return None

    def vars_for_template(player):
        """✅ Pass a random alias to the template in case they want to generate one"""
        return {
            'random_alias': generate_random_alias()
        }

class EnterPhoneNumber(Page):
    form_model = 'player'
    form_fields = ['phone_last_4_digits']

    def error_message(self, values):
        phone_digits = values.get('phone_last_4_digits')

        # ✅ 1. Format check
        if len(phone_digits) != 4 or not phone_digits.isdigit():
            return "Veuillez entrer exactement 4 chiffres."

        # ✅ 2. Check for duplicates in the current session
        for p in self.session.get_participants():
            if p.vars.get('phone_number') == phone_digits and p.code != self.participant.code:
                return "Ce numéro est déjà utilisé par un autre participant. Veuillez entrer un autre."

        # ✅ 3. Check for duplicates in the database
        try:
            existing = get_endowment_from_db(phone_number=phone_digits)
            if existing:
                return "Ce numéro a déjà été utilisé dans une autre session. Veuillez en choisir un autre."
        except Exception as e:
            print(f"❌ Erreur lors de la vérification en base : {e}", flush=True)
            return "Erreur technique lors de la vérification. Veuillez réessayer."

        # ✅ 4. If all good, store the digits (for saving later)
        self.player.phone_last_4_digits = phone_digits
        return None

    def before_next_page(self):
        """✅ Save participant data before proceeding."""

        total_payoff = round(float(self.player.participant.payoff), 2)  # ✅ Keeps decimals
        self.player.total_payoff = total_payoff
        self.player.endowment = total_payoff


class Engagement(Page):
    pass

class Results(Page):
    def vars_for_template(self):
        total = self.participant.vars.get("total_payoff", 0)

        return {
            "alias_code": self.player.alias_code,
            "phone_last_4_digits": self.player.phone_last_4_digits,
            "total_payoff":  "{:.2f}".format(total)  # ✅ Format to 2 decimals

        }

    def before_next_page(self):
        print("✅ Saving data at the end of session...", flush=True)
        self.player.save_participant_data()  # ✅ Call saving function


    def before_next_page(self):
        self.player.save_participant_data()  # ✅ Call saving function

page_sequence = [
    EnterAlias,
    EnterPhoneNumber,
    Engagement,
    Results,
]