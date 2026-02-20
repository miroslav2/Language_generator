from modules.phonology.syllables import SyllableObject

import copy

class PhoneticWord:
    def __init__(self, stress_index: int, raw_word_phonetic: list[SyllableObject]):
        self.raw_word_phonetic = raw_word_phonetic
        self.final_word_phonetic = copy.deepcopy(raw_word_phonetic)
        self.stress_index = stress_index
        
        if 0 <= stress_index < len(self.final_word_phonetic):
            self.final_word_phonetic[stress_index].is_stressed = True
    
    def __repr__(self):
        return ''.join(str(syl) for syl in self.final_word_phonetic)
    
    def get_raw_word_phonetic(self) -> str:
        return ''.join(str(syl) for syl in self.raw_word_phonetic)
    
    def get_final_word_phonetic_syllables(self) -> str:
        return '.'.join(str(syl) for syl in self.final_word_phonetic)
    
    def get_raw_word_phonetic_syllables(self) -> str:
        return '.'.join(str(syl) for syl in self.raw_word_phonetic)
                

class WordPhonologyGenerator:
    def __init__(self):
        pass