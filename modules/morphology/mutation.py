from core.data_structures import Lexeme

class StemManager:
    """
    Управляет супплетивизмом и изменением корней (go -> went).
    """
    def get_stem(self, lexeme: Lexeme, context: dict) -> str:
        # 1. Проверка жестких исключений
        target_form = context.get('tense')
        if target_form in lexeme.irregularities:
            return lexeme.irregularities[target_form]
        
        # 2. Здесь будет логика для классов (strong verbs)
        
        return lexeme.base_form