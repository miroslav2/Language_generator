from core.rule_settings import LanguageGenerationRules


class LanguageState:
    """
    Хранилище данных текущего языка.
    """
    def __init__(self):
        self.name = "New Language"
        self.phonemes = []
        self.syllable_rules = []
        self.lexicon = {} 
        self.grammar_settings = {}
        self.generation_rules = LanguageGenerationRules()