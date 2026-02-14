import random

class WeightedSyllableGenerator:
    """
    Генератор слогов на основе вероятностей.
    """
    def __init__(self, rules: list):
        # rules example: [{'pattern': 'CV', 'weight': 50}, {'pattern': 'CVC', 'weight': 30}]
        self.rules = rules

    def get_template(self) -> str:
        patterns = [r['pattern'] for r in self.rules]
        weights = [r['weight'] for r in self.rules]
        return random.choices(patterns, weights=weights, k=1)[0]