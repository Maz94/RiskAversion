from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c
)

class C(BaseConstants):
    NAME_IN_URL = 'Demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    age = models.IntegerField(label='Quel est votre âge ?', min=18, max=99)

    gender = models.StringField(
        choices=[['Homme', 'Homme'], ['Femme', 'Femme'], ['Autre', 'Autre']],
        label='Quel est votre genre ?',
        widget=widgets.RadioSelect
    )

    education = models.IntegerField(
        choices=[
            [1, 'Étudiant(e) en première année de licence'],
            [2, 'Étudiant(e) en deuxième année de licence'],
            [3, 'Étudiant(e) en troisième année de licence'],
            [4, 'Étudiant(e) en master'],
            [5, 'Autre']
        ],
        label='Actuellement, je suis',
        widget=widgets.RadioSelect
    )

    study_field = models.IntegerField(
        choices=[
            [1, 'Arts, Humanités ou Langues'],
            [2, 'Économie'],
            [3, 'Sciences sociales'],
            [4, 'Ingénierie ou Sciences physiques'],
            [5, 'Informatique ou Science des données'],
            [6, 'Droit, Médecine ou Dentisterie'],
            [7, 'Autre']
        ],
        label='Quel domaine d’étude décrit le mieux votre spécialisation ?',
        widget=widgets.RadioSelect
    )

    # Behavioral Preferences
    risk_tolerance = models.IntegerField(
        label="Je préfère un gain modéré garanti plutôt qu’une opportunité de gagner plus avec un risque de perte",
        choices=[[1, 'Non, jamais'], [2, 'Plutôt non'], [3, 'Neutre'], [4, 'Plutôt oui'], [5, 'Oui, toujours']],
        widget=widgets.RadioSelect)
    patience = models.IntegerField(
        label='Je suis capable d’économiser pour atteindre un objectif financier à long terme',
        choices=[[1, 'Jamais'], [2, 'Rarement'], [3, 'Neutre'], [4, 'Souvent'],[5, 'Toujours']],
        widget=widgets.RadioSelect)
    altruism = models.IntegerField(
        label='Je suis prêt(e) à aider un(e) inconnu(e) en difficulté sans attendre de contrepartie',
        choices=[[1, 'Non, jamais'], [2, 'Plutôt non'], [3, 'Neutre'], [4, 'Plutôt oui'], [5, 'Oui, toujours']],
        widget=widgets.RadioSelect)

    # Environmental Preferences
    climate_concern = models.IntegerField(
        label='Le changement climatique est un problème sérieux',
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )
    human_impact = models.IntegerField(
        label="L'humain a un impact sur le climat ",
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )






    environmental_concern = models.IntegerField(
        label='Votre préoccupation environnementale ?',
        choices=[[1, 'Pas du tout'], [2, 'Peu'], [3, 'Neutre'], [4, 'Assez'],
                 [5, 'Très']],
        widget=widgets.RadioSelect)

    responsibility_environment = models.IntegerField(
        label='Il est de ma responsabilité personnelle de protéger l’environnement ',
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect)






    eco_spending = models.IntegerField(
        label='Je suis prêt(e) à payer plus cher pour un produit écologique ',
        choices=[[1, 'Non'], [2, 'Plutôt non'], [3, 'Neutre'], [4, 'Plutôt oui'], [5, 'Oui']],
        widget=widgets.RadioSelect
    )

    investment_environment = models.IntegerField(
        label="Je prends en compte l’impact écologique d’un investissement ",
        choices=[[1, 'Pas du tout'], [2, 'Un peu'], [3, 'Neutre'], [4, 'Assez'], [5, 'Beaucoup']],
        widget=widgets.RadioSelect
    )

    lower_return = models.IntegerField(
        label="Je suis prêt(e) à accepter un rendement inférieur pour plus de durabilité ",
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )

    investment_impact = models.IntegerField(
        label="Les investissements responsables ont un impact positif sur l'environnement",
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )
    economic_vs_environment = models.IntegerField(
        label='Priorité à l’économie vs environnement ?',
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )

    nature_resilience = models.IntegerField(
        label='Capacité de la nature à se régénérer ?',
        choices=[[1, 'Pas du tout d’accord'], [2, 'Plutôt pas d’accord'], [3, 'Neutre'], [4, 'Plutôt d’accord'],
                 [5, 'Tout à fait d’accord']],
        widget=widgets.RadioSelect
    )

    investment_priority = models.StringField(
        choices=[
            ('financial', 'Rendement financier'),
            ('stability', 'Stabilité & faible risque'),
            ('impact', 'Impact social & environnemental'),
            ('reputation', 'Réputation de l’entreprise'),
            ('diversification', 'Diversification du portefeuille'),
        ],
        label="Facteur clé dans vos investissements ?",
        widget=widgets.RadioSelect,
        blank=True
    )

    climate_consequences = models.StringField(
        choices=[
            ('catastrophes', 'Catastrophes naturelles'),
            ('biodiversite', 'Perte de biodiversité'),
            ('social', 'Impact économique & social'),
            ('ressources', 'Accès aux ressources naturelles'),
            ('not_concerned', 'Pas concerné(e)'),
        ],
        label="Conséquence climatique la plus préoccupante ?",
        widget=widgets.RadioSelect,
        blank=True
    )
