from otree.api import Bot
import random
from . import Decision, Result  # ✅ Import from the current module (init)

class PlayerBot(Bot):
    def play_round(self):
        profile = self.participant.vars.get('profile', {})
        risk = profile.get('risk_aversion', 'medium')

        if risk not in ['low', 'medium', 'high']:
            print(f"[WARN] Unknown risk_aversion '{risk}' → defaulting to medium")
            risk = 'medium'

        if risk == 'low':
            n = random.randint(70, 100)
        elif risk == 'high':
            n = random.randint(5, 35)
        else:
            n = random.randint(35, 70)

        print(f"Bot risk profile: {risk}, chose to open {n} boxes.")

        yield Decision, dict(n_boxes=n)
        yield Result
