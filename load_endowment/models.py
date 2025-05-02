from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'load_endowment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    CSV_FILE = '/Users/amazigh/PycharmProjects/oTree/pythonProject/test1/_static/global/data.csv'  # Path to the CSV file


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    phone_last_4_digits = models.StringField(
        label="Please enter the last 4 digits of your phone number",
        max_length=4,
        min_length=4,
    )
    endowment = models.CurrencyField(initial=0)  # Will be loaded from the CSV
