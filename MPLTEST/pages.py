from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Player
from .config import get_endowment_from_db  # ✅ Import DB function
from .config import Constants
import random
import json
import copy
from decimal import Decimal
import time
import csv
from otree.api import Currency  # Ensure Currency is imported from oTree
# ******************************************************************************************************************** #
# *** PAGE DECISION *** #
# ******************************************************************************************************************** #
class CurrencyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Currency):
            return float(obj)
        return super().default(obj)

class Introduction(Page):
    def vars_for_template(self):

        return {
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Introduction"],

        }

class EnterAlias(Page):
    form_model = 'player'

    def get_form_fields(self):
        """If alias is already taken, show only the 'move_to_next' button."""
        if self.participant.vars.get('alias_conflict', False):
            return ['move_to_next']
        return ['alias_code']

    def error_message(self, values):
        alias = values.get('alias_code')

        if self.participant.vars.get('alias_conflict', False):
            return None  # Skip validation if alias is not mandatory

        # ✅ Check if alias already exists in session
        for p in self.session.get_participants():
            if p.vars.get('alias_code') == alias and p.code != self.participant.code:
                self.participant.vars['alias_conflict'] = True
                return "Cet alias a déjà été utilisé. Veuillez passer à l'étape suivante."

        self.participant.vars['alias_conflict'] = False  # No conflict
        return None

    def vars_for_template(self):
        """Pass a flag to show the 'Next' button if there's a conflict."""
        return {'show_next_button': self.participant.vars.get('alias_conflict', False)}

    def before_next_page(self):
        """Fetch endowment based on alias, else move to phone number lookup."""
        if self.player.move_to_next:
            self.participant.vars['alias_conflict_resolved'] = True
            return

        alias = self.player.alias_code
        self.participant.vars['alias'] = alias
        if alias:
            self.participant.vars['alias_code'] = alias

            # ✅ Fetch endowment from PostgreSQL
            fetched_data = get_endowment_from_db(alias=alias)

            # ✅ Store data
            self.player.label = self.participant.vars['alias']
            if fetched_data:
                self.player.endowment = fetched_data["endowment"]
                self.participant.vars['endowment'] = fetched_data["endowment"]
                self.participant.vars['phone_number'] = fetched_data["phone_number"]
            else:
                self.participant.vars['endowment'] = None  # Indicate no endowment

class EnterPhoneNumber(Page):
    form_model = 'player'
    form_fields = ['phone_last_4_digits']

    def is_displayed(self):
        """Show this page only if alias lookup failed."""
        return self.participant.vars.get('endowment') is None

    def error_message(self, values):
        phone_digits = values.get('phone_last_4_digits')

        # Ensure input is exactly 4 digits
        if len(phone_digits) != 4 or not phone_digits.isdigit():
            return "Veuillez entrer exactement 4 chiffres."

        # ✅ Check for duplicates within current session
        for p in self.session.get_participants():
            if p.vars.get('phone_number') == phone_digits and p.code != self.participant.code:
                return "Ce numéro est déjà utilisé par un autre participant. Veuillez entrer un autre."

        # ✅ Fetch endowment from DB
        fetched_data = get_endowment_from_db(phone_number=phone_digits)

        if not fetched_data:
            return "Aucun participant correspondant trouvé avec ces 4 chiffres. Veuillez réessayer."

        # ✅ If valid, store the endowment
        self.player.endowment = fetched_data["endowment"]
        self.participant.vars['endowment'] = fetched_data["endowment"]
        self.participant.vars['phone_number'] = fetched_data["phone_number"]
        return None



class DisplayEndowment(Page):

    def vars_for_template(self):
        return {
            'endowment': c(self.participant.vars.get('endowment', 0)),
        }

class WaitForExperimenter(Page):
    """Participants wait until they receive the predefined code from the experimenter."""

    form_model = 'player'
    form_fields = ['entry_code']

    def is_displayed(self):
        return not self.participant.vars.get('verified', False)  # Stay here until verified

    def error_message(self, values):
        correct_code = Constants.PREDEFINED_CODE  # Use the predefined code
        if values['entry_code'] != correct_code:
            return "Code incorrect. Veuillez réessayer."
        else:
            self.participant.vars['verified'] = True  # ✅ Mark as verified immediately


    def vars_for_template(self):
        return {
            'endowment': c(self.participant.vars.get('endowment', 0)),
        }


class Questionnaire(Page):
    form_model = 'player'
    form_fields = [
        'first_session_earnings', 'amount_brought', 'reason_for_difference',
         'equivalent_expense',
        'pain_of_losing',   'emotional_attachment',
        'strategy_change'
    ]

    def vars_for_template(self):
        return {
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Questionnaire"],
            "use_sliders": True,
            "slider_questions": [
                ("pain_of_losing", "Si vous perdiez cet argent, à quel point cela vous affecterait-il ?"),
                ("emotional_attachment", "À quel point vous sentez-vous émotionnellement attaché(e) à l'argent gagné lors de la première session ?")
            ]
        }

    def error_message(self, values):
        # Ensure an explanation is provided and contains at least 30 characters
        if float(values["first_session_earnings"]) != float(values["amount_brought"]):
            if not values["reason_for_difference"] or len(values["reason_for_difference"].strip()) < 30:
                return "Veuillez fournir une explication d'au moins 30 caractères si le montant apporté est différent de celui gagné."

class Instructions(Page):

    def is_displayed(self):
        # Only display instructions in round 1
        return self.subsession.round_number == 1

    def vars_for_template(self):
        return {
            'num_choices': len(self.participant.vars.get('mpl_choices', [])),
            'treatment': self.participant.vars.get('treatment', 'neutral'),
            'num_payoff': Constants.num_payoff,
            'endowment': c(self.participant.vars.get('endowment', 0)),
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Instructions"]


        }

class Comprehension(Page):

    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3', 'question4', 'question5', 'question6', 'question7', 'question8', 'question9']
    # Define explanations for incorrect answers
    explanations = {
        'question1': "Dans l'Option A, si l'issue défavorable se produit, vous recevez 0 €, mais l'externalité s'applique toujours.",
        'question2': "L'externalité est prise en charge par l'expérimentateur, pas par vous. Les externalités n'affectent pas votre gain final.",
        'question3': "Dans ce scénario, l'option sûre entraîne une perte de -20 €, mais ne génère pas d'externalité.",
        'question4': "Dans ce scénario, seule l'Option A génère une externalité.",
        'question5': "Dans ce scénario, l'issue élevée de l'Option A est de 0 €. ",
        'question6': "Même si vous recevez 0 € en choisissant l'Option A, l'externalité est produite indépendamment du résultat monétaire.",
        'question7': "Vrai, l'argent gagné lors de la session précédente sera utilisée lors de cette seconde session.",
        'question8': "Une donation de 5€ équivaut à une compensation de 5kg de CO2.",
        'question9': "Votre capital initial peut être affecté par vos décisions, et dans certaines situations, vous pourriez terminer l’expérience avec moins d’argent que ce que vous aviez au départ."
    }


    def get_form_fields(self):
        # If you need dynamic form fields, calculate them here
        return self.form_fields
    def vars_for_template(self):
        # Extract the first 3 lotteries for comprehension
        comprehension_lotteries = Constants.practice_lotteries[:3]
        # Apply externality multiplier based on treatment
        treatment_multiplier = 3 if self.participant.vars.get('treatment') == 'green' else -3
        # Extract relevant data as lists and format for display
        lottery_hi = [f"{float(lottery['x1']):.0f}" for lottery in comprehension_lotteries]  # Format as integer string
        lottery_lo = [f"{float(lottery['x2']):.0f}" for lottery in comprehension_lotteries]
        p1 = [int(lottery['p1'] * 100) for lottery in comprehension_lotteries]  # Convert to percentage
        p2 = [int(lottery['p2'] * 100) for lottery in comprehension_lotteries]
        safe_outcome = [float(lottery['y']) for lottery in comprehension_lotteries]
        ext_risky = [int(lottery['externality_risky_practice']*treatment_multiplier) for lottery in comprehension_lotteries]
        ext_safe = [int(lottery['externality_safe_practice']*treatment_multiplier) for lottery in comprehension_lotteries]





        return {
            'task_number': self.player.task_index + 1,
            'lottery_hi': lottery_hi,
            'lottery_lo': lottery_lo,
            'p1': p1,
            'p2': p2,
            'safe_outcome': safe_outcome,
            'ext_risky': ext_risky,
            'ext_safe': ext_safe,
            'formfields': self.form_fields,  # Use form_fields directly
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Comprehension"],
            'treatment': self.participant.vars.get('treatment', 'neutral'),

        }

    def error_message(self, values):
        correct_answers = {
            'question1': 'option1',
            'question2': 'option2',
            'question3': 'option2',
            'question4': 'option2',
            'question5': 'option1',
            'question6': 'option1',
            'question7': 'option1',
            'question8': 'option2',
            'question9': 'option1'
        }

        errors = []

        for field, correct in correct_answers.items():
            if values[field] != correct:
                explanation = self.explanations.get(field, "Vérifiez vos réponses s'il vous plaît.")
                errors.append(
                    f"<p>- La réponse à la {field.replace('question', 'question ')} est incorrecte: {explanation}</p>")

        # Allow progress if no errors
        if not errors:
            self.participant.vars['comprehension_attempts'] = 0
            return None
        else:
            # Increment attempt counter
            self.participant.vars['comprehension_attempts'] = self.participant.vars.get('comprehension_attempts',0) + 1
            # Store errors in participant vars to persist for the next render
            self.participant.vars['comprehension_errors'] = errors
            # Return errors as separate sentences on new lines
            return "\n".join(errors)  # Join errors with newline characters

class Practice(Page):
    form_model = 'player'

    def get_form_fields(self):
        return ['practice_choice']

    def vars_for_template(self):
        # Translate practice task index (1, 2, 3) to lottery index (4, 5, 6)
        practice_index = self.player.task_index
        lottery = Constants.practice_lotteries[practice_index + 3]  # Start from lottery 4


        # Apply externality multiplier based on treatment
        treatment_multiplier = 3 if self.participant.vars.get('treatment') == 'green' else -3
        ext_risky = lottery['externality_risky_practice'] * treatment_multiplier
        ext_safe = lottery['externality_safe_practice'] * treatment_multiplier

        return {
            'task_number': practice_index + 1,  # Show practice task 1, 2, 3
            'lottery_hi': lottery['x1'],
            'lottery_lo': lottery['x2'],
            'p1': lottery['p1'] * 100,
            'p2': lottery['p2'] * 100,
            'safe_outcome': lottery['y'],
            'ext_risky': ext_risky,
            'ext_safe': ext_safe,
            'treatment': self.participant.vars.get('treatment', 'neutral'),

        }

    def before_next_page(self):
        draw = (random.uniform(0, 1))
        practice_index = self.player.task_index
        lottery = Constants.practice_lotteries[practice_index + 3]  # Correct lottery index

        # Apply externality multiplier
        treatment_multiplier = 3 if self.participant.vars.get('treatment') == 'green' else -3
        ext_risky = lottery['externality_risky_practice'] * treatment_multiplier
        ext_safe = lottery['externality_safe_practice'] * treatment_multiplier

        # Calculate result based on the draw
        if self.player.practice_choice == 'Risky':
            result = lottery['x1'] if draw <= lottery['p1'] else lottery['x2']
            externality_value = ext_risky
        else:
            result = lottery['y']
            externality_value = ext_safe
        # Format the draw as a whole number
        draw_percentage = round(draw * 100)
        # Store practice choices with externalities
        if 'practice_choices' not in self.participant.vars:
            self.participant.vars['practice_choices'] = []

        self.participant.vars['practice_choices'].append({
            'task_number': practice_index + 1,  # Practice task 1, 2, 3
            'choice_made': self.player.practice_choice,
            'lottery_hi': lottery['x1'],
            'lottery_lo': lottery['x2'],
            'p1': lottery['p1'] * 100,
            'p2': lottery['p2'] * 100,
            'safe_outcome': lottery['y'],
            'result': result,
            'draw': draw_percentage,  # Use the formatted draw value
            'ext_risky': ext_risky,
            'ext_safe': ext_safe
        })
        # Progress through practice tasks
        if practice_index < 2:  # Tasks 1, 2, 3 (indexed as 0, 1, 2)
            self.player.task_index += 1
        else:
            self.player.task_index = 0  # Reset for the next phase

class PracticeResults(Page):
    min_time_seconds = []

    def vars_for_template(self):

        # Get all practice choices from participant vars
        practice_choices = self.participant.vars.get('practice_choices', [])
        endowment =  self.participant.vars['endowment']  # Endowment from previous session
        showup=5
        # Filter only the tasks where a choice was made (ignores skipped ones)
        selected_choices = [choice for choice in practice_choices if choice['choice_made']]
        practice_total_payoff= showup + endowment
        # Randomly select one choice from the made selections
        if selected_choices:
            selected_practice = random.choice(selected_choices)
        else:
            selected_practice = None
        return {
            'practice_choices': practice_choices,
            'selected_practice': selected_practice,
            'num_tasks':Constants.num_tasks,
            'num_payoff': Constants.num_payoff,
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["PracticeResults"],
            "endowment" : endowment,
            "showup" : showup,
            "practice_total_payoff":practice_total_payoff,

        }

class Decision(Page):
    form_model = 'player'
    min_time_seconds = []

    def get_form_fields(self):
        n = int(Constants.num_choices)  # Number of choices per round

        # Retrieve the randomized round index
        current_index = self.player.task_index

        # Get the shuffled round order
        shuffled_rounds = copy.deepcopy(self.participant.vars['round_order'])

        # Get the specific round for this page
        task_index = shuffled_rounds[current_index] + 1  # 1-based index for form fields

        # Return form fields for the chosen round
        form_fields = [f'choice_{task_index}_{j}' for j in range(1, n + 1)]
        return form_fields

    def vars_for_template(self):
        # Get the current round index from the shuffled order
        current_index = self.player.task_index
        shuffled_rounds = copy.deepcopy(self.participant.vars['round_order'])
        task_index = shuffled_rounds[current_index]  # Get the current round
        total_tasks = Constants.num_tasks
        task_var_name = f'mpl_choices_round_{task_index + 1}'  # Use 1-based index for retrieval
        progress_percentage = (current_index / total_tasks) * 100

        choices = copy.deepcopy(self.participant.vars.get(task_var_name, []))# Retrieve the choices for this task

        # Retrieve treatment
        treatment = self.participant.vars.get('treatment')  # Default to neutral if not found

        # Extract values for display
        lottery_hi = [float(choice[2]) for choice in choices]
        lottery_lo = [float(choice[4]) for choice in choices]
        p1 = [float(choice[3].strip('%')) for choice in choices]
        p2 = [float(choice[5].strip('%')) for choice in choices]
        safe_outcome = [float(choice[6]) for choice in choices]
        # Retrieve externality values
        externality_risky = [(choice[7]) for choice in choices]
        externality_safe = [(choice[8]) for choice in choices]
        ext_risky = [float(val) for val in externality_risky]
        ext_safe = [float(val) for val in externality_safe]


        return {
            'choices': choices,
            'task_number': current_index + 1,
            'round_number': current_index + 1,
            'lottery_hi': lottery_hi,
            'lottery_lo': lottery_lo,
            'p1': p1,
            'p2': p2,
            'safe_outcome':safe_outcome,
            'externality_safe': externality_safe,
            'externality_risky': externality_risky,
            'ext_risky': ext_risky[0],
            'ext_safe':  ext_safe[0],
            'treatment': treatment,
            'total_tasks': total_tasks,
            'progress_percentage': progress_percentage,
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Decision"],

        }

    def before_next_page(self):
        task_index = self.player.task_index
        shuffled_rounds = copy.deepcopy(self.participant.vars['round_order'])
        round_index = shuffled_rounds[task_index]  # Get the current round index

        # Retrieve the choices for the current round
        task_var_name = f'mpl_choices_round_{round_index + 1}'
        choices = copy.deepcopy(self.participant.vars.get(task_var_name, []))

        # Initialize choices_made list if not already present
        if 'choices_made' not in self.participant.vars:
            self.participant.vars['choices_made'] = []

        # Initialize all_choices_ for participant if not present
        if 'all_choices_' not in self.participant.vars:
            self.participant.vars['all_choices_'] = []
            # Process externalities and choices
        externality_risky = [float(choice[7]) if len(choice) > 7 else 0 for choice in choices]
        externality_safe = [float(choice[8]) if len(choice) > 8 else 0 for choice in choices]

        # Store externalities in participant.vars
        self.participant.vars['Ext Risky'] = externality_risky
        self.participant.vars['Ext Safe'] = externality_safe
        self.participant.vars['ext_display'] = [
            f"+€{ext:.2f}" if ext > 0 else f"€{ext:.2f}" for ext in externality_risky
        ]
        for j, choice in enumerate(choices, start=1):
            choice_field_name = f'choice_{round_index + 1}_{j}'
            choice_value = getattr(self.player, choice_field_name)  # 'Safe' or 'Risky'


            # Create a dictionary with relevant information from the choice
            choice_record = {
                'participant_id': self.player.participant.id_in_session,
                'task_number': round_index + 1,
                'choice_number': j,
                'choice_made': choice_value,
                'x1': float(choice[2]),  # High outcome
                'p1': float(choice[3].strip('%')),  # Probability of high outcome
                'x2': float(choice[4]),  # Low outcome
                'p2': float(choice[5].strip('%')),  # Probability of low outcome
                'y': float(choice[6]),  # Safe outcome
                'externality_risky': externality_risky[j - 1],
                'externality_safe': externality_safe[j - 1],
                'field_name': choice_field_name
            }
            # Append to choices_made and all_choices_
            self.participant.vars['choices_made'].append(choice_record)
            self.participant.vars['all_choices_'].append(choice_record)

        # Debugging: Print collected choices at each stage
        print(f"Choices made for Round {round_index + 1}: {self.participant.vars['choices_made']}")

        # Get the endowment

        """Compute the final payoff while ensuring it falls between 25 and 35."""

        # Get the endowment
        endowment = c(self.participant.vars.get('endowment', 0))  # Endowment from previous session
        show_up_fee = 5  # Fixed show-up fee
        min_total = 5  # ✅ Minimum allowed total earnings (including all)
        max_total = 25  # ✅ Maximum allowed total earnings (including all)

        # Progress to next round or compute final payoff
        if self.player.task_index < Constants.num_tasks - 1:
            self.player.task_index += 1
            return  # Exit function early if tasks remain

        # Randomly select num_payoff choices from all collected choices
        all_choices_made = self.participant.vars['all_choices_']
        num_payoff = Constants.num_payoff

        # Ensure there are enough choices for selection
        if len(all_choices_made) >= num_payoff:
            selected_choices = random.sample(all_choices_made, num_payoff)
        else:
            # Duplicate choices if fewer than num_payoff exist
            selected_choices = all_choices_made * 2 if len(all_choices_made) == 1 else all_choices_made

        valid_selection_found = False
        attempt_count = 0  # Track reshuffle attempts

        while not valid_selection_found:
            selected_choices = random.sample(all_choices_made, num_payoff)

            # Store selected choices
            self.player.selected_choices = json.dumps(selected_choices)

            total_decision_payoff = 0  # ✅ Store total decision payoff
            total_externality = 0
            results = []

            # Compute payoff by simulating draws
            for selected in selected_choices:
                draw_result = random.uniform(0, 100)  # Simulate random draw
                if selected['choice_made'] == 'Risky':
                    decision_payoff = selected['x1'] if draw_result <= selected['p1'] else selected['x2']
                    externality = selected['externality_risky']
                else:
                    decision_payoff = selected['y']
                    externality = selected['externality_safe']

                total_decision_payoff += decision_payoff  # ✅ Accumulate payoff
                total_externality += externality

                results.append({
                    'task': selected['task_number'],
                    'choice_num': selected['choice_number'],
                    'choice_made': selected['choice_made'],
                    'field_name': selected['field_name'],
                    'draw_result': draw_result,
                    'payoff': decision_payoff,  # ✅ Store individual decision payoff
                    'externality': externality
                })

            # Compute final earnings
            final_payoff = endowment + total_decision_payoff + show_up_fee

            # ✅ Ensure final payoff is between 25 and 35
            if min_total <= final_payoff <= max_total:
                valid_selection_found = True
                print(f"✅ Valid selection found after {attempt_count} attempts! Final Payoff: €{final_payoff:.2f}")
            else:
                attempt_count += 1
                print(f"❌ Constraints not met (Payoff: €{final_payoff:.2f}), reshuffling...\n")

        # Store final values
        self.participant.vars['selected_for_payoff'] = results
        self.participant.vars['final_payoff'] = total_decision_payoff  # ✅ Renamed from `decision_total_payoff`
        self.participant.vars['total_externality'] = total_externality

        # ✅ Save values in Player model
        self.player.payoff = total_decision_payoff  # ✅ Make player.payoff equal to decision payoff
        self.player.total_externality = total_externality
        self.player.final_earnings = final_payoff  # ✅ Includes show-up fee + endowment

class Results(Page):
    def vars_for_template(self):
        selected_choices = self.participant.vars.get('selected_for_payoff', [])
        all_choices = self.participant.vars.get('all_choices_', [])

        # ✅ Get stored final payoff instead of recomputing it
        final_payoff = self.participant.vars['final_payoff']
        total_externality = self.participant.vars['total_externality']
        endowment =  self.participant.vars['endowment']  # Endowment from previous session

        # ✅ Ensure draw_result is formatted as a whole number
        for result in selected_choices:
            result['draw_result'] = f"{float(result['draw_result']):.0f}" if isinstance(result['draw_result'], str) else f"{result['draw_result']:.0f}"

        # ✅ Extract task and choice numbers correctly
        for choice in selected_choices + all_choices:
            if 'field_name' in choice and choice['field_name']:
                parts = choice['field_name'].split('_')
                if len(parts) == 3:
                    choice['task_number'] = parts[1]
                    choice['choice_number'] = parts[2]
            else:
                choice['task_number'] = choice.get('task_number', 'N/A')
                choice['choice_number'] = choice.get('choice_number', 'N/A')

            # Add the field_name explicitly for display
            choice['field_name_display'] = choice['field_name']

        return {
            'selected_choices': selected_choices,
            'all_choices': all_choices,
            'decision_payoff': final_payoff,  # ✅ Using `final_payoff` correctly
            'total_externality': total_externality,
            'externality_risky': self.participant.vars.get('Ext Risky', 0),
            'externality_safe': self.participant.vars.get('Ext Safe', 0),
            'externality': self.participant.vars.get('ext_display', 0),
            "min_time_seconds": Constants.MIN_TIME_PER_PAGE["Results"],
            'endowment': endowment,
        }

    def before_next_page(self):
        endowment = self.participant.vars['endowment']  # Endowment from previous session

        self.participant.payoff = self.player.payoff + endowment
        self.player.payoff = self.player.payoff + endowment


class PayoffSummary(Page):
    def vars_for_template(self):
        # Retrieve stored values
        experiment_payoff = self.participant.vars['final_payoff']  # ✅ This is the correct decision-based payoff
        endowment =  self.participant.vars['endowment']  # Endowment from previous session
        participation_fee_session_2 = 5  # Fixed participation fee for session 2
        total_externality = self.participant.vars.get('total_externality', 0)  # Total externality generated

        # ✅ Compute total final earnings while ensuring it remains within [25, 35]
        total_payoff = experiment_payoff + endowment + participation_fee_session_2

        # ✅ Store total payoff in participant vars
        self.participant.vars['total_payoff'] = total_payoff

        # ✅ Set player.payoff to only the decision payoff (not including endowment)
        self.player.payoff = experiment_payoff  # ✅ Ensuring consistency
        self.player.decision_payoff = self.player.payoff
        return {
            'experiment_payoff': experiment_payoff,  # ✅ This is the payoff from decisions
            'endowment': endowment,  # ✅ Endowment from session 1
            'participation_fee_session_2': participation_fee_session_2,
            'total_externality': total_externality,
            'total_payoff': total_payoff,  # ✅ Corrected total payoff
        }


class PayoffSurvey(Page):
    form_model = 'player'

    form_fields = [
        'satisfaction', 'env_contribution',
        'externalities_influence',
         'comments',
        'factors_influencing_choices'
    ]
    def vars_for_template(self):
        return {
            'formfields': self.form_fields,  # Use form_fields directly
        }

class ThankYou(Page):
    def is_displayed(self):
        return True  # Toujours afficher cette page à la fin


m = int(Constants.num_tasks)  # Number of rounds

page_sequence = []
page_sequence = [
    Introduction,
    Questionnaire,
    EnterAlias,
    EnterPhoneNumber,
    DisplayEndowment,
   # WaitForExperimenter  # Participants wait until they enter the correct code
]

# Insert instructions at the beginning if enabled
if Constants.instructions:
  page_sequence.insert(6, Instructions)
if Constants.comprehension:
  page_sequence.append(Comprehension)
  #Insert practice rounds if enabled
if Constants.practice:
   for i in range(Constants.num_practice):
    page_sequence.append(Practice)
page_sequence.append(PracticeResults)  # Show results after practice

page_sequence += [Decision] * m  # Repeat the Decision page for each task
# Add Results page at the end if enabled
if Constants.results:
  page_sequence.append(Results)
page_sequence += [PayoffSummary]
page_sequence += [PayoffSurvey]
page_sequence += [ThankYou]

