from otree.api import Page
from .models import Player

class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'education', 'study_field',
        'risk_tolerance', 'patience', 'altruism','climate_concern',
        'human_impact','environmental_concern' ,'responsibility_environment',
        'economic_vs_environment','nature_resilience' ,'eco_spending',
        'investment_environment','lower_return', 'investment_impact','investment_priority',
        'climate_consequences'

    ]
    def vars_for_template(self):

        return {
            "min_time_seconds": 5,

        }

    def before_next_page(self):
        profile = self.participant.vars.get('profile', {})
        profile.update({
            'age': self.player.age,
            'gender': self.player.gender,
            'education': self.player.education,
            'study_field': self.player.study_field,
            'risk_tolerance': self.player.risk_tolerance,
            'patience': self.player.patience,
            'altruism': self.player.altruism,
            'climate_concern': self.player.climate_concern,
            'human_impact': self.player.human_impact,
            'environmental_concern': self.player.environmental_concern,
            'responsibility_environment': self.player.responsibility_environment,
            'economic_vs_environment': self.player.economic_vs_environment,
            'nature_resilience': self.player.nature_resilience,
            'eco_spending': self.player.eco_spending,
            'investment_environment': self.player.investment_environment,
            'lower_return': self.player.lower_return,
            'investment_impact': self.player.investment_impact,
            'investment_priority': self.player.investment_priority,
            'climate_consequences': self.player.climate_consequences,
        })
        self.participant.vars['profile'] = profile


page_sequence = [Demographics]
