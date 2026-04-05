import random
from modules.phonology.ipa_manager import IPAManager, PhonemeObject
from modules.phonology.inventory_slots import slot_index_for_symbol

class PhonologyProfile:
    """
    Хранит выбранный набор звуков для конкретного языка.
    """
    def __init__(self):
        self.consonants: list[PhonemeObject] = []
        self.vowels: list[PhonemeObject] = []
    
    def __repr__(self):
        c_str = ", ".join([str(p) for p in self.consonants])
        v_str = ", ".join([str(p) for p in self.vowels])
        return f"Phonology:\n  Consonants ({len(self.consonants)}): {c_str}\n  Vowels ({len(self.vowels)}): {v_str}"

class Diphthongs:
    def __init__(self, vowel_1: PhonemeObject, vowel_2: PhonemeObject):
        self.vowel_1 = vowel_1
        self.vowel_2 = vowel_2

    def __repr__(self):
        return f'{self.vowel_1.symbol}{self.vowel_2.symbol}'
    
    def __eq__(self, other_diphthong):
        if isinstance(other_diphthong, Diphthongs):
            return other_diphthong.vowel_1 == self.vowel_1 and other_diphthong.vowel_2 == self.vowel_2
        return False
    
    def __hash__(self):
        return hash(str(self.vowel_1) + str(self.vowel_2))
        
    @property
    def base(self):
        return str(self)

class PhonologyGenerator:
    """
    Отвечает за генерацию инвентаря звуков на основе настроек.
    """
    def __init__(self, ipa_manager: IPAManager):
        self.ipa = ipa_manager
        self.complexity = 0.3
        self.allowed_consonants_groups = ['Approximants (Аппроксиманты)', 'Clicks (Щелкающие / Кликсы)', 'Co-articulated (Коартикулированные)', 'Ejectives (Абруптивные / Эйективы)', 'Fricatives (Фрикативные/Щелевые)', 'Implosives (Имплозивные)', 'Lateral Approximants (Боковые)', 'Lateral Fricatives (Боковые фрикативные)', 'Nasals (Носовые)', 'Plosives (Взрывные)', 'Trills & Taps (Дрожащие и Одноударные)']
        self.allowed_vowels_groups = ['Close Vowels (Верхний подъем)', 'Close-mid Vowels (Средне-верхний подъем)', 'Mid Vowels (Средний подъем)', 'Near-close Vowels (Ненапряженные верхние)', 'Near-open Vowels (Почти нижний подъем)', 'Open Vowels (Нижний подъем)', 'Open-mid Vowels (Средне-нижний подъем)']

    def generate_inventory(self, consonants: list, vowels: list) -> PhonologyProfile:
        profile = PhonologyProfile()
        profile.consonants = consonants
        profile.vowels = vowels
        return profile

    def consonant_selection_weight(self, c: dict) -> float:
        """
        Чем ниже rarity в базе, тем чаще звук; экзотика с rarity близко к complexity получает штраф.
        """
        rarity = float(c.get("rarity", 0.5))
        margin = self.complexity - rarity
        if margin < 0:
            return 0.0
        base = (1.0 - rarity) ** 1.35
        edge = max(0.0, min(1.0, margin * 2.0))
        return max(0.001, base * (0.35 + 0.65 * edge))

    def vowel_selection_weight(self, v: dict) -> float:
        rarity = float(v.get("rarity", 0.5))
        margin = self.complexity - rarity
        if margin < 0:
            return 0.0
        return max(0.001, (1.0 - rarity) ** 1.2 * (0.4 + 0.6 * max(0.0, min(1.0, margin * 2.0))))

    def _weighted_pick_index(self, weights: list[float], rng: random.Random) -> int:
        total = sum(weights)
        if total <= 0:
            return 0
        r = rng.random() * total
        acc = 0.0
        for i, w in enumerate(weights):
            acc += w
            if r <= acc:
                return i
        return len(weights) - 1

    def _pick_consonants_weighted(
        self,
        pool: list[dict],
        count: int,
        rng: random.Random,
        use_slots: bool,
    ) -> list[dict]:
        working = list(pool)
        selected: list[dict] = []
        satisfied_slots: set[int] = set()

        def allowed(d: dict) -> bool:
            sym = d.get("symbol", "")
            if not use_slots:
                return True
            si = slot_index_for_symbol(sym)
            if si is None:
                return True
            return si not in satisfied_slots

        while len(selected) < count and working:
            cand = [d for d in working if allowed(d)]
            if not cand:
                cand = working
            wts = [self.consonant_selection_weight(d) for d in cand]
            if sum(wts) <= 0:
                wts = [1.0] * len(cand)
            idx = self._weighted_pick_index(wts, rng)
            pick = cand[idx]
            selected.append(pick)
            working.remove(pick)
            si = slot_index_for_symbol(pick.get("symbol", ""))
            if si is not None:
                satisfied_slots.add(si)
        return selected

    def _pick_vowels_weighted(
        self,
        pool: list[dict],
        count: int,
        rng: random.Random,
        must_have: list[str] | None = None,
    ) -> list[dict]:
        must_have = must_have or ["a", "i", "u"]
        by_sym = {v["symbol"]: v for v in pool}
        selected: list[dict] = []
        used_syms: set[str] = set()

        for sym in must_have:
            if len(selected) >= count:
                break
            if sym in by_sym and sym not in used_syms:
                selected.append(by_sym[sym])
                used_syms.add(sym)

        working = [v for v in pool if v["symbol"] not in used_syms]
        need = max(0, count - len(selected))
        while need > 0 and working:
            wts = [self.vowel_selection_weight(v) for v in working]
            if sum(wts) <= 0:
                wts = [1.0] * len(working)
            idx = self._weighted_pick_index(wts, rng)
            pick = working.pop(idx)
            selected.append(pick)
            need -= 1
        return selected

    def auto_generate_inventory(
        self,
        num_consonants: int,
        num_vowels: int,
        rng: random.Random | None = None,
        use_consonant_slot_dedup: bool = True,
    ) -> PhonologyProfile:
        """
        complexity: 0.0 (только самые простые звуки) -> 1.0 (полный хаос и кликсы)
        """
        rng = rng if rng is not None else random.Random()
        profile = PhonologyProfile()

        available_cons = [
            c
            for c in self.ipa.all_consonants
            if c.get("rarity", 1.0) <= self.complexity
            and c.get("group") in self.allowed_consonants_groups
        ]

        count_c = min(len(available_cons), num_consonants)
        selected_cons_data = self._pick_consonants_weighted(
            available_cons, count_c, rng, use_slots=use_consonant_slot_dedup
        )

        profile.consonants = [PhonemeObject(d) for d in selected_cons_data]

        available_vowels = [
            v
            for v in self.ipa.all_vowels
            if v.get("rarity", 1.0) <= self.complexity
            and v.get("group") in self.allowed_vowels_groups
        ]

        final_vowels_data = self._pick_vowels_weighted(
            available_vowels, num_vowels, rng, must_have=["a", "i", "u"]
        )

        profile.vowels = [PhonemeObject(d) for d in final_vowels_data]

        return profile

    def profile_from_manual_symbols(
        self, consonant_symbols: list[str], vowel_symbols: list[str]
    ) -> PhonologyProfile:
        profile = PhonologyProfile()
        c_map = {c["symbol"]: c for c in self.ipa.all_consonants}
        v_map = {v["symbol"]: v for v in self.ipa.all_vowels}
        for sym in consonant_symbols:
            if sym in c_map:
                profile.consonants.append(PhonemeObject(c_map[sym]))
        for sym in vowel_symbols:
            if sym in v_map:
                profile.vowels.append(PhonemeObject(v_map[sym]))
        return profile
    
    def set_allowed_groups(self, allowed: tuple[list, list]):
        self.allowed_consonants_groups, self.allowed_vowels_groups = allowed

    def set_complexity(self, complexity: float):
        self.complexity = complexity
    
    def get_available_groups(self) -> tuple[list, list]:
        """Вспомогательный метод: возвращает список всех групп из базы (для UI)"""
        consonants_groups = set()
        vowels_groups = set()
        # Собираем группы из всех согласных
        for c in self.ipa.all_consonants:
            if 'group' in c:
                consonants_groups.add(c['group'])
        
        for v in self.ipa.all_vowels:
            if 'group' in v:
                vowels_groups.add(v['group'])
        
        return (sorted(list(consonants_groups)), sorted(list(vowels_groups)))
    
    def get_all_sounds(self) -> tuple[list, list]:
        consonants = [c['symbol'] for c in self.ipa.all_consonants]
        vowels = [v['symbol'] for v in self.ipa.all_vowels]
        return (consonants, vowels)

    def get_groupped_all_sounds(self) -> tuple[dict, dict]:
        grouped_consonants_sounds = {}
        grouped_vowels_sounds = {}
        for c in self.ipa.all_consonants:
            group_name = c.get('group', 'unknown')
            consonants = c['symbol']
            if group_name not in grouped_consonants_sounds:
                grouped_consonants_sounds[group_name] = []
            grouped_consonants_sounds[group_name].append(consonants)
        
        for v in self.ipa.all_vowels:
            group_name = v.get('group', 'unknown')
            vowels = v['symbol']
            if group_name not in grouped_vowels_sounds:
                grouped_vowels_sounds[group_name] = []
            grouped_vowels_sounds[group_name].append(vowels)
        return (grouped_consonants_sounds, grouped_vowels_sounds)

    def get_allowed_sounds(self) -> tuple[list, list]:
        consonants = [c['symbol'] for c in self.ipa.all_consonants if c.get('rarity', 1.0) <= self.complexity and c.get('group') in self.allowed_consonants_groups]
        vowels = [v['symbol'] for v in self.ipa.all_vowels if v.get('rarity', 1.0) <= self.complexity and v.get('group') in self.allowed_vowels_groups]
        return (consonants, vowels)