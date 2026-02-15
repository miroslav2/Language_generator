import json
import os
from typing import List, Dict, Optional

class PhonemeObject:
    """
    Объект, представляющий конкретный звук с его модификаторами.
    """
    def __init__(self, base_symbol: str):
        self.base = base_symbol

    def add_modifier(self, modifier_symbol: list) -> str:
        """Добавляет диакритику, тон или знак долготы"""
        return self.base + "".join(modifier_symbol)
    
    def add_modifier(self, modifier_symbol: str) -> str:
        """Добавляет диакритику, тон или знак долготы"""
        return self.base + modifier_symbol

    def __repr__(self):
        return self.base


class IPAManager:
    def __init__(self, json_path="resources/ipa_db.json"):
        self.data = self._load_json(json_path)
        
        # Кэши (упрощенные списки для быстрого поиска)
        self.all_consonants = []
        self.all_vowels = []
        self.modifiers_map = {} # Быстрый поиск модификатора по названию
        
        self._parse_db()

    def _load_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database not found: {path}")
        with open(path, 'r', encoding='utf-8') as ipa:
            return json.load(ipa)

    def _parse_db(self):
        """Превращает вложенный JSON в удобные плоские списки"""
        
        # 1. Собираем все согласные
        for group in self.data.get("consonants", []):
            for sound in group.get("sounds", []):
                sound['group'] = group.get('group_name')
                self.all_consonants.append(sound)

        # 2. Собираем все гласные
        for group in self.data.get("vowels", []):
            for sound in group.get("sounds", []):
                sound['group'] = group.get('group_name')
                self.all_vowels.append(sound)

        # 3. Собираем модификаторы в словарь для поиска
        for group in self.data.get("modifiers", []):
            # Тут ключи могут быть signs или sounds, зависит от json
            signs = group.get("signs") or group.get("sounds", [])
            for sign in signs:
                # 1. Добавляем поиск по имени (есть у всех)
                if 'name' in sign:
                    self.modifiers_map[sign['name']] = sign
                
                # 2. Добавляем поиск по функции (есть у диакритик и ударений)
                if 'function' in sign:
                    self.modifiers_map[sign['function']] = sign
                    
                # 3. Можно добавить поиск по типу (есть у тонов)
                if 'type' in sign:
                    self.modifiers_map[sign['type']] = sign

    # --- МЕТОДЫ ПОИСКА (ФИЛЬТРЫ) ---

    def get_consonants(self, place=None, manner=None, voiced=None) -> List[dict]:
        """Универсальный фильтр согласных"""
        result = self.all_consonants
        if place:
            result = [s for s in result if s.get('place') == place]
        if manner:
            result = [s for s in result if s.get('manner') == manner]
        if voiced is not None:
            result = [s for s in result if s.get('voiced') == voiced]
        return result

    def get_vowels(self, height=None, rounded=None) -> List[dict]:
        """Универсальный фильтр гласных"""
        result = self.all_vowels
        if height:
            result = [s for s in result if s.get('height') == height]
        if rounded is not None:
            result = [s for s in result if s.get('rounded') == rounded]
        return result

    def get_modifier(self, name_or_func: str) -> Optional[str]:
        """Возвращает символ модификатора по имени (например 'long' -> 'ː')"""
        mod = self.modifiers_map.get(name_or_func)
        # Если нашли точно по имени - возвращаем символ
        if mod:
            return mod['symbol']
        # Если не нашли, пробуем искать в списке вручную (если map не сработал)
        for val in self.modifiers_map.values():
            if val['name'] == name_or_func or val.get('function') == name_or_func:
                return val['symbol']
        return None
