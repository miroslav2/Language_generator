from __future__ import annotations

import random
from types import SimpleNamespace

from modules.phonology.ipa_manager import IPAManager
from modules.phonology.inventory_generator import PhonologyGenerator
from modules.phonology.categorizer import Categorizer
from modules.phonology.word_phonology import WordPhonologyGenerator
from modules.orthography.orthography_engine import WordEngine
from core.language_config import LanguageBlueprint


def build_language_stack(blueprint: LanguageBlueprint, ipa: IPAManager) -> SimpleNamespace:
    """
    Собирает профиль, категории и генераторы слов с общим RNG по seed
    (слова одного языка воспроизводимы и согласованы).
    """
    rng = blueprint.make_rng()
    gen = PhonologyGenerator(ipa)
    gen.set_complexity(blueprint.complexity)

    cg = blueprint.allowed_consonant_groups
    vg = blueprint.allowed_vowel_groups
    if cg and vg:
        gen.set_allowed_groups((cg, vg))

    if blueprint.inventory_mode == "manual":
        profile = gen.profile_from_manual_symbols(
            blueprint.manual_consonant_symbols,
            blueprint.manual_vowel_symbols,
        )
    else:
        profile = gen.auto_generate_inventory(
            blueprint.num_consonants,
            blueprint.num_vowels,
            rng=rng,
            use_consonant_slot_dedup=blueprint.use_consonant_slot_dedup,
        )

    categorizer = Categorizer(profile)
    categorizer.diphthongs_generator(int(blueprint.num_diphthongs), rng=rng)
    categories = categorizer.categorization()

    word_generator = WordPhonologyGenerator(
        blueprint.min_syllables,
        blueprint.max_syllables,
        categories,
        rules=blueprint.rules,
        ipa=ipa,
        profile=profile,
        rng=rng,
        stress_pattern=blueprint.stress_pattern,
        syllable_openness=blueprint.syllable_openness,
    )

    orth_seed = (blueprint.seed if blueprint.seed is not None else rng.randint(1, 2**30)) ^ 0x9E3779B9
    word_engine = WordEngine(rules=blueprint.rules, rng=random.Random(orth_seed))

    return SimpleNamespace(
        phonology_generator=gen,
        profile=profile,
        categorizer=categorizer,
        categories=categories,
        word_generator=word_generator,
        word_engine=word_engine,
        rng=rng,
    )
