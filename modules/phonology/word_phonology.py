from modules.phonology.syllables import SyllableObject, SyllablesManager
from modules.phonology.categorizer import CategoryObject

import copy, random
import os, json

class PhoneticWord:
    def __init__(self, stress_index: int, raw_word_phonetic: list[SyllableObject]):
        self.raw_word_phonetic = raw_word_phonetic
        self.final_word_phonetic = copy.deepcopy(raw_word_phonetic)
        self.num_syllables: int = -1
        
        if 0 <= stress_index < len(self.final_word_phonetic):
            self.stress_index = stress_index
            self.final_word_phonetic[stress_index].set_stress_status(True)
        else:
            self.stress_index = -1
    
    def __repr__(self):
        return ''.join(str(syl) for syl in self.final_word_phonetic)
    
    def get_raw_word_phonetic(self) -> str:
        return ''.join(str(syl) for syl in self.raw_word_phonetic)
    
    def get_final_word_phonetic_syllables(self) -> str:
        return '.'.join(str(syl) for syl in self.final_word_phonetic)
    
    def get_raw_word_phonetic_syllables(self) -> str:
        return '.'.join(str(syl) for syl in self.raw_word_phonetic)
    
    def get_raw_word_syllables(self) -> list[SyllableObject]:
        return self.raw_word_phonetic
    
    def get_final_word_syllables(self) -> list[SyllableObject]:
        return self.final_word_phonetic
    
    def get_num_syllables(self) -> int:
        return self.num_syllables
    
    def get_stress_index(self) -> int:
        return self.stress_index
    
    def set_final_word_phonetic(self, final_word_phonetic: list[SyllableObject]):
        self.final_word_phonetic = final_word_phonetic
    
    def set_num_syllables(self, num_syllables: int):
        self.num_syllables = num_syllables
                

class WordPhonologyGenerator:
    def __init__(self, min_syllables: int, max_syllables: int, categories: CategoryObject):
        self.categories = categories
        self.templates = self._load_templates()
        self.min_syllables = min_syllables
        self.max_syllables = max_syllables
    
    def _load_templates(self, path: str = "resources/presets/syllable_templates.json") -> list[dict]:
        """Загружает шаблоны слогов из JSON"""
        
        if not os.path.exists(path):
            return [{ "pattern": "V",     "weight": 20, "description": "Vowel only (a-tom)" },
                    { "pattern": "CV",    "weight": 100,"description": "Universal syllable (ba, ka, mi)" },
                    { "pattern": "NV",    "weight": 60, "description": "Nasal onset (ma, no)" },
                    { "pattern": "LV",    "weight": 50, "description": "Liquid onset (la, ro)" },
                    { "pattern": "FV",    "weight": 50, "description": "Fricative onset (fa, zo)" },
                    { "pattern": "PV",    "weight": 70, "description": "Plosive onset (pa, da)" },
                    { "pattern": "VC",    "weight": 30, "description": "Vowel start closed (am, it)" },
                    { "pattern": "CVC",   "weight": 80, "description": "Standard closed (cat, dog)" },
                    { "pattern": "CVN",   "weight": 60, "description": "Nasal coda (pan, bin)" },
                    { "pattern": "CVL",   "weight": 50, "description": "Liquid coda (car, ball)" },
                    { "pattern": "CVS",   "weight": 40, "description": "Sibilant coda (bus, ash)" },
                    { "pattern": "CVF",   "weight": 30, "description": "Fricative coda (leaf, math)" },
                    { "pattern": "CVP",   "weight": 40, "description": "Stop coda (bat, top)" },
                    { "pattern": "D",     "weight": 10, "description": "Pure diphthong (eye, ow)" },
                    { "pattern": "CD",    "weight": 40, "description": "Open diphthong (boy, cow, hi)" },
                    { "pattern": "DC",    "weight": 15, "description": "Diphthong closed (out, oil)" },
                    { "pattern": "CDC",   "weight": 30, "description": "Closed diphthong (loud, coin)" },
                    { "pattern": "CDN",   "weight": 25, "description": "Diphthong + Nasal (down, time)" },
                    { "pattern": "CDL",   "weight": 20, "description": "Diphthong + Liquid (file, our)" }]
                    #           ["V", "CV", "NV", "LV", "FV", "PV", 
                    #            "VC", "CVC", "CVN", "CVL", "CVS", "CVF", "CVP",
                    #            "D", "CD", "DC", "CDC", "CDN", "CDL", "CDP", "CDF",] 
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        flat_templates = []
        for group in data:
            for tmpl in group['templates']:
                flat_templates.append(tmpl)
        return flat_templates
    
    def _get_random_template(self) -> str:
        """Выбирает один шаблон (строку) с учетом весов"""
        if not self.templates: return "CV"
        
        patterns = [t['pattern'] for t in self.templates]
        weights = [t['weight'] for t in self.templates]
        return random.choices(patterns, weights=weights, k=1)[0]

    def generate_word(self) -> PhoneticWord:
        """Создает готовое слово"""
        min_syl = self.min_syllables
        max_syl = self.max_syllables
        length = random.randint(min_syl, max_syl)
        syllables = []

        for _ in range(length):
            # Пытаемся создать слог (несколько попыток)
            syl_obj = None
            for _ in range(10):
                tmpl = self._get_random_template()
                manager = SyllablesManager(self.categories, tmpl)
                syl_obj = manager.syllable_generator()
                if syl_obj:
                    break
            
            # Если не вышло - аварийный вариант
            if not syl_obj:
                manager = SyllablesManager(self.categorizer, "CV")
                syl_obj = manager.syllable_generator()
            
            syllables.append(syl_obj)

        # Решаем, где ударение
        stress_idx = self._determine_stress(length)
        
        phonetic_word = PhoneticWord(stress_idx, syllables)
        
        self._eply_rules(phonetic_word)
        
        # Собираем слово
        return phonetic_word
    
    def _determine_stress(self, num_syllables: int) -> int:
        """
        Решает, на какой слог падает ударение.
        В разработке
        """
        if num_syllables == 1:
            return 0
            
        roll = random.random()
        if roll < 0.6:
            return 0
        elif roll < 0.9:
            return num_syllables - 2 if num_syllables >= 2 else 0
        else:
            return num_syllables - 1
    
    def _eply_rules(self, phonetic_word: PhoneticWord):
        """В разработке"""
        final_phonetic_word = phonetic_word.get_final_word_syllables()
        phonetic_word.set_final_word_phonetic(final_phonetic_word)