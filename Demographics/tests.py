from otree.api import Bot
from .pages import Demographics
import random

class PlayerBot(Bot):
    def play_round(self):
        profile = self.participant.vars.get('profile', {})

        yield Demographics, dict(
            age=profile.get('age', random.randint(18, 65)),
            gender=profile.get('gender', random.choice(['male', 'female', 'non-binary'])),
            education=profile.get('education', random.choice(['high school', 'bachelor', 'master', 'PhD'])),
            study_field=profile.get('study_field', 'Economics'),
            risk_tolerance=profile.get('risk_tolerance', random.randint(1, 10)),
            patience=profile.get('patience', random.randint(1, 10)),
            altruism=profile.get('altruism', random.randint(1, 10)),
            climate_concern=profile.get('climate_concern', random.randint(1, 10)),
            human_impact=profile.get('human_impact', random.randint(1, 10)),
            environmental_concern=profile.get('environmental_concern', random.randint(1, 10)),
            responsibility_environment=profile.get('responsibility_environment', random.randint(1, 10)),
            economic_vs_environment=profile.get('economic_vs_environment', random.randint(1, 10)),
            nature_resilience=profile.get('nature_resilience', random.randint(1, 10)),
            eco_spending=profile.get('eco_spending', random.randint(1, 10)),
            investment_environment=profile.get('investment_environment', random.randint(1, 10)),
            lower_return=profile.get('lower_return', random.randint(1, 10)),
            investment_impact=profile.get('investment_impact', random.randint(1, 10)),
            investment_priority=profile.get('investment_priority', random.randint(1, 10)),
            climate_consequences=profile.get('climate_consequences', random.randint(1, 10)),
        )
