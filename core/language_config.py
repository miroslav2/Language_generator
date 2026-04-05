from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from core.rule_settings import LanguageGenerationRules, default_rules_readable


@dataclass
class LanguageBlueprint:
    """Снимок настроек языка для мастера и генерации."""

    name: str = "Новый язык"
    seed: int | None = None

    inventory_mode: str = "auto"  # "auto" | "manual"
    complexity: float = 0.45
    num_consonants: int = 18
    num_vowels: int = 5
    allowed_consonant_groups: list[str] = field(default_factory=list)
    allowed_vowel_groups: list[str] = field(default_factory=list)
    manual_consonant_symbols: list[str] = field(default_factory=list)
    manual_vowel_symbols: list[str] = field(default_factory=list)

    use_consonant_slot_dedup: bool = True

    num_diphthongs: int = 4
    min_syllables: int = 2
    max_syllables: int = 4
    """0 = только закрытые слоги поощряются мало; 1 = открытые слоги заметно чаще."""
    syllable_openness: float = 0.55
    stress_pattern: str = "penultimate"  # initial | penultimate | final | mixed

    rules: LanguageGenerationRules = field(default_factory=default_rules_readable)

    @staticmethod
    def default() -> LanguageBlueprint:
        return LanguageBlueprint()

    def make_rng(self) -> random.Random:
        if self.seed is None:
            return random.Random()
        return random.Random(self.seed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "seed": self.seed,
            "inventory_mode": self.inventory_mode,
            "complexity": self.complexity,
            "num_consonants": self.num_consonants,
            "num_vowels": self.num_vowels,
            "allowed_consonant_groups": list(self.allowed_consonant_groups),
            "allowed_vowel_groups": list(self.allowed_vowel_groups),
            "manual_consonant_symbols": list(self.manual_consonant_symbols),
            "manual_vowel_symbols": list(self.manual_vowel_symbols),
            "use_consonant_slot_dedup": self.use_consonant_slot_dedup,
            "num_diphthongs": self.num_diphthongs,
            "min_syllables": self.min_syllables,
            "max_syllables": self.max_syllables,
            "syllable_openness": self.syllable_openness,
            "stress_pattern": self.stress_pattern,
            "rules": self.rules.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LanguageBlueprint:
        rules_raw = data.get("rules") or {}
        return cls(
            name=str(data.get("name", "Язык")),
            seed=data.get("seed"),
            inventory_mode=str(data.get("inventory_mode", "auto")),
            complexity=float(data.get("complexity", 0.45)),
            num_consonants=int(data.get("num_consonants", 18)),
            num_vowels=int(data.get("num_vowels", 5)),
            allowed_consonant_groups=list(data.get("allowed_consonant_groups", [])),
            allowed_vowel_groups=list(data.get("allowed_vowel_groups", [])),
            manual_consonant_symbols=list(data.get("manual_consonant_symbols", [])),
            manual_vowel_symbols=list(data.get("manual_vowel_symbols", [])),
            use_consonant_slot_dedup=bool(data.get("use_consonant_slot_dedup", True)),
            num_diphthongs=int(data.get("num_diphthongs", 4)),
            min_syllables=int(data.get("min_syllables", 2)),
            max_syllables=int(data.get("max_syllables", 4)),
            syllable_openness=float(data.get("syllable_openness", 0.55)),
            stress_pattern=str(data.get("stress_pattern", "penultimate")),
            rules=LanguageGenerationRules.from_dict(rules_raw) if rules_raw else default_rules_readable(),
        )
