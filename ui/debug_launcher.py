import sys
# Импортируем менеджер, который мы только что создали
# Убедись, что файл modules/phonology/ipa_manager.py существует!
from modules.phonology.ipa_manager import IPAManager, PhonemeObject
from modules.phonology.engine import PhonologyGenerator

class DebugRunner:
    def run(self):
        print("=== ULTIMATE LANGUAGE GENERATOR [DEBUG MODE] ===")
        
        while True:
            print("\n-----------------------------")
            print(" ГЛАВНОЕ МЕНЮ ОТЛАДКИ")
            print("-----------------------------")
            print("1. Тест Фонетики (IPA Database & Modifiers)")
            print("2. Создать новый проект (Пока пусто)")
            print("3. Генератор Инвентаря (Создать набор звуков)")
            print("0. Выход")
            
            cmd = input("\n>>> Ваш выбор: ")
            
            if cmd == "0":
                print("Завершение работы.")
                sys.exit()
            elif cmd == "1":
                self.test_ipa_features()
            elif cmd == "2":
                print("Этот функционал еще в разработке.")
            elif cmd == "3":
                self.test_inventory_generation()
            else:
                print("Неверная команда.")

    def test_ipa_features(self):
        print("\n[INFO] Загрузка IPA базы...")
        
        try:
            # Инициализируем наш менеджер
            ipa = IPAManager()
        except FileNotFoundError:
            print("[ERROR] Файл resources/ipa_db.json не найден!")
            return
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении JSON: {e}")
            return

        print(f"--> Успешно загружено: {len(ipa.all_consonants)} согл., {len(ipa.all_vowels)} гласн.")

        # --- ТЕСТ 1: ПОИСК ---
        print("\n--- 1. Демонстрация Поиска ---")
        
        print("Ищем: Взрывные (plosive) и Глухие (voiced=False)")
        plosives = ipa.get_consonants(manner="plosive", voiced=False)
        # Выводим только символы через запятую
        print(f"Результат: {[p['symbol'] for p in plosives]}")

        print("\nИщем: Огубленные гласные (rounded=True)")
        rounded = ipa.get_vowels(rounded=True)
        print(f"Результат: {[v['symbol'] for v in rounded]}")

        # --- ТЕСТ 2: МОДИФИКАТОРЫ ---
        print("\n--- 2. Демонстрация Диакритик ---")
        
        # Берем звук 'n' для опытов
        n_data = ipa.get_consonants(place="alveolar", manner="nasal")[0]
        my_sound = PhonemeObject(n_data['symbol'], n_data)
        
        print(f"Базовый звук: /{my_sound}/")
        
        # 1. Оглушаем (добавляем кружочек снизу)
        voiceless_sym = ipa.get_modifier("voiceless")
        if voiceless_sym:
            my_sound.add_modifier(voiceless_sym)
            print(f" + Оглушение: /{my_sound}/ (n̥)")
        
        # 2. Делаем долгим
        long_sym = ipa.get_modifier("long")
        if long_sym:
            my_sound.add_modifier(long_sym)
            print(f" + Долгота:   /{my_sound}/ (n̥ː)")

        # --- ТЕСТ 3: ТОНЫ ---
        print("\n--- 3. Демонстрация Тонов ---")
        syllable = "ma"
        print(f"Слог: {syllable}")
        
        # Пробуем разные тоны
        example_tones = ["high", "falling", "low rising"]
        
        for tone_name in example_tones:
            tone_sym = ipa.get_modifier(tone_name)
            if tone_sym:
                print(f"Тон '{tone_name}': {syllable}{tone_sym}")
            else:
                print(f"Тон '{tone_name}' не найден в базе.")

        input("\n[Нажмите Enter для возврата в меню...]")
    
    def test_inventory_generation(self):
        print("\n--- ГЕНЕРАТОР ИНВЕНТАРЯ ---")
        try:
            ipa = IPAManager()
            generator = PhonologyGenerator(ipa)
        except Exception as e:
            print(f"Ошибка инициализации: {e}")
            return

        while True:
            print("\nВыберите уровень сложности языка:")
            print("1. Примитивный (Полинезийский стиль) - Complexity 0.1")
            print("2. Стандартный (Европейский стиль)   - Complexity 0.4")
            print("3. Экзотический (Ксено/Африканский)  - Complexity 0.9")
            print("0. Назад")
            
            choice = input(">>> ")
            
            complexity = 0.3
            if choice == "0": break
            elif choice == "1": complexity = 0.1
            elif choice == "2": complexity = 0.4
            elif choice == "3": complexity = 0.9
            else: continue
            
            print(f"\nГенерируем язык со сложностью {complexity}...")
            profile = generator.generate_inventory(complexity)
            
            print("="*40)
            print(profile)
            print("="*40)