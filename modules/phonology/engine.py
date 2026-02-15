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

    def generate_inventory(self, consonants: list, vowels: list) -> PhonologyProfile:
        profile = PhonologyProfile()
        profile.consonants = consonants
        profile.vowels = vowels
        return profile

    def auto_generate_inventory(self, complexity: float = 0.3) -> PhonologyProfile:
        """
        complexity: 0.0 (только самые простые звуки) -> 1.0 (полный хаос и кликсы)
        """
        profile = PhonologyProfile()
        
        # 1. Определяем размер инвентаря (чем сложнее, тем больше звуков, обычно)
        # В среднем языке ~20-25 согласных и ~5-6 гласных
        num_consonants = int(15 + (complexity * 20)) # от 15 до 35
        num_vowels = int(3 + (complexity * 10))      # от 3 до 13
        
        # 2. Выбираем СОГЛАСНЫЕ
        # Фильтруем базу: берем только те звуки, чья редкость <= complexity + небольшой запас
        # Например, если complexity 0.1, мы не возьмем кликсы (rarity 0.9)
        threshold = complexity + 0.2
        if threshold > 1.0: threshold = 1.0
        
        available_cons = [c for c in self.ipa.all_consonants if c.get('rarity', 1.0) <= threshold]
        
        # Если доступных меньше, чем хотим - берем сколько есть
        count_c = min(len(available_cons), num_consonants)
        selected_cons_data = random.sample(available_cons, count_c)
        
        # Превращаем словари в объекты PhonemeObject
        profile.consonants = [PhonemeObject(d['symbol'], d) for d in selected_cons_data]

        # 3. Выбираем ГЛАСНЫЕ
        # Для гласных всегда берем базу (a, i, u), если они доступны
        available_vowels = [v for v in self.ipa.all_vowels if v.get('rarity', 1.0) <= threshold]
        
        # Гарантируем наличие a, i, u (треугольник гласных), если сложность низкая
        must_have = ['a', 'i', 'u']
        final_vowels_data = []
        
        for symbol in must_have:
            # Ищем звук в доступных
            found = next((v for v in available_vowels if v['symbol'] == symbol), None)
            if found:
                final_vowels_data.append(found)
                available_vowels.remove(found) # Чтобы не дублировать
        
        # Добираем остальные случайно
        remaining_count = max(0, num_vowels - len(final_vowels_data))
        count_v = min(len(available_vowels), remaining_count)
        
        final_vowels_data += random.sample(available_vowels, count_v)
        
        profile.vowels = [PhonemeObject(d['symbol'], d) for d in final_vowels_data]
        
        return profile