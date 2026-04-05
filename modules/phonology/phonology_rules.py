from __future__ import annotations

from typing import TYPE_CHECKING

from modules.phonology.ipa_manager import PhonemeObject, IPAManager
from core.rule_settings import LanguageGenerationRules

if TYPE_CHECKING:
    from modules.phonology.word_phonology import PhoneticWord

OBSTRUENT_MANNERS = frozenset({
    "plosive", "stop", "fricative", "sibilant", "affricate",
    "ejective", "click", "implosive", "lateral fricative",
})

NASAL_SYMBOL_BY_PLACE = {
    "bilabial": "m",
    "labiodental": "ɱ",
    "dental": "n",
    "alveolar": "n",
    "postalveolar": "n",
    "retroflex": "ɳ",
    "palatal": "ɲ",
    "palatoalveolar": "ɲ",
    "velar": "ŋ",
    "uvular": "ɴ",
    "pharyngeal": "n",
    "glottal": "n",
}


def _is_phoneme(p) -> bool:
    return isinstance(p, PhonemeObject)


def _is_obstruent(p: PhonemeObject) -> bool:
    return p.manner in OBSTRUENT_MANNERS


def _is_nasal(p: PhonemeObject) -> bool:
    return p.manner == "nasal"


class PhonologyRuleApplier:
    """
    Применяет включённые в LanguageGenerationRules постобработки к финальной фонетике слова.
    Работает только с объектами PhonemeObject в атаке/коде; ядра с дифтонгами не меняет.
    """

    def __init__(
        self,
        rules: LanguageGenerationRules,
        ipa: IPAManager | None = None,
        inventory_consonants: list[PhonemeObject] | None = None,
    ):
        self.rules = rules
        self._ipa = ipa
        self._by_symbol: dict[str, PhonemeObject] = {
            p.symbol: p for p in (inventory_consonants or [])
        }

    def apply(self, word: "PhoneticWord") -> None:
        syls = word.get_final_word_syllables()
        if not syls:
            return

        if self.rules.phon_trim_long_onsets or self.rules.phon_trim_long_codas:
            self._trim_clusters(syls)

        if self.rules.phon_simplify_geminate_across_boundary:
            self._simplify_geminates(syls)

        if self.rules.phon_nasal_place_assimilation:
            self._nasal_place(syls)

        if self.rules.phon_voicing_assimilation:
            self._voicing(syls)

        word.set_final_word_phonetic(syls)

    def _rebuild_all(self, syls):
        for s in syls:
            s.rebuild_segments()

    def _trim_clusters(self, syls):
        for s in syls:
            if self.rules.phon_trim_long_onsets and len(s.onset) > 2:
                s.onset = [s.onset[0], s.onset[-1]]
            if self.rules.phon_trim_long_codas and len(s.coda) > 2:
                s.coda = s.coda[-2:]
        self._rebuild_all(syls)

    def _simplify_geminates(self, syls):
        for i in range(len(syls) - 1):
            a, b = syls[i], syls[i + 1]
            if not a.coda or not b.onset:
                continue
            last = a.coda[-1]
            first = b.onset[0]
            if _is_phoneme(last) and _is_phoneme(first) and last.symbol == first.symbol:
                b.onset = b.onset[1:]
        self._rebuild_all(syls)

    def _nasal_place(self, syls):
        for i in range(len(syls) - 1):
            a, b = syls[i], syls[i + 1]
            if not a.coda or not b.onset:
                continue
            last = a.coda[-1]
            if not _is_phoneme(last) or not _is_nasal(last):
                continue
            nxt = next((p for p in b.onset if _is_phoneme(p)), None)
            if not nxt or not nxt.place:
                continue
            target = NASAL_SYMBOL_BY_PLACE.get(nxt.place)
            if not target or target not in self._by_symbol:
                continue
            a.coda[-1] = self._by_symbol[target]
        self._rebuild_all(syls)

    def _voicing(self, syls):
        if not self._ipa:
            return
        for i in range(len(syls) - 1):
            a, b = syls[i], syls[i + 1]
            if not a.coda or not b.onset:
                continue
            c = a.coda[-1]
            o = b.onset[0]
            if not _is_phoneme(c) or not _is_phoneme(o):
                continue
            if not _is_obstruent(c) or not _is_obstruent(o):
                continue
            if o.voiced is None or c.voiced is None:
                continue
            if c.voiced == o.voiced:
                continue
            repl = self._partner_obstruent(c, o.voiced)
            if repl is not None:
                a.coda[-1] = repl
        self._rebuild_all(syls)

    def _partner_obstruent(self, src: PhonemeObject, target_voiced: bool) -> PhonemeObject | None:
        for d in self._ipa.all_consonants:
            if d.get("place") != src.place:
                continue
            if d.get("manner") != src.manner:
                continue
            if d.get("voiced") is not target_voiced:
                continue
            sym = d.get("symbol")
            if sym and sym in self._by_symbol:
                return self._by_symbol[sym]
        return None


# Обратная совместимость со старым именем класса
Phonology_rules = PhonologyRuleApplier
