from typing import Dict, List, Optional

class Lexeme:
    """
    Умная словарная статья. Хранит формы слова и исключения.
    """
    def __init__(self, meaning: str, base_form: str, word_class: str = "regular"):
        self.meaning = meaning
        self.base_form = base_form
        self.word_class = word_class
        self.irregularities: Dict[str, str] = {} # {"past": "went"}

class Word:
    """
    Готовое слово в предложении.
    """
    def __init__(self, text: str, grammar_tags: Dict):
        self.text = text
        self.tags = grammar_tags