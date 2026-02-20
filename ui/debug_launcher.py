import sys
import random
# Импортируем менеджер, который мы только что создали
# Убедись, что файл modules/phonology/ipa_manager.py существует!
from modules.phonology.ipa_manager import IPAManager, PhonemeObject
from modules.phonology.inventory_generator import PhonologyGenerator
from modules.phonology.categorizer import Categorizer
from modules.phonology.syllables import SyllablesManager

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
            print("4. Генератор слогов")
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
            elif cmd == "4":
                self.test_syllable_generation()
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
        my_sound = PhonemeObject(n_data['symbol'])
        
        print(f"Базовый звук: /{my_sound}/")
        
        # 1. Оглушаем (добавляем кружочек снизу)
        voiceless_sym = ipa.get_modifier("voiceless")
        if voiceless_sym:
            my_sound.add_modifier(list(voiceless_sym))
            print(f" + Оглушение: /{my_sound}/ (n̥)")
        
        # 2. Делаем долгим
        long_sym = ipa.get_modifier("long")
        if long_sym:
            my_sound.add_modifier(list(long_sym))
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
            print("4. Настраиваемый")
            print("5. Свой набор")
            print("6. Настройка генератора")
            print("7. Список всех групп")
            print("8. Список всех звуков")
            print("9. Список всех звуков по группам")
            print("10. Список разрешённых звуков")
            print("0. Назад")
            
            choice = input(">>> ")
            
            complexity = 0.3
            if choice == "0": break
            elif choice == "1": generator.set_complexity(0.3)
            elif choice == "2": generator.set_complexity(0.6)
            elif choice == "3": generator.set_complexity(0.9)
            elif choice == "4":
                
                complexity = float(input("Введите желаемую сложность языка (от 0.00 до 1.00) >> "))
            elif choice == "5":
                consonants = input("введите согласные звуки через пробел >> ").split()
                vowels = input("введите гласные звуки через пробел >> ").split()
                profile = generator.generate_inventory(consonants, vowels)
            
                print("="*40)
                print(profile)
                print("="*40)

                continue
            elif choice == "6":
                allowed_consonants_groups = []
                allowed_vowels_groups = []
                consonants_groups, vowels_goups = generator.get_available_groups()
                complexity = float(input("Введите сложность языка (0.00 - 1.00) >> "))
                print("вкл\выкл групп согласных:")
                for c in consonants_groups:
                    if input(f"Включить группу {c} (Y\\n) >> ") == "Y":
                        allowed_consonants_groups.append(c)
                
                print("вкл\выкл групп гласных:")
                for v in vowels_goups:
                    if input(f"Включить группу {v} (Y\\n) >> ") == "Y":
                        allowed_vowels_groups.append(v)
                
                generator.set_complexity(complexity)
                generator.set_allowed_groups((allowed_consonants_groups, allowed_vowels_groups))
                continue
            elif choice == "7":
                c, v = generator.get_available_groups()
                print(f"\nСписок групп согласных >> {c}\n\nСписок групп гласных >> {v}")
                input("\n[Нажмите Enter для возврата в меню...]")
                continue
            elif choice == "8":
                c, v = generator.get_all_sounds()
                print(f"\nСписок всех согласных >> {c}\n\nСписок всех гласных >> {v}")
                input("\n[Нажмите Enter для возврата в меню...]")
                continue
            elif choice == "9":
                c_dict, v_dict = generator.get_groupped_all_sounds()

                c_dict, v_dict = generator.get_groupped_all_sounds()

                print(f"\n--- СПИСОК ВСЕХ СОГЛАСНЫХ ПО ГРУППАМ ---")
                # c_dict.items() вернет пары ("Plosives", ['p', 't'...])
                # sorted( ... ) отсортирует по алфавиту имен групп
                for group_name, sounds in sorted(c_dict.items()):
                    print(f"\n{group_name}:\n{', '.join(sounds)}")

                print(f"\n--- СПИСОК ВСЕХ ГЛАСНЫХ ПО ГРУППАМ ---")
                for group_name, sounds in sorted(v_dict.items()):
                    print(f"\n{group_name}:\n{', '.join(sounds)}")
                
                input("\n[Нажмите Enter для возврата в меню...]")
                continue
            elif choice == "10":
                c, v = generator.get_allowed_sounds()
                print(f"\nСписок допустимых согласных >> {c}\n\nСписок допустимых гласных >> {v}")
                input("\n[Нажмите Enter для возврата в меню...]")
                continue
            else: continue
            
            num_consonants = int(input("Введите желаемое количество согласных в языке >> "))
            num_vowels = int(input("Введите желаемое количество гласных в языке >> "))
            
            print(f"\nГенерируем язык со сложностью {complexity}...")
            profile = generator.auto_generate_inventory(num_consonants, num_vowels)
            
            print("="*40)
            print(profile)
            print("="*40)

            print(f"\nКатегоризатор")

            categorizer = Categorizer(profile)
            categorizer.diphthongs_generator(5)
            
            categories = categorizer.categorization()
            print("="*40)
            print(categories)
            print("="*40)

            
            input("\n[Нажмите Enter для возврата в меню...]")

    def test_syllable_generation(self):
        print("\n--- ТЕСТ ГЕНЕРАЦИИ СЛОГОВ ---")
        
        # 1. Готовим инструменты (как в настоящей программе)
        ipa = IPAManager()
        gen = PhonologyGenerator(ipa)

        complexity = float(input('\nВведите желаемую сложность языка >> '))
        gen.set_complexity(complexity)

        num_consonants = int(input("Введите желаемое количество согласных в языке >> "))
        num_vowels = int(input("Введите желаемое количество гласных в языке >> "))
        
        print(f"\nГенерируем язык со сложностью {complexity}...")
        profile = gen.auto_generate_inventory(num_consonants, num_vowels)
        
        print("="*40)
        print(profile)
        print("="*40)
        
        print("Инвентарь создан.")
        
        print(f"\nКатегоризатор")

        num_diphthongs = float(input('\nВведите желаемую количество дифтонгов >> '))

        categorizer = Categorizer(profile)
        categorizer.diphthongs_generator(num_diphthongs)
        
        cats = categorizer.categorization()
        print("="*40)
        print(cats)
        print("="*40)
           
        # 3. Генерируем слоги по разным шаблонам
        print("\nПробуем шаблоны:")

        templates = [
    # 1. Простые открытые
    "V", "CV", "NV", "LV", "FV", "PV",
    
    # 2. Простые закрытые
    "VC", "CVC", "CVN", "CVL", "CVS", "CVF", "CVP",
    
    # 3. С дифтонгами
    "D", "CD", "DC", "CDC", "CDN", "CDL", "CDP", "CDF",
    
    # 4. Сложные начала (Onsets)
    "PLV", "FLV", "SLV", "NLV", # Liquid после кого-то
    "PNV", "FNV", "SNV",        # Nasal после кого-то (pneu, snow)
    "PFV", "PSV",               # Fricative после Stop (pf, ps)
    
    # 5. Кластеры с S (Sibilant)
    "SPV", "SFV", "SNV", "SLV",
    "SPLV", "SFLV", # Тройные (stra, spla)
    
    # 6. Сложные концы (Codas)
    "CVSP",                 # st, sk, sp
    "CVLP", "CVLF", "CVLN", # lp, lf, ln
    "CVNP", "CVNF", "CVNS", # nt, nf, ns
    
    # 7. Монстры
    "PLVLC", "FLVNC", "SPVLP", "SFLVNS", "CCCVC", "CDC", "C", "CC"
]
        
        for tmpl in templates:
            manager = SyllablesManager(cats, tmpl)
            try:
                # Генерируем 3 примера для каждого шаблона
                syl_objects = [manager.syllable_generator() for _ in range(5)]
                for syl in syl_objects: syl.set_stress_status(random.choice([True, False]))
                results = [str(syll) for syll in syl_objects]
                print(f"Шаблон {tmpl}: {', '.join(results)}")
            except Exception as e:
                print(f"Шаблон {tmpl}: Ошибка ({e}) - возможно, нет нужных звуков")
        
        input("\n[Нажмите Enter для возврата в меню...]")