from modules.phonology.word_phonology import PhoneticWord
from modules.phonology.inventory_generator import Diphthongs
import os, json, random

class Word:
    def __init__(self, phonetic_word: PhoneticWord, orthography: str):
        self.phonetic_word = phonetic_word
        self.orthography = orthography

    def __repr__(self):
        return self.orthography
    
    def get_phonetic(self) -> str:
        return self.phonetic_word.get_final_word_phonetic_syllables()
    
    def get_orthography(self) -> str:
        return self.orthography
    
    def set_orthography(self, orthography):
        self.orthography = orthography

class WordEngine:
    def __init__(self, json_path="resources/grapheme_db.json"):
        self.data: dict = self._load_json(json_path)
        self.vowels: dict = self.data.get('vowels')
        self.consonants: dict = self.data.get('consonants')
        self.chars: dict = self.vowels | self.consonants

    def _load_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database not found: {path}")
        with open(path, 'r', encoding='utf-8') as grapheme:
            return json.load(grapheme)
    
    def words_generator(self, words_list: list[PhoneticWord]) -> list[Word]:
        words: list[Word] = []
        for word in words_list:
            word_orthography: str = ''
            for syllable in word.get_raw_word_syllables():
                for phoneme in syllable.get_phoneme_list():
                    if type(phoneme) == Diphthongs:
                        symbol_1 = phoneme.vowel_1.symbol
                        symbol_2 = phoneme.vowel_2.symbol
                        char_1 = random.choice(self.chars.get(symbol_1, {}).get(random.choice(['latin', 'cyrillic', 'runes']), []))
                        char_2 = random.choice(self.chars.get(symbol_2, {}).get(random.choice(['latin', 'cyrillic', 'runes']), []))
                        word_orthography = word_orthography + char_1 + char_2
                    else:
                        char = random.choice(self.chars.get(phoneme.base, {}).get(random.choice(['latin', 'cyrillic', 'runes']), []))
                        word_orthography = word_orthography + char

            words.append(Word(word, word_orthography))
        return words