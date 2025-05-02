import random

from . import *

class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        yield Submission(
            Slider,
            dict(num_successful_sliders=random.randint(C.REQUIRED_SUCCESS-1, C.REQUIRED_SUCCESS +2)),
            check_html=False
        )
        yield Submission(Results, check_html=False)
