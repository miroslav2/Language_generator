from typing import List

class CompoundEngine:
    """
    Склейка корней (пароход, steamboat).
    """
    def __init__(self, linking_rules: list = None):
        self.linking_rules = linking_rules or []

    def assemble(self, roots: List[str]) -> str:
        # Простая склейка для начала
        return "".join(roots)