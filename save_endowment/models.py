import os
import pandas as pd
import random
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
from otree.api import *
import random
import string



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



class C(BaseConstants):
    NAME_IN_URL = 'your_app'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    alias_code = models.StringField(blank=True)
    phone_last_4_digits = models.StringField(blank=True)
    total_payoff = models.FloatField()  # ✅ Allows decimal values
    endowment = models.FloatField()
def save_participant_data(self):
        """✅ Save participant data from the first session to PostgreSQL."""
        print(f"✅ Saving participant {self.participant.id_in_session} to DB...", flush=True)

        df = pd.DataFrame({
            "participant_id": [self.participant.id_in_session],
            "alias_code": [self.alias_code],
            "phone_last_4_digits": [self.phone_last_4_digits],
            "endowment": [self.total_payoff],
            "timestamp": [datetime.now()]
        })

        try:
            # ✅ Save data to PostgreSQL
            df.to_sql("experiment_sessions", con=engine, schema="public", if_exists="append", index=False)
            print("✅ Data saved successfully in PostgreSQL!", flush=True)

        except Exception as e:
            print(f"❌ Error saving data: {e}", flush=True)




def generate_random_alias():
    """✅ Generate a random alias consisting of 6 random letters/numbers"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
