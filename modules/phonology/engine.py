import random
from modules.phonology.ipa_manager import IPAManager, PhonemeObject

class PhonologyProfile:
    """
    Хранит выбранный набор звуков для конкретного языка.
    """
    def __init__(self):
        self.consonants = []
        self.vowels = []
    
    def __repr__(self):
        c_str = ", ".join([str(p) for p in self.consonants])
        v_str = ", ".join([str(p) for p in self.vowels])
        return f"Phonology:\n  Consonants ({len(self.consonants)}): {c_str}\n  Vowels ({len(self.vowels)}): {v_str}"

class PhonologyGenerator:
    """
    Отвечает за генерацию инвентаря звуков на основе настроек.
    """
    def __init__(self, ipa_manager: IPAManager):
        self.ipa = ipa_manager
        self.allowed_consonants_groups = ['Approximants (Аппроксиманты)', 'Clicks (Щелкающие / Кликсы)', 'Co-articulated (Коартикулированные)', 'Ejectives (Абруптивные / Эйективы)', 'Fricatives (Фрикативные/Щелевые)', 'Implosives (Имплозивные)', 'Lateral Approximants (Боковые)', 'Lateral Fricatives (Боковые фрикативные)', 'Nasals (Носовые)', 'Plosives (Взрывные)', 'Trills & Taps (Дрожащие и Одноударные)']
        self.allowed_vowels_groups = ['Close Vowels (Верхний подъем)', 'Close-mid Vowels (Средне-верхний подъем)', 'Mid Vowels (Средний подъем)', 'Near-close Vowels (Ненапряженные верхние)', 'Near-open Vowels (Почти нижний подъем)', 'Open Vowels (Нижний подъем)', 'Open-mid Vowels (Средне-нижний подъем)']

    def generate_inventory(self, consonants: list, vowels: list) -> PhonologyProfile:
        profile = PhonologyProfile()
        profile.consonants = consonants
        profile.vowels = vowels
        return profile

    def auto_generate_inventory(self, num_consonants: int, num_vowels: int, complexity: float = 0.3) -> PhonologyProfile:
        """
        complexity: 0.0 (только самые простые звуки) -> 1.0 (полный хаос и кликсы)
        """
        profile = PhonologyProfile()
        
        # 1. Определяем размер инвентаря (чем сложнее, тем больше звуков, обычно)
        # В среднем языке ~20-25 согласных и ~5-6 гласных
        
        # 2. Выбираем СОГЛАСНЫЕ
        # Фильтруем базу: берем только те звуки, чья редкость <= complexity + небольшой запас
        # Например, если complexity 0.1, мы не возьмем кликсы (rarity 0.9)
        threshold = complexity + 0.05
        if threshold > 1.0: threshold = 1.0
        
        available_cons = [c for c in self.ipa.all_consonants if c.get('rarity', 1.0) <= threshold and c.get('group') in self.allowed_consonants_groups]
        
        # Если доступных меньше, чем хотим - берем сколько есть
        count_c = min(len(available_cons), num_consonants)
        selected_cons_data = random.sample(available_cons, count_c)
        
        # Превращаем словари в объекты PhonemeObject
        profile.consonants = [PhonemeObject(d['symbol']) for d in selected_cons_data]

        # 3. Выбираем ГЛАСНЫЕ
        # Для гласных всегда берем базу (a, i, u), если они доступны
        available_vowels = [v for v in self.ipa.all_vowels if v.get('rarity', 1.0) <= threshold and v.get('group') in self.allowed_vowels_groups]
        
        # Гарантируем (почти) наличие a, i, u
        must_have = ['a', 'i', 'u']
        final_vowels_data = []
        
        for symbol in must_have:
            # Ищем звук в доступных
            found = next((v for v in available_vowels if v['symbol'] == symbol), None)
            
            if found:
                # 80% шанс добавить "базовый" гласный
                # Если выпало > 0.8, мы его пропускаем (рискуем остаться без 'u')
                if random.random() < 0.8:
                    final_vowels_data.append(found)
                    if found in available_vowels:
                        available_vowels.remove(found)
        
        # Добираем остальные случайно
        remaining_count = max(0, num_vowels - len(final_vowels_data))
        count_v = min(len(available_vowels), remaining_count)
        
        final_vowels_data += random.sample(available_vowels, count_v)
        
        profile.vowels = [PhonemeObject(d['symbol']) for d in final_vowels_data]
        
        return profile
    
    def set_allowed_groups(self, allowed: tuple[list, list]):
        self.allowed_consonants_groups, self.allowed_vowels_groups = allowed
    
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