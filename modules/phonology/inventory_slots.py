"""
Семейства согласных: в одном «естественном» языке обычно один r-подобный, один l-подобный и т.д.
При автоподборе инвентаря из каждого семейства берётся не больше одного звука.
"""

from __future__ import annotations

# Индексы семейств — произвольны; важно только разбиение на непересекающиеся наборы для подбора.
CONSONANT_SLOT_FAMILIES: list[frozenset[str]] = [
    frozenset({"r", "ɾ", "ɹ", "ʀ", "ɻ", "ɽ"}),
    frozenset({"l", "ɭ", "ʎ", "ʟ"}),
    frozenset({"w", "ʋ"}),
    frozenset({"ɬ", "ɮ"}),
    frozenset({"ʘ", "ǀ", "ǃ", "ǂ", "ǁ"}),
]


def slot_index_for_symbol(symbol: str) -> int | None:
    for i, fam in enumerate(CONSONANT_SLOT_FAMILIES):
        if symbol in fam:
            return i
    return None


def slots_satisfied_by_symbols(symbols: set[str]) -> set[int]:
    sat: set[int] = set()
    for sym in symbols:
        idx = slot_index_for_symbol(sym)
        if idx is not None:
            sat.add(idx)
    return sat
