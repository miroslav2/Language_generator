from modules.phonology.engine import PhonologyProfile,Diphthongs
from modules.phonology.ipa_manager import IPAManager
import random

class CategoriesObject:
    def __init__(self):
        self.categories = {
            'C': [], # (Consonants): любой согласный
            'P': [], # (Plosive/Stop): Взрывные
            'F': [], # (Fricative): Фрикативные (Шумные)
            'N': [], # (Nasal): Носовые
            'L': [], # (Liquid/Glide): Плавные/Сонорные
            'S': [], # (Sibilant): Подвид фрикативных
            'V': [], # (Vowel): Обычные гласные (короткие)
            'D': []  # (Diphthong): Дифтонги (длинные)
        }

    def __repr__(self):
        categorized_sounds = []
        for key, values in self.categories.items():
            sounds_str = ", ".join([str(p) for p in values])
            categorized_sounds.append(f"{key}: {sounds_str}")
        return '\n'.join(categorized_sounds)

class Categorizer:
    def __init__(self, profile: PhonologyProfile):
        self.phonology_profile = profile
        self.diphthongs: list[Diphthongs] = []

    def diphthongs_generator(self, num_diphthongs: int) -> tuple[str, list]:
        diphthongs: set[Diphthongs] = set()
        if len(self.phonology_profile.vowels) >= 2:
            attempts = 0
            max_attempts = 100
            while len(diphthongs) < num_diphthongs and attempts < max_attempts:
                v1 = random.choice(self.phonology_profile.vowels)
                v2 = random.choice(self.phonology_profile.vowels)
                if v1.base != v2.base:
                    diphthongs.add(Diphthongs(v1, v2))
                attempts += 1
        self.diphthongs = list(diphthongs)
        return ('D', list(diphthongs))

    def individual_diphthongs_generator(self, diphthongs: list[str]) -> tuple[str, list]:
        refactoring_diphthongs = [d for d in diphthongs if len(d) == 2]
        self.diphthongs = [Diphthongs(d[0], d[1]) for d in refactoring_diphthongs]
        return ('D', self.diphthongs)

    def categorization(self) -> CategoriesObject:
        categories_object = CategoriesObject()
        for consonant_sound in self.phonology_profile.consonants:
            manner = consonant_sound.manner
            
            categories_object.categories['C'].append(consonant_sound)

            if manner in ['plosive', 'implosive', 'ejective', 'click', 'stop']:
                categories_object.categories['P'].append(consonant_sound)
            if manner in ['nasal']:
                categories_object.categories['N'].append(consonant_sound)
            if manner in ['fricative', 'lateral fricative', 'sibilant', 'affricate']:
                categories_object.categories['F'].append(consonant_sound)
            if manner in ['approximant', 'lateral', 'lateral approximant', 'trill', 'tap', 'flap']:
                categories_object.categories['L'].append(consonant_sound)
            if consonant_sound.base in ['s', 'z', 'ʃ', 'ʒ', 'ʂ', 'ʐ', 'ɕ', 'ʑ']:
                categories_object.categories['S'].append(consonant_sound)
        
        for vowels_sound in self.phonology_profile.vowels:
            categories_object.categories['V'].append(vowels_sound)
        
        categories_object.categories['D'] = self.diphthongs
        return categories_object



