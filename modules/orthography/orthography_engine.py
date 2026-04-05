from __future__ import annotations

import os
import random
import json

from modules.phonology.word_phonology import PhoneticWord
from modules.phonology.inventory_generator import Diphthongs
from modules.phonology.ipa_manager import PhonemeObject
from core.rule_settings import LanguageGenerationRules


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
    def __init__(
        self,
        json_path: str = "resources/grapheme_db.json",
        rules: LanguageGenerationRules | None = None,
        rng: random.Random | None = None,
    ):
        self.data: dict = self._load_json(json_path)
        self.vowels: dict = self.data.get("vowels") or {}
        self.consonants: dict = self.data.get("consonants") or {}
        self.chars: dict = self.vowels | self.consonants
        self.rules = rules if rules is not None else LanguageGenerationRules()
        self._rng = rng if rng is not None else random.Random()

    def _load_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database not found: {path}")
        with open(path, "r", encoding="utf-8") as grapheme:
            return json.load(grapheme)

    def set_rules(self, rules: LanguageGenerationRules) -> None:
        self.rules = rules

    def _script_for_word(self) -> str:
        scripts = ("latin", "cyrillic", "runes")
        if not self.rules.orth_fixed_script:
            return self._rng.choice(scripts)
        if self.rules.orth_script == "mixed":
            return self._rng.choice(scripts)
        return self.rules.orth_script if self.rules.orth_script in scripts else "latin"

    def _grapheme_options(self, ipa_key: str, script: str) -> list[str]:
        block = self.chars.get(ipa_key, {})
        return list(block.get(script, []) or [])

    def _pick_grapheme(self, ipa_key: str, script: str) -> str:
        opts = self._grapheme_options(ipa_key, script)
        if not opts:
            return ipa_key
        if self.rules.orth_prefer_primary_grapheme:
            return opts[0]
        return self._rng.choice(opts)

    def _is_vowel_segment(self, seg) -> bool:
        if isinstance(seg, Diphthongs):
            return True
        if isinstance(seg, PhonemeObject):
            return seg.symbol in self.vowels
        return False

    def _first_nucleus_vowel(self, seg) -> PhonemeObject | None:
        if isinstance(seg, Diphthongs):
            return seg.vowel_1
        if isinstance(seg, PhonemeObject):
            return seg
        return None

    def _last_syllable_phoneme(self, syllable) -> object | None:
        if syllable.coda:
            return syllable.coda[-1]
        if syllable.nucleus:
            return syllable.nucleus[-1]
        return None

    def _first_syllable_phoneme(self, syllable) -> object | None:
        if syllable.onset:
            return syllable.onset[0]
        if syllable.nucleus:
            return syllable.nucleus[0]
        return None

    def _glide_spelling(self, script: str, second_vowel: PhonemeObject | None) -> str:
        rounded = second_vowel.rounded if second_vowel else False
        if script == "cyrillic":
            return "в" if rounded else "й"
        if script == "runes":
            return "ᚹ" if rounded else "ᛃ"
        if rounded:
            return self._pick_grapheme("w", "latin")
        return self._pick_grapheme("j", "latin")

    def _spell_phoneme_sequence(
        self,
        segments: list,
        script: str,
        pieces: list[str],
        last_ipa: str | None,
    ) -> tuple[str | None, list[str]]:
        for phoneme in segments:
            if isinstance(phoneme, Diphthongs):
                s1, s2 = phoneme.vowel_1.symbol, phoneme.vowel_2.symbol
                for ipa_key in (s1, s2):
                    ch = self._pick_grapheme(ipa_key, script)
                    if (
                        self.rules.orth_double_for_identical_adjacent
                        and pieces
                        and ch == pieces[-1]
                        and last_ipa == ipa_key
                    ):
                        ch = ch + ch
                    pieces.append(ch)
                    last_ipa = ipa_key
            else:
                ipa_key = phoneme.base
                ch = self._pick_grapheme(ipa_key, script)
                if (
                    self.rules.orth_double_for_identical_adjacent
                    and pieces
                    and ch == pieces[-1]
                    and last_ipa == ipa_key
                ):
                    ch = ch + ch
                pieces.append(ch)
                last_ipa = ipa_key
        return last_ipa, pieces

    def _build_orthography(self, word: PhoneticWord, script: str) -> str:
        syllables = word.get_final_word_syllables()
        if not syllables:
            return ""

        syllable_chunks: list[str] = []
        for si, syllable in enumerate(syllables):
            pieces: list[str] = []
            last_ipa: str | None = None

            if si > 0 and self.rules.orth_insert_glide_between_vowels:
                prev = syllables[si - 1]
                lp = self._last_syllable_phoneme(prev)
                fp = self._first_syllable_phoneme(syllable)
                if self._is_vowel_segment(lp) and self._is_vowel_segment(fp):
                    sv = self._first_nucleus_vowel(fp)
                    pieces.append(self._glide_spelling(script, sv))

            last_ipa, pieces = self._spell_phoneme_sequence(
                syllable.onset, script, pieces, last_ipa
            )
            last_ipa, pieces = self._spell_phoneme_sequence(
                syllable.nucleus, script, pieces, last_ipa
            )
            last_ipa, pieces = self._spell_phoneme_sequence(
                syllable.coda, script, pieces, last_ipa
            )

            syllable_chunks.append("".join(pieces))

        sep = "-" if self.rules.orth_syllable_hyphens else ""
        return sep.join(syllable_chunks)

    def words_generator(self, words_list: list[PhoneticWord]) -> list[Word]:
        words: list[Word] = []
        for word in words_list:
            script = self._script_for_word()
            orthography = self._build_orthography(word, script)
            words.append(Word(word, orthography))
        return words
