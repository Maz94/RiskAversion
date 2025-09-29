from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'Consent_form'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    
def creating_session(subsession):
    import random
    for p in subsession.get_players():
        p.participant.vars['profile'] = {
            'risk_aversion': random.choice(['low', 'medium', 'high']),
            'knowledge_level': random.choice(['basic', 'intermediate', 'advanced']),
            'environmental_values': random.randint(1, 7),
            'social_values': random.randint(1, 7),
            'demographics': {
                'age': random.randint(18, 70),
                'gender': random.choice(['male', 'female', 'non-binary']),
                'education': random.choice(['high school', 'bachelor', 'master', 'PhD']),
            }
        }
        p.participant.vars['total_payoff'] = 0  # to accumulate across all apps

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent_given = models.BooleanField(
        label="Je m'engage à participer aux deux sessions et à respecter les conditions énoncées.",
        widget=widgets.CheckboxInput
    )
    withdrawn = models.BooleanField(initial=False)  # This field must exist