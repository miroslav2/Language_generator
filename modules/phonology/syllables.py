from modules.phonology.categorizer import CategoriesObject
from modules.phonology.engine import PhonologyProfile, Diphthongs
from modules.phonology.ipa_manager import PhonemeObject

import random

class SyllablesObject():
    def __init__(self, type: str, onset: list[PhonemeObject], nucleus: list[PhonemeObject | Diphthongs], coda: list[PhonemeObject]):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda
        self.syllables = onset + nucleus + coda
        self.type_syllables = type
        self.len_syllables = len(type)

    def __repr__(self):
        return ''.join([str(obj) for obj in self.syllables])
    
class SyllablesManager:
    def __init__(self, categories: CategoriesObject, type_syl: str):
        self.categories = categories
        self.type_syllable = type_syl

    def syllable_generator(self):
        nucleus_type = ''
        has_nucleus = False
        
        if 'V' in self.type_syllable:
            nucleus_type = 'V'
            has_nucleus = True
        elif 'D' in self.type_syllable:
            nucleus_type = 'D'
            has_nucleus = True

        if has_nucleus:
            onset_str, nucleus_str, coda_str = self.type_syllable.partition(nucleus_type)
        else:
            onset_str = self.type_syllable
            nucleus_str = ''
            coda_str = ''

        onset = []
        nucleus = []
        coda = []

        last_sound = None
        for ch in onset_str:
            possible_sounds = self.categories.categories.get(ch)
            if not possible_sounds: return None
            
            choice = random.choice(possible_sounds)
            attempts = 0
            while str(choice) == str(last_sound) and len(possible_sounds) > 1 and attempts < 10:
                choice = random.choice(possible_sounds)
                attempts += 1
            
            onset.append(choice)
            last_sound = choice
        
        last_sound = None
        for ch in coda_str:
            possible_sounds = self.categories.categories.get(ch)
            if not possible_sounds: return None
            
            choice = random.choice(possible_sounds)
            attempts = 0
            while str(choice) == str(last_sound) and len(possible_sounds) > 1 and attempts < 10:
                choice = random.choice(possible_sounds)
                attempts += 1

            coda.append(choice)
            last_sound = choice
        if has_nucleus:
            possible_nuclei = self.categories.categories.get(nucleus_str)
            if not possible_nuclei: return None
            nucleus.append(random.choice(possible_nuclei))

        return SyllablesObject(self.type_syllable, onset, nucleus, coda)
