from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import csv
from MPLTEST.config import *
import random
from random import randrange
import json
import copy

author = 'Amazigh Ferhati'

doc = """
Multiple price list task as proposed by Holt/Laury (2002), American Economic Review 92(5).
"""



# ********************************************************************************************************************#
# *** CLASS SUBSESSION
# ********************************************************************************************************************#
class Subsession(BaseSubsession):
    def creating_session(self):
        n = int(Constants.num_choices) # Number of choices per round
        m = int(Constants.num_tasks)# Number of rounds



        for p in self.get_players():
            # Randomly assign treatment
            assigned_treatment = 'green' if p.id_in_group % 2 == 0 else 'brown'
            p.participant.vars['treatment'] = assigned_treatment

            # Debugging (Optional)
            print(f"Participant {p.id_in_group} assigned to {assigned_treatment} treatment")

            # Initialize overall choice tracking lists

            p.participant.vars['mpl_choices'] = []
            p.participant.vars['choices_made'] = []

            # Create a list of round indices
            round_indices = list(range(m))

            # Shuffle the full list of tuples after all rounds (if enabled)

            if Constants.condition_to_shuffle:
                round_indices = round_indices.copy()  # Copy to avoid modifying the original list
                random.shuffle(round_indices)  # Now it's safe to shuffle

            # Store the shuffled order for each participant
            p.participant.vars['round_order'] = copy.deepcopy(round_indices)
            p.participant.vars['current_round_index'] = 0

            print("Round indices (shuffled):", round_indices)

            # Copy lists first to avoid modifying Constants directly
            x1_copy = Constants.x1.copy()
            x2_copy = Constants.x2.copy()
            p1_copy = Constants.p1.copy()
            p2_copy = Constants.p2.copy()
            y_copy = Constants.y.copy()
            externality_risky_copy = Constants.externality_risky.copy()
            externality_safe_copy = Constants.externality_safe.copy()

            # Loop through the randomized round indices
            for round_index in round_indices:
                print(f"Processing Round {round_index + 1} for Participant {p.id_in_group}")

                # Retrieve current values for this round by indexing the copied lists
                current_x1 = c(x1_copy[round_index])
                current_x2 = c(x2_copy[round_index])
                current_p1 = p1_copy[round_index]
                current_p2 = p2_copy[round_index]
                current_y = c(y_copy[round_index])

                if assigned_treatment == 'green':
                    current_externality_risky = (
                            c(externality_risky_copy[round_index]) * c(Constants.externality_value)
                    )
                    current_externality_safe = (
                            c(externality_safe_copy[round_index]) * c(Constants.externality_value)
                    )
                else:  # Brown treatment
                    current_externality_risky = (
                            c(externality_risky_copy[round_index]) * (-c(Constants.externality_value))
                    )
                    current_externality_safe = (
                            c(externality_safe_copy[round_index]) * (-c(Constants.externality_value))
                    )

                decrement_amount = Constants.decrement_amount
                indices_choices = list(range(1, n + 1))

                p1_list = ["{0:.2f}".format(current_p1 * 100) + "%"] * n
                p2_list = ["{0:.2f}".format(current_p2 * 100) + "%"] * n
                lottery_hi = [current_x1] * n
                lottery_lo = [current_x2] * n
                externality_risky = [current_externality_risky] * n
                externality_safe = [current_externality_safe] * n

                # Decrement or increment the safe outcome for each choice
                safe_outcome_list = [
                    (current_y - (i * decrement_amount)) if current_y > 0
                    else (current_y + (i * decrement_amount))
                    for i in reversed(range(n))
                ]

                # Generate unique form fields
                form_fields = [f'choice_{round_index + 1}_{k}' for k in range(1, n + 1)]

                # Compile choices for this round into tuples
                round_choices = list(
                    zip(indices_choices, form_fields, lottery_hi, p1_list, lottery_lo, p2_list, safe_outcome_list,
                        externality_risky, externality_safe)
                )

                if Constants.condition_to_shuffle_safe_choices:
                    round_choices = round_choices.copy()  # Copy to avoid modifying the original list
                    random.shuffle(round_choices)
                    print(f"Shuffling safe choices for Round {round_index + 1}...")



            # Store shuffled round choices in participant vars
                round_var_name = f'mpl_choices_round_{round_index + 1}'
                p.participant.vars[round_var_name] = round_choices

                p.participant.vars['mpl_choices'].extend(round_choices)

                print(f"Stored {round_var_name} for Participant {p.id_in_group}: {p.participant.vars[round_var_name]}")

            # Debugging: Print the full list after shuffling
            print("\nShuffled mpl_choices for Participant:")
            print("{:<5} {:<15} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                "Index", "Choice", "High", "p1", "Low", "p2", "Safe", "Ext_Risky", "Ext_Safe"))
            for choice in p.participant.vars['mpl_choices']:
                print("{:<5} {:<15} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    choice[0], choice[1], choice[2], choice[3], choice[4], choice[5], choice[6], choice[7], choice[8]))


# ******************************************************************************************************************** #
# *** CLASS GROUP
# ******************************************************************************************************************** #
class Group(BaseGroup):
    pass


# ******************************************************************************************************************** #
# *** CLASS PLAYER
# ******************************************************************************************************************** #
class Player(BasePlayer):

    label = models.StringField()

    entry_code = models.StringField(label="Veuillez entrer le code fourni par l'expérimentateur.")

    page_pass_time = models.FloatField(blank=True)  # Allow None initially

    alias_code = models.StringField(
        blank=True,
        label="Entrez votre alias unique généré lors de la précédente session"
    )
    move_to_next = models.BooleanField(initial=False)  # Tracks if "Next" button is clicked
    phone_last_4_digits = models.StringField(
        label="Si vous avez oublié votre alias, entrez les 4 derniers chiffres de votre numéro de téléphone",
        max_length=4,
        min_length=4
    )
    # First Session Earnings  & Amount Brought
    endowment = models.CurrencyField(initial=0)  # Will be loaded from the CSV
    #
    decision_payoff = models.CurrencyField(initial=0)
    #
    final_earnings = models.CurrencyField(initial=0)
    # Total Externality Generated
    total_externality = models.CurrencyField(initial=0)


    # Declared First Session Earnings  & Amount Brought
    first_session_earnings = models.CurrencyField(
        label="Combien d\'argent aviez-vous gagné lors de la première session ?",
        min=0
    )
    amount_brought = models.CurrencyField(
        label="Combien d\'argent avez-vous apporté aujourd’hui pour cette session ?",
        min=0
    )
    reason_for_difference = models.LongStringField(
        label="Si le montant que vous avez apporté est différent de celui gagné lors de la première session, veuillez expliquer pourquoi.",
        blank=True
    )



    equivalent_expense = models.StringField(
        label="Si vous deviez comparer ce montant à une dépense quotidienne, laquelle serait-ce ?",
        choices=[
            "Un repas au restaurant",
            "Un panier de courses pour quelques jours",
            "Une facture (électricité, internet, etc.)",
            "Un abonnement mensuel (Netflix, salle de sport, forfait téléphonique)"
        ],
        widget=widgets.RadioSelect
    )



    pain_of_losing = models.IntegerField(
        label="Si vous perdiez cet argent, à quel point cela vous affecterait-il ?",
        min=1, max=7
    )





    emotional_attachment = models.IntegerField(
        label="À quel point vous sentez-vous attaché(e) à \'argent gagné lors de la première session ?",
        min=1, max=7
    )

    strategy_change = models.StringField(
        label="Allez-vous modifier votre stratégie par rapport à la première session ?",
        choices=[
            "Oui, je vais être plus prudent(e)",
            "Oui, je vais prendre plus de risques",
            "Non, je vais adopter la même stratégie",
            "Je ne sais pas encore"
        ],
        widget=widgets.RadioSelect
    )




    question1 = models.StringField(
        choices=[('option1', '0 €, et une externalité est générée.'), ('option2', '50 €, et une externalité est générée.')],
        label="Si le faible résultat se produit (70 % de chance) dans l'option A, que recevrez-vous ?",
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        choices=[('option1', 'Vrai'), ('option2', 'Faux')],
        label="Vrai ou Faux : Vous êtes responsable du paiement du coût de l'externalité générée par l'option A.",
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        choices=[('option1', '-20 €, et une externalité est générée.'), ('option2', "-20 €, et aucune externalité n'est générée.")],
        label="Si vous choisissez l'Option B, quel est le résultat ?",
        widget=widgets.RadioSelect
    )
    question4 = models.StringField(
        choices=[('option1', 'Vrai'), ('option2', 'Faux')],
        label="Vrai ou Faux : Des externalités sont générées par l'option A et l'option B dans ce scénario.",
        widget=widgets.RadioSelect
    )
    question5 = models.StringField(
        choices=[('option1', '0€'), ('option2', '0€, sans externalité')],
        label="Si l'option A aboutit au résultat élevé, que recevrez-vous ?",
        widget=widgets.RadioSelect
    )
    question6 = models.StringField(
        choices=[('option1', "L'externalité est toujours générée"), ('option2', 'Aucune externalité n\'est générée')],
        label="Si l'option A aboutit à 0 €, que se passe-t-il avec l'externalité ?",
        widget=widgets.RadioSelect
    )
    question7 = models.StringField(
        choices=[('option1', 'Vrai'), ('option2', 'Faux')],
        label="Vrai ou Faux: Votre capital initial gagné lors de la session précédente sera utilisé au cours de l’expérience.",
        widget=widgets.RadioSelect
    )
    question8 = models.StringField(
        choices=[('option1', '10kg'), ('option2', '5kg'), ('option3', '20kg')],
        label="Le projet South Pole finance des initiatives environnementales en réduisant les émissions de CO₂. Selon vous, combien de kilogrammes de CO₂ peuvent être compensés par un don de 5€ ?",
        widget=widgets.RadioSelect
    )
    question9 = models.StringField(
        choices=[('option1', 'Vrai'), ('option2', 'Faux')],
        label="Vrai ou Faux: Dans cette expérience, en fonction de vos décisions et du hasard, vous pouvez aussi perdre de l’argent et terminer l’expérience avec moins d’argent que ce que vous aviez au départ.",
        widget=widgets.RadioSelect
    )
    comprehension_attempts = models.IntegerField(initial=0)

    comprehension_errors = models.IntegerField(initial=0)
    # Store choices made as a JSON string
    choices_made = models.LongStringField(
        doc="Stores the list of choices made by the player during the experiment"
    )
    # Store the randomly selected choices for payoff
    selected_choices = models.LongStringField(
        doc="Stores the randomly selected choices for payoff"
    )
    # Store detailed results for each draw (lottery outcomes and payoffs)
    detailed_results = models.LongStringField(
        doc="Detailed results showing draw, payoff, and externality"
    )

    practice_choice = models.StringField(
        choices=['Safe', 'Risky'],
        widget=widgets.RadioSelect,
        label="Which option do you choose?"
    )
    comprehension_answer = models.StringField(
        label="What was the result of the last draw?"
    )


    def has_reached_max_attempts(self):
        return self.comprehension_attempts >= 2

    # Dynamically create fields for each choice
    for task_number in range(1, Constants.num_tasks + 1):
        for choice_number in range(1, Constants.num_choices + 1):
            locals()[f'choice_{task_number}_{choice_number}'] = models.StringField(
                choices=['Safe', 'Risky'],
                doc=f"Player's decision for task {task_number}, choice {choice_number}.",
                widget=widgets.RadioSelect
            )
    del task_number, choice_number

    # Satisfaction with the final payoff
    satisfaction = models.IntegerField(
        label="Comment évaluez-vous votre satisfaction par rapport à vos gains finaux ?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal
    )

    # Perceived contribution to the environment
    env_contribution = models.IntegerField(
        label="Pensez-vous avoir contribué de manière positive à l’environnement au cours de cette expérience ?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal
    )



    # Influence of externalities on decisions
    externalities_influence = models.IntegerField(
        label="À quel point les externalités ont-elles influencé vos choix ?",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal
    )

    factors_influencing_choices = models.StringField(
        label="Quels éléments ont le plus influencé vos décisions aujourd\'hui ?",
        choices=[
            "Maximiser mes gains",
            "Éviter de perdre de l\'argent",
            "L\'impact environnemental",
            "L\'impact social",
            "Je privilégie la sécurité à l\'incertitude",
            "Autre"
        ],
        widget=widgets.RadioSelect
    )


    # Open-ended response: Any additional comments
    comments = models.LongStringField(
        label="Avez-vous des commentaires sur l’expérience ou le système de rémunération ?",
        blank=True
    )




    # Additional fields for the player's decisions and results
    task_index = models.IntegerField(initial=0)
    random_draw = models.IntegerField(
        doc="Random draw to determine whether to pay the 'high' or 'low' outcome of the randomly picked lottery."
    )
    choice_to_pay = models.StringField(
        doc="Choice to pay for the participant, determined at random."
    )

    inconsistent = models.IntegerField(
        initial=0,
        doc="Indicator for inconsistent choices (1 if inconsistent, 0 if consistent)."
    )
    switching_row = models.IntegerField(
        doc="The switching row where the participant switches from Safe to Risky."
    )




    # Determine consistency of choices
    #
    #
    #    def set_consistency(self):
    #    n = Constants.num_choices * Constants.num_tasks  # Total number of choices

        # Replace 'Safe' with 1 and 'Risky' with 0 for consistency check
    #   self.participant.vars['mpl_choices_made'] = [
    ##       1 if j == 'Safe' else 0 for j in self.participant.vars['mpl_choices']
    #   ]

        # Check for multiple switching behavior (inconsistency)
    #  for j in range(1, n):
    #    choices = self.participant.vars['mpl_choices_made']
    #    self.inconsistent = 1 if choices[j] > choices[j - 1] else 0
    #     if self.inconsistent == 1:
    #          break

    # Determine the switching row
    def set_switching_row(self):
        # Set switching point to the row number of the first 'Risky' choice
        if self.inconsistent == 0:
            self.switching_row = sum(self.participant.vars['mpl_choices_made']) + 1

