from otree.api import *
from .models import C
import csv

def get_endowment(phone_number):
    """Fetch the endowment from the CSV file based on the phone number."""
    try:
        with open(C.CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Update the keys to match the actual column names in your CSV
                if row['save_endowment.1.player.phone_last_4_digits'] == phone_number:
                    return float(row['save_endowment.1.player.endowment'])
    except FileNotFoundError:
        print("CSV file not found!")
        return None
    except KeyError as e:
        print(f"KeyError: {e}. Check your CSV column names.")
        return None
    return None



class EnterPhoneNumber(Page):
    form_model = 'player'
    form_fields = ['phone_last_4_digits']

    def before_next_page(self):
        # Fetch endowment from the CSV file
        endowment = get_endowment(self.player.phone_last_4_digits)
        if endowment is not None:
            self.player.endowment = endowment
        else:
            self.player.endowment = 0  # Default if the phone number is not found


class DisplayEndowment(Page):
    def vars_for_template(self):
        return {
            'endowment': self.player.endowment,
        }


page_sequence = [
    EnterPhoneNumber,
    DisplayEndowment,
]
