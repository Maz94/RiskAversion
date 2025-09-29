from otree.api import Bot
from . import Instructions, Decision, Results
import random

class PlayerBot(Bot):
    def play_round(self):
        profile = self.participant.vars.get('profile', {})
        knowledge = profile.get('knowledge_level', 'intermediate')
        targets = [18.09, 85.03, 8.11, 77.09, 92.17, 14.64, 59.99, 93.17, 9.11, 17.76]

        responses = []
        for target in targets:
            if knowledge == 'basic':
                # More imprecise: wide random around the target
                guess = round(random.uniform(max(0, target - 50), min(100, target + 50)), 2)
            elif knowledge == 'advanced':
                # Very precise: small random noise
                guess = round(random.uniform(max(0, target - 2), min(100, target + 2)), 2)
            else:
                # Intermediate: medium noise
                guess = round(random.uniform(max(0, target - 10), min(100, target + 10)), 2)
            responses.append(guess)

        # Step 1: Instructions
        yield Instructions

        # Step 2: Decision with the generated answers
        data = {f"nle_{i+1}": responses[i] for i in range(10)}
        yield Decision, data

        # Step 3: Results
        yield Results
