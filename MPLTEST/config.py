# <imports>
def length(value):
    return len(value)

import os

import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from otree.api import Currency as c
from otree.constants import BaseConstants
# </imports>
import json

from otree.api import Currency
import os
import psycopg2
import os
import psycopg2
from sqlalchemy import create_engine


import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# ***********************ee********************************************************************************************* #
# *** CLASS CONSTANTS *** #
# ******************************************************************************************************************** #

# ✅ Ensure DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set! Make sure you have added a PostgreSQL database on Heroku.")

# ✅ Create connection pool
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_endowment_from_db(alias=None, phone_number=None):
    """Fetch endowment and phone number from PostgreSQL based on alias or phone number."""
    if alias:
        query = "SELECT endowment, phone_last_4_digits FROM public.save_endowment_player WHERE alias_code = %s;"
        param = (alias,)
    elif phone_number:
        query = "SELECT endowment, phone_last_4_digits FROM public.save_endowment_player WHERE phone_last_4_digits = %s;"
        param = (phone_number,)
    else:
        print("❌ No valid alias or phone number provided!")
        return None

    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cursor = conn.cursor()
        cursor.execute(query, param)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            endowment, phone_last_4_digits = result
            print(f"✅ Found endowment: {endowment}, Phone: {phone_last_4_digits}")
            return {"endowment": float(endowment), "phone_number": phone_last_4_digits}
        else:
            print("❌ No matching record found.")
    except Exception as e:
        print(f"❌ Error fetching endowment: {e}")

    return None

class Constants(BaseConstants):
    PREDEFINED_CODE = "EXP2025"

    # Define minimum time per page (in seconds)
    MIN_TIME_PER_PAGE = {

        "Instructions": 1,
        "Introduction": 1,
        "PracticeResults": 1,
        "Decision": 1,
        "Comprehension":1,
        "Questionnaire":1,
        "Results": 1

    }

    # Practice Lotteries
    practice_lotteries = [
        {'x1': 100, 'x2': 0, 'p1': 0.3, 'p2': 0.7, 'y': 50, 'externality_risky_practice': 1, 'externality_safe_practice': 1},
        {'x1': 80, 'x2': -40, 'p1': 0.8, 'p2': 0.2, 'y': -20, 'externality_risky_practice': 1, 'externality_safe_practice': 0},
        {'x1': -60, 'x2': 0, 'p1': 0.5, 'p2': 0.5, 'y': -30, 'externality_risky_practice': 1, 'externality_safe_practice': 1},
        {'x1': 15, 'x2': 0, 'p1': 0.5, 'p2': 0.5, 'y': 5, 'externality_risky_practice':1,'externality_safe_practice':1},
        {'x1': 40, 'x2': -10, 'p1': 0.3, 'p2': 0.7, 'y': -20 ,'externality_risky_practice':1,'externality_safe_practice':0},
        {'x1': -30, 'x2': 0, 'p1': 0.8, 'p2': 0.2, 'y': -10, 'externality_risky_practice':0,'externality_safe_practice':1},
    ]
    num_practice = 3  # Practice lotteries (lotteries 4-6)
    num_comprehension = 3  # Comprehension lotteries (lotteries 1-3)


    # --------------------------Constants.x1_gains_neutralConstants.x1_gains_neutral-------------------------------------------------------------------------------------- #
    # --- Task-specific Settings --- #
    # ---------------------------------------------------------------------------------------------------------------- #


    # lottery payoffs
    # "high" and "low" outcomes (in currency units set in settings.py) of "lottery A" and "lottery B"

    x1 = [
        0, 5, 0, 0, 0, 0,  0,      -5,       0,      0,    0,     0,
        -10, 10, -10,10,0,     0,   5,    0,            0,  0,   5,   0,    0,   5,    0,
        0, -5, 0, 0, 10, -10, 10, 0, 0, 0, 0, 10, 10
    ]

    x2 = [
        20, 20, 20, 20, 20, 20,-20,     -20,     -20,    -20,  -20,   -20,  20, -20,20,-20,
        10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
        -20, -20, -20, -20, -20, 20, -20, -20, -20, -20, -20, -20, -20

    ]

    p2 = [
        0.5, 0.5, 0.25, 0.625, 0.75, 0.875, 0.5,     0.5,    0.25,  0.625, 0.75, 0.875,   0.5, 0.5, 0.25, 0.75,
        0.5, 0.5, 0.5, 0.25, 0.75, 0.5, 0.5, 0.25, 0.5, 0.5, 0.75,
        0.5, 0.5, 0.25, 0.75, 0.5, 0.25, 0.75, 0.5, 0.75, 0.5, 0.75, 0.5, 0.5
    ]

    y = [
        10, 10, 10, 10, 10, 10, -10,     -10,     -10,    -10,  -10,   -10, 0,   0,  0,0,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        -10, -10, -10, -10, 0, 0, 0, -10, -10, -10, -10, 0, 0
    ]

    p1 = [1 - p for p in p2]  # Calculate p1 from p2 dynamically

    externality_risky = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,0,0,1,0
        ]

    externality_safe = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,1      ]
    externality_value = 5
    # number of binary choices between "lottery A" and "lottery B"
    num_tasks = length(x1)# Total number of rounds
    num_choices = 4
    decrement_amount = 1

    num_payoff= 5
    num_practice= 3

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Overall Settings and Appearance --- #
    # ---------------------------------------------------------------------------------------------------------------- #


    # order choices between lottery pairs randomly

    condition_to_shuffle = True  # Shuffle the decision screens
    condition_to_shuffle_safe_choices = False # Shuffle the safe choices
    # enforce consistency, i.e. only allow for a single switching point
    # if <enforce_consistency = True>, all options "A" above a selected option "A" are automatically selected
    # similarly, all options "B" below a selected option "B" are automatically checked, implying consistent choices
    # note that <enforce_consistency> is only implemented if <one_choice_per_page = False> and <random_order = False>
    enforce_consistency = False #Use only if condition_to_shuffle_safe_choices = False



    # depict probabilities as percentage numbers
    # if <percentage = True>, the probability of outcome "high" will be displayed as percentage number
    # if <percentage = False>, the probabilities will be displayed as fractions, i.e. "1/X", "2/X", etc.
    percentage = True



    # show progress bar
    # if <progress_bar = True> and <one_choice_per_page = True>, a progress bar is rendered
    # if <progress_bar = False>, no information with respect to the advance within the task is displayed
    # the progress bar graphically depicts the advance within the task in terms of how many decision have been made
    # further, information in terms of "page x out of <num_choices>" (with x denoting the current choice) is provided
    progress_bar = True

    # show instructions page
    # if <instructions = True>, a separate template "Instructions.html" is rendered prior to the task
    # if <instructions = False>, the task starts immediately (e.g. in case of printed instructions)
    instructions = True
    comprehension =True

    practice = True

    # show results page summarizing the task's outcome including payoff information
    # if <results = True>, a separate page containing all relevant information is displayed after finishing the task
    # if <results = False>, the template "Decision.html" will not be rendered
    results = True

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- oTree Settings (Don't Modify) --- #
    # ---------------------------------------------------------------------------------------------------------------- #

    name_in_url = 'mpl'
    players_per_group = None


    num_rounds = 1
