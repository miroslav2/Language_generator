"""
Пошаговый мастер настройки искусственного языка (tkinter).
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.language_config import LanguageBlueprint
from core.language_pipeline import build_language_stack
from modules.phonology.ipa_manager import IPAManager
from modules.phonology.inventory_generator import PhonologyGenerator

DEFAULT_OFF_CONSONANT_GROUPS = frozenset(
    {
        "Clicks (Щелкающие / Кликсы)",
        "Implosives (Имплозивные)",
        "Ejectives (Абруптивные / Эйективы)",
        "Co-articulated (Коартикулированные)",
    }
)


class LanguageWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конструктор языка")
        self.geometry("800x640")
        self.minsize(660, 520)

        self.bp = LanguageBlueprint.default()
        self.ipa: IPAManager | None = None
        self._stack = None
        self._preview_lines: list[str] = []

        self._step = 0
        self._max_step = 4

        self._group_c_vars: dict[str, tk.BooleanVar] = {}
        self._group_v_vars: dict[str, tk.BooleanVar] = {}
        self._content: ttk.Frame | None = None

        self._build_chrome()
        self._load_ipa()
        self.show_step(0)

    def _build_chrome(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = ttk.Frame(self, padding=12)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        self._header = ttk.Label(outer, text="", font=("Segoe UI", 12, "bold"))
        self._header.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._content_host = ttk.Frame(outer)
        self._content_host.grid(row=1, column=0, sticky="nsew")
        self._content_host.columnconfigure(0, weight=1)
        self._content_host.rowconfigure(0, weight=1)

        nav = ttk.Frame(outer)
        nav.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self._btn_back = ttk.Button(nav, text="← Назад", command=self.go_back)
        self._btn_back.grid(row=0, column=0, padx=(0, 8))

        self._btn_next = ttk.Button(nav, text="Далее →", command=self.go_next)
        self._btn_next.grid(row=0, column=1, padx=(8, 0))

        ttk.Button(nav, text="Выход", command=self.destroy).grid(row=0, column=2, padx=(24, 0))

    def _load_ipa(self):
        self._flat_c, self._flat_v = [], []
        try:
            self.ipa = IPAManager()
        except Exception as e:
            messagebox.showerror("IPA", f"Не удалось загрузить базу звуков:\n{e}")
            self.ipa = None
            return

        gen = PhonologyGenerator(self.ipa)
        c_groups, v_groups = gen.get_available_groups()

        self.bp.allowed_consonant_groups = [g for g in c_groups if g not in DEFAULT_OFF_CONSONANT_GROUPS]
        self.bp.allowed_vowel_groups = list(v_groups)

        self._all_c_by_group, self._all_v_by_group = gen.get_groupped_all_sounds()
        self._flat_c = sorted({s for _gn, syms in self._all_c_by_group.items() for s in syms})
        self._flat_v = sorted({s for _gn, syms in self._all_v_by_group.items() for s in syms})

        for g in c_groups:
            self._group_c_vars[g] = tk.BooleanVar(value=g in self.bp.allowed_consonant_groups)
        for g in v_groups:
            self._group_v_vars[g] = tk.BooleanVar(value=g in self.bp.allowed_vowel_groups)

    def _clear_content(self):
        if self._content:
            self._content.destroy()
        self._content = ttk.Frame(self._content_host)
        self._content.grid(row=0, column=0, sticky="nsew")
        self._content.columnconfigure(0, weight=1)
        self._content.rowconfigure(0, weight=1)

    def show_step(self, n: int):
        self._step = max(0, min(n, self._max_step))
        self._clear_content()

        titles = [
            "Шаг 1. Имя и воспроизводимость",
            "Шаг 2. Фонетический инвентарь",
            "Шаг 3. Слоги и ударение",
            "Шаг 4. Правила произношения и написания",
            "Шаг 5. Предпросмотр",
        ]
        self._header.config(text=titles[self._step])

        inner = ttk.Frame(self._content, padding=4)
        inner.grid(row=0, column=0, sticky="nsew")
        inner.columnconfigure(0, weight=1)
        inner.rowconfigure(0, weight=1)

        if self._step == 0:
            self._build_step_name(inner)
        elif self._step == 1:
            self._build_step_inventory(inner)
        elif self._step == 2:
            self._build_step_syllables(inner)
        elif self._step == 3:
            self._build_step_rules(inner)
        else:
            self._build_step_preview(inner)

        self._btn_back.state(["!disabled"] if self._step > 0 else ["disabled"])
        if self._step < self._max_step:
            self._btn_next.config(text="Далее →")
        else:
            self._btn_next.config(text="Закрыть")

    def go_back(self):
        if self._step <= 0:
            return
        self._collect_current_step()
        self.show_step(self._step - 1)

    def go_next(self):
        self._collect_current_step()
        if not self._validate_after_collect():
            return
        if self._step >= self._max_step:
            self.destroy()
            return
        self.show_step(self._step + 1)

    def _collect_current_step(self):
        if self._step == 0:
            self._collect_step_name()
        elif self._step == 1:
            self._collect_step_inventory()
        elif self._step == 2:
            self._collect_step_syllables()
        elif self._step == 3:
            self._collect_step_rules()

    def _validate_after_collect(self) -> bool:
        if self.ipa is None and self._step != self._max_step:
            messagebox.showwarning("IPA", "База IPA недоступна.")
            return False
        if self._step == 1:
            if self.bp.inventory_mode == "manual":
                if not self.bp.manual_consonant_symbols or not self.bp.manual_vowel_symbols:
                    messagebox.showwarning(
                        "Инвентарь",
                        "В ручном режиме выберите хотя бы один согласный и один гласный.",
                    )
                    return False
            else:
                if not self.bp.allowed_consonant_groups or not self.bp.allowed_vowel_groups:
                    messagebox.showwarning(
                        "Группы", "Отметьте хотя бы одну группу согласных и гласных."
                    )
                    return False
        if self._step == 2:
            if self.bp.min_syllables < 1 or self.bp.max_syllables < self.bp.min_syllables:
                messagebox.showwarning("Слоги", "Проверьте минимум и максимум слогов.")
                return False
        return True

    # --- Step 0 ---
    def _build_step_name(self, parent):
        f = ttk.Frame(parent)
        f.grid(row=0, column=0, sticky="nw")
        ttk.Label(f, text="Название языка").grid(row=0, column=0, sticky="w", pady=4)
        self._ent_name = ttk.Entry(f, width=42)
        self._ent_name.insert(0, self.bp.name)
        self._ent_name.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

        ttk.Label(f, text="Seed (число; пусто — случайный язык)").grid(row=1, column=0, sticky="w", pady=4)
        self._ent_seed = ttk.Entry(f, width=20)
        if self.bp.seed is not None:
            self._ent_seed.insert(0, str(self.bp.seed))
        self._ent_seed.grid(row=1, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(
            f,
            text="Один seed при тех же настройках даёт тот же набор звуков и последовательность слов.",
            wraplength=540,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=12)

        ttk.Button(f, text="Загрузить настройки из JSON…", command=self._load_blueprint_json).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

    def _collect_step_name(self):
        self.bp.name = self._ent_name.get().strip() or "Язык"
        s = self._ent_seed.get().strip()
        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            self.bp.seed = int(s)
        else:
            self.bp.seed = None

    def _load_blueprint_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Загрузить blueprint")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.bp = LanguageBlueprint.from_dict(data)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as e:
            messagebox.showerror("JSON", str(e))
            return
        for g, var in self._group_c_vars.items():
            var.set(g in self.bp.allowed_consonant_groups)
        for g, var in self._group_v_vars.items():
            var.set(g in self.bp.allowed_vowel_groups)
        self._ent_name.delete(0, tk.END)
        self._ent_name.insert(0, self.bp.name)
        self._ent_seed.delete(0, tk.END)
        if self.bp.seed is not None:
            self._ent_seed.insert(0, str(self.bp.seed))
        messagebox.showinfo("Загружено", "Настройки подставлены. Проверьте следующие шаги.")

    # --- Step 1 ---
    def _build_step_inventory(self, parent):
        self._inv_mode = tk.StringVar(value=self.bp.inventory_mode)

        top = ttk.LabelFrame(parent, text="Режим инвентаря", padding=8)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Radiobutton(
            top, text="Авто: группы IPA + число фонем", variable=self._inv_mode, value="auto"
        ).pack(anchor="w")
        ttk.Radiobutton(
            top, text="Вручную: только отмеченные символы", variable=self._inv_mode, value="manual"
        ).pack(anchor="w")

        auto = ttk.LabelFrame(parent, text="Автоподбор", padding=8)
        auto.grid(row=1, column=0, sticky="nsew", pady=6)
        parent.rowconfigure(1, weight=1)

        ttk.Label(auto, text="Сложность (ниже — проще звуки)").grid(row=0, column=0, sticky="w")
        self._scale_complex = ttk.Scale(auto, from_=0.05, to=1.0, orient="horizontal")
        self._scale_complex.set(self.bp.complexity)
        self._scale_complex.grid(row=0, column=1, sticky="ew", padx=8)
        auto.columnconfigure(1, weight=1)

        ttk.Label(auto, text="Число согласных").grid(row=1, column=0, sticky="w", pady=4)
        self._sp_c = tk.Spinbox(auto, from_=6, to=60, width=8)
        self._sp_c.delete(0, tk.END)
        self._sp_c.insert(0, str(self.bp.num_consonants))
        self._sp_c.grid(row=1, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(auto, text="Число гласных").grid(row=2, column=0, sticky="w", pady=4)
        self._sp_v = tk.Spinbox(auto, from_=2, to=24, width=8)
        self._sp_v.delete(0, tk.END)
        self._sp_v.insert(0, str(self.bp.num_vowels))
        self._sp_v.grid(row=2, column=1, sticky="w", padx=8, pady=4)

        self._var_slot_dedup = tk.BooleanVar(value=self.bp.use_consonant_slot_dedup)
        ttk.Checkbutton(
            auto,
            text="Один вариант на «семейство» (r, l, w, клики…) — язык звучит цельнее",
            variable=self._var_slot_dedup,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        grp_fr = ttk.LabelFrame(auto, text="Группы согласных", padding=4)
        grp_fr.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=4)
        auto.rowconfigure(4, weight=1)
        self._fill_scroll_checks(grp_fr, self._group_c_vars)

        grp_v = ttk.LabelFrame(parent, text="Группы гласных", padding=4)
        grp_v.grid(row=2, column=0, sticky="nsew", pady=4)
        self._fill_scroll_checks(grp_v, self._group_v_vars)

        man = ttk.LabelFrame(parent, text="Ручной выбор (стрелки переносят в выбранные)", padding=6)
        man.grid(row=3, column=0, sticky="nsew", pady=6)
        parent.rowconfigure(3, weight=1)
        self._build_manual_lists(man)

    def _fill_scroll_checks(self, parent, vars_map: dict[str, tk.BooleanVar]):
        canvas = tk.Canvas(parent, highlightthickness=0, height=140)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        def _cfg(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", _cfg)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        def _wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _wheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        canvas.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        for i, name in enumerate(sorted(vars_map.keys())):
            ttk.Checkbutton(inner, text=name, variable=vars_map[name]).grid(
                row=i, column=0, sticky="w", padx=6, pady=1
            )

    def _list_column(self, parent, title: str):
        fr = ttk.LabelFrame(parent, text=title, padding=4)
        fr.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        lb = tk.Listbox(fr, selectmode=tk.EXTENDED, height=10, exportselection=False, font=("Segoe UI", 10))
        sb = ttk.Scrollbar(fr, command=lb.yview)
        lb.config(yscrollcommand=sb.set)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        return lb

    def _build_manual_lists(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill=tk.BOTH, expand=True)
        self._lb_c_avail = self._list_column(row, "Согласные — каталог")
        mid = ttk.Frame(row)
        mid.pack(side=tk.LEFT, padx=4)
        ttk.Button(mid, text="→", width=3, command=self._man_c_add).pack(pady=3)
        ttk.Button(mid, text="←", width=3, command=self._man_c_rem).pack(pady=3)
        self._lb_c_sel = self._list_column(row, "Согласные — в языке")
        for s in self._flat_c:
            self._lb_c_avail.insert(tk.END, s)
        for s in self.bp.manual_consonant_symbols:
            self._lb_c_sel.insert(tk.END, s)

        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.BOTH, expand=True, pady=6)
        self._lb_v_avail = self._list_column(row2, "Гласные — каталог")
        mid2 = ttk.Frame(row2)
        mid2.pack(side=tk.LEFT, padx=4)
        ttk.Button(mid2, text="→", width=3, command=self._man_v_add).pack(pady=3)
        ttk.Button(mid2, text="←", width=3, command=self._man_v_rem).pack(pady=3)
        self._lb_v_sel = self._list_column(row2, "Гласные — в языке")
        for s in self._flat_v:
            self._lb_v_avail.insert(tk.END, s)
        for s in self.bp.manual_vowel_symbols:
            self._lb_v_sel.insert(tk.END, s)

    def _man_c_add(self):
        for i in self._lb_c_avail.curselection():
            s = self._lb_c_avail.get(i)
            if s not in self._lb_c_sel.get(0, tk.END):
                self._lb_c_sel.insert(tk.END, s)

    def _man_c_rem(self):
        for i in reversed(self._lb_c_sel.curselection()):
            self._lb_c_sel.delete(i)

    def _man_v_add(self):
        for i in self._lb_v_avail.curselection():
            s = self._lb_v_avail.get(i)
            if s not in self._lb_v_sel.get(0, tk.END):
                self._lb_v_sel.insert(tk.END, s)

    def _man_v_rem(self):
        for i in reversed(self._lb_v_sel.curselection()):
            self._lb_v_sel.delete(i)

    def _collect_step_inventory(self):
        self.bp.inventory_mode = self._inv_mode.get()
        self.bp.complexity = float(self._scale_complex.get())
        try:
            self.bp.num_consonants = int(self._sp_c.get())
            self.bp.num_vowels = int(self._sp_v.get())
        except ValueError:
            pass
        self.bp.use_consonant_slot_dedup = self._var_slot_dedup.get()
        self.bp.allowed_consonant_groups = [g for g, v in self._group_c_vars.items() if v.get()]
        self.bp.allowed_vowel_groups = [g for g, v in self._group_v_vars.items() if v.get()]
        self.bp.manual_consonant_symbols = list(self._lb_c_sel.get(0, tk.END))
        self.bp.manual_vowel_symbols = list(self._lb_v_sel.get(0, tk.END))

    # --- Step 2 ---
    def _build_step_syllables(self, parent):
        f = ttk.Frame(parent)
        f.grid(row=0, column=0, sticky="nw")
        ttk.Label(f, text="Мин. слогов в слове").grid(row=0, column=0, sticky="w", pady=4)
        self._sp_min_syl = tk.Spinbox(f, from_=1, to=12, width=6)
        self._sp_min_syl.delete(0, tk.END)
        self._sp_min_syl.insert(0, str(self.bp.min_syllables))
        self._sp_min_syl.grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(f, text="Макс. слогов").grid(row=1, column=0, sticky="w", pady=4)
        self._sp_max_syl = tk.Spinbox(f, from_=1, to=12, width=6)
        self._sp_max_syl.delete(0, tk.END)
        self._sp_max_syl.insert(0, str(self.bp.max_syllables))
        self._sp_max_syl.grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(f, text="Дифтонгов в системе").grid(row=2, column=0, sticky="w", pady=4)
        self._sp_diph = tk.Spinbox(f, from_=0, to=20, width=6)
        self._sp_diph.delete(0, tk.END)
        self._sp_diph.insert(0, str(self.bp.num_diphthongs))
        self._sp_diph.grid(row=2, column=1, sticky="w", padx=8)

        ttk.Label(f, text="Доля открытых слогов (выше — больше CV, меньше закрытых)").grid(
            row=3, column=0, sticky="w", pady=(12, 4)
        )
        self._scale_open = ttk.Scale(f, from_=0.0, to=1.0, orient="horizontal", length=320)
        self._scale_open.set(self.bp.syllable_openness)
        self._scale_open.grid(row=3, column=1, sticky="w", padx=8)

        ttk.Label(f, text="Ударение (для всего языка)").grid(row=4, column=0, sticky="w", pady=(12, 4))
        self._cb_stress = ttk.Combobox(
            f,
            width=22,
            state="readonly",
            values=("penultimate", "initial", "final", "mixed"),
        )
        self._cb_stress.set(self.bp.stress_pattern)
        self._cb_stress.grid(row=4, column=1, sticky="w", padx=8)

        ttk.Label(
            f,
            text="penultimate — как в латыни; initial / final — фиксированно; mixed — разброс.",
            wraplength=520,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=10)

    def _collect_step_syllables(self):
        try:
            self.bp.min_syllables = int(self._sp_min_syl.get())
            self.bp.max_syllables = int(self._sp_max_syl.get())
            self.bp.num_diphthongs = int(self._sp_diph.get())
        except ValueError:
            pass
        self.bp.syllable_openness = float(self._scale_open.get())
        self.bp.stress_pattern = self._cb_stress.get() or "penultimate"

    # --- Step 3 ---
    def _build_step_rules(self, parent):
        r = self.bp.rules
        self._rb_phon = {}
        checks = [
            ("phon_trim_long_onsets", "Обрезать длинный приступ слога (>2 согласных)"),
            ("phon_trim_long_codas", "Обрезать длинный код"),
            ("phon_voicing_assimilation", "Согласование глух/звонк между слогами"),
            ("phon_nasal_place_assimilation", "Носовой по месту следующего согласного"),
            ("phon_simplify_geminate_across_boundary", "Упростить удвоение на стыке слогов"),
            ("orth_fixed_script", "Один алфавит на слово"),
            ("orth_prefer_primary_grapheme", "Проще буквы (первый вариант из базы)"),
            ("orth_syllable_hyphens", "Дефисы между слогами"),
            ("orth_double_for_identical_adjacent", "Двойные буквы при повторе звука"),
            ("orth_insert_glide_between_vowels", "Glide между гласными на стыке"),
        ]

        box = ttk.LabelFrame(parent, text="Фонетика и написание", padding=8)
        box.grid(row=0, column=0, sticky="nw")
        for i, (attr, label) in enumerate(checks):
            var = tk.BooleanVar(value=getattr(r, attr))
            self._rb_phon[attr] = var
            ttk.Checkbutton(box, text=label, variable=var).grid(row=i, column=0, sticky="w", pady=2)

        scr = ttk.Frame(parent)
        scr.grid(row=1, column=0, sticky="w", pady=12)
        ttk.Label(scr, text="Алфавит для слов").grid(row=0, column=0, sticky="w")
        self._cb_script = ttk.Combobox(
            scr, width=14, state="readonly", values=("latin", "cyrillic", "runes", "mixed")
        )
        self._cb_script.set(r.orth_script)
        self._cb_script.grid(row=0, column=1, padx=8)

    def _collect_step_rules(self):
        r = self.bp.rules
        for attr, var in self._rb_phon.items():
            setattr(r, attr, var.get())
        r.orth_script = self._cb_script.get() or "latin"

    # --- Step 4 preview ---
    def _build_step_preview(self, parent):
        if self.ipa is None:
            ttk.Label(parent, text="IPA недоступна.").pack(anchor="w")
            return

        try:
            self._stack = build_language_stack(self.bp, self.ipa)
        except Exception as e:
            messagebox.showerror("Генерация", str(e))
            ttk.Label(parent, text=f"Ошибка: {e}").pack(anchor="w")
            return

        top = ttk.Frame(parent)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="Обновить примеры", command=self._regenerate_preview).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(top, text="Сохранить настройки JSON…", command=self._save_json).pack(side=tk.LEFT)

        inv = ttk.LabelFrame(parent, text="Инвентарь", padding=6)
        inv.grid(row=1, column=0, sticky="ew", pady=8)
        prof = self._stack.profile
        ttk.Label(
            inv,
            text=f"Согласные ({len(prof.consonants)}): " + " ".join(str(p) for p in prof.consonants),
            wraplength=720,
        ).pack(anchor="w")
        ttk.Label(
            inv,
            text=f"Гласные ({len(prof.vowels)}): " + " ".join(str(p) for p in prof.vowels),
            wraplength=720,
        ).pack(anchor="w")

        txt_fr = ttk.LabelFrame(parent, text="Слова (написание — [фонетика])", padding=6)
        txt_fr.grid(row=2, column=0, sticky="nsew", pady=4)
        parent.rowconfigure(2, weight=1)

        self._txt_prev = tk.Text(txt_fr, height=18, wrap="word", font=("Consolas", 10))
        sb = ttk.Scrollbar(txt_fr, command=self._txt_prev.yview)
        self._txt_prev.config(yscrollcommand=sb.set)
        self._txt_prev.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._regenerate_preview()

    def _regenerate_preview(self):
        if not self._stack:
            return
        wg = self._stack.word_generator
        we = self._stack.word_engine
        words = [wg.generate_word() for _ in range(18)]
        out = we.words_generator(words)
        self._preview_lines = [f"{w.get_orthography()}  —  [{w.get_phonetic()}]" for w in out]
        if hasattr(self, "_txt_prev"):
            self._txt_prev.delete("1.0", tk.END)
            self._txt_prev.insert(tk.END, "\n".join(self._preview_lines))

    def _save_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Сохранить blueprint",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.bp.to_dict(), f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", path)
        except OSError as e:
            messagebox.showerror("Ошибка", str(e))


def run_wizard():
    app = LanguageWizard()
    app.mainloop()
