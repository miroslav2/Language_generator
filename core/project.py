import json
from core.state import LanguageState

class LanguageProject:
    def __init__(self, name: str):
        self.state = LanguageState()
        self.state.name = name

    def save(self, path: str):
        print(f"Сохранение проекта {self.state.name}...")
        # Реализация сохранения в JSON
        pass