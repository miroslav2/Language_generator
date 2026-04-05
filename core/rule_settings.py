from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any


@dataclass
class LanguageGenerationRules:
    """
    Включаемые правила сглаживания фонетики и оформления написания.
    Все флаги по умолчанию выключены, кроме удобочитаемой орфографии
    (фиксированный алфавит и предпочтение основного графемного варианта).
    """

    # --- Фонетика (последовательное применение в порядке перечисления в PhonologyRuleApplier) ---
    phon_trim_long_onsets: bool = False
    """Если в начале слога больше двух согласных, оставить только первые два."""

    phon_trim_long_codas: bool = False
    """Если в конце слога больше двух согласных, оставить только последние два."""

    phon_voicing_assimilation: bool = False
    """Согласование по глухости/звонкости на стыке слогов (кода + начало следующего слога)."""

    phon_nasal_place_assimilation: bool = False
    """Носовой в конце слога принимает место артикуляции у первого согласного следующего слога."""

    phon_simplify_geminate_across_boundary: bool = False
    """Одинаковый согласный на стыке слогов: убрать дубль в начале следующего слога."""

    # --- Написание ---
    orth_fixed_script: bool = True
    """Не чередовать латиницу/кириллицу/руны внутри одного слова."""

    orth_script: str = "latin"
    """Один из ключей в grapheme_db: latin | cyrillic | runes (при mixed — случайный на слово)."""

    orth_prefer_primary_grapheme: bool = True
    """Брать первый вариант из списка графем (обычно самый простой)."""

    orth_syllable_hyphens: bool = False
    """Вставлять дефис между слогами в написании."""

    orth_double_for_identical_adjacent: bool = True
    """Удлинять запись при двух одинаковых сегментах подряд (двойная согласная)."""

    orth_insert_glide_between_vowels: bool = False
    """Между двумя гласными в разных слогах вставить glide j/w по округлённости второго гласного."""

    def clone(self) -> LanguageGenerationRules:
        return LanguageGenerationRules(**self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LanguageGenerationRules:
        known = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in data.items() if k in known}
        return cls(**kwargs)


def default_rules_readable() -> LanguageGenerationRules:
    """Пресет: удобное чтение/написание без агрессивной фонетики."""
    return LanguageGenerationRules(
        orth_fixed_script=True,
        orth_script="latin",
        orth_prefer_primary_grapheme=True,
        orth_syllable_hyphens=False,
        orth_double_for_identical_adjacent=True,
        orth_insert_glide_between_vowels=False,
    )


def default_rules_smoothed_phonology() -> LanguageGenerationRules:
    """Пресет: сглаженная произносительная форма слова."""
    r = default_rules_readable()
    r.phon_trim_long_onsets = True
    r.phon_trim_long_codas = True
    r.phon_voicing_assimilation = True
    r.phon_nasal_place_assimilation = True
    r.phon_simplify_geminate_across_boundary = True
    return r
