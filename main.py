import customtkinter as ctk
from tkinter import messagebox

from integracao.parser import converter_funcoes
from integracao.calculos import (
    calcular_integral,
    calcular_area_entre_curvas,
    encontrar_intersecoes,
    calcular_volume_discos,
    calcular_volume_cascas,
)
from integracao.plotagem import (
    plotar_funcoes,
    plotar_volume_discos,
    plotar_volume_cascas,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COR_BG        = "#0D0F14"
COR_PAINEL    = "#13161E"
COR_CARD      = "#1A1E2A"
COR_BORDA     = "#252A3A"
COR_ACENTO    = "#4F7EFF"
COR_ACENTO2   = "#3B2A5C"
COR_TEXTO     = "#E8EAF0"
COR_TEXTO_DIM = "#6B7280"
COR_SUCESSO   = "#10B981"
COR_ENTRY_BG  = "#0F1219"


class LabelSecao(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text.upper(),
            font=("Courier New", 10, "bold"),
            text_color=COR_ACENTO,
            **kwargs
        )


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("∫ Calculadora de Integrais")
        self.geometry("860x960")
        self.minsize(780, 860)
        self.configure(fg_color=COR_BG)
        self.funcoes_entries = []
        self._construir_interface()

    # ══════════════════════════════════════
    # INTERFACE
    # ══════════════════════════════════════

    def _construir_interface(self):

        # ── CABEÇALHO ─────────────────────
        cab = ctk.CTkFrame(self, fg_color=COR_PAINEL, corner_radius=0)
        cab.pack(fill="x")
        ctk.CTkFrame(cab, height=3, fg_color=COR_ACENTO, corner_radius=0).pack(fill="x")

        inner_cab = ctk.CTkFrame(cab, fg_color="transparent")
        inner_cab.pack(padx=30, pady=16, fill="x")

        ctk.CTkLabel(
            inner_cab, text="∫",
            font=("Georgia", 34, "bold"), text_color=COR_ACENTO
        ).pack(side="left", padx=(0, 12))

        bloco = ctk.CTkFrame(inner_cab, fg_color="transparent")
        bloco.pack(side="left")
        ctk.CTkLabel(
            bloco, text="Calculadora de Integrais",
            font=("Georgia", 21, "bold"), text_color=COR_TEXTO
        ).pack(anchor="w")
        ctk.CTkLabel(
            bloco, text="Cálculo simbólico · Área entre curvas · Volume de sólidos",
            font=("Courier New", 11), text_color=COR_TEXTO_DIM
        ).pack(anchor="w")

        # ── CORPO ─────────────────────────
        corpo = ctk.CTkScrollableFrame(
            self, fg_color=COR_BG,
            scrollbar_button_color=COR_BORDA,
            scrollbar_button_hover_color=COR_ACENTO
        )
        corpo.pack(fill="both", expand=True)

        # ── CARD: SINTAXE ──────────────────
        card_sint = self._card(corpo)
        LabelSecao(card_sint, text="sintaxe").pack(anchor="w", pady=(0, 8))

        exemplos = [
            ("x**2",    "potência"),
            ("2*x",     "multiplicação"),
            ("sin(x)",  "seno"),
            ("cos(x)",  "cosseno"),
            ("exp(x)",  "exponencial"),
            ("log(x)",  "logaritmo natural"),
            ("sqrt(x)", "raiz quadrada"),
            ("pi",      "π"),
        ]

        tabela = ctk.CTkFrame(card_sint, fg_color="#12151F", corner_radius=6)
        tabela.pack(fill="x")

        for i, (sintaxe, desc) in enumerate(exemplos):
            linha = ctk.CTkFrame(
                tabela,
                fg_color="#12151F" if i % 2 == 0 else "#0F1219",
                corner_radius=0
            )
            linha.pack(fill="x")
            ctk.CTkLabel(
                linha, text=sintaxe,
                font=("Courier New", 12, "bold"),
                text_color=COR_ACENTO, width=110, anchor="w"
            ).pack(side="left", padx=(14, 0), pady=6)
            ctk.CTkLabel(
                linha, text=desc,
                font=("Courier New", 11),
                text_color=COR_TEXTO_DIM, anchor="w"
            ).pack(side="left", padx=(6, 14), pady=6)

        # ── CARD: FUNÇÕES ──────────────────
        card_func = self._card(corpo)
        LabelSecao(card_func, text="funções").pack(anchor="w", pady=(0, 10))

        frame_qtd = ctk.CTkFrame(card_func, fg_color="transparent")
        frame_qtd.pack(fill="x")

        ctk.CTkLabel(
            frame_qtd, text="Quantidade de funções",
            font=("Courier New", 12), text_color=COR_TEXTO
        ).pack(side="left")

        self.entry_qtd = ctk.CTkEntry(
            frame_qtd, width=70, height=36,
            fg_color=COR_ENTRY_BG, border_color=COR_BORDA,
            text_color=COR_TEXTO, font=("Courier New", 13), corner_radius=6
        )
        self.entry_qtd.pack(side="left", padx=12)

        ctk.CTkButton(
            frame_qtd, text="Criar Campos",
            command=self.criar_campos_funcoes,
            height=36, fg_color=COR_ACENTO, hover_color="#3D6BE0",
            font=("Courier New", 12, "bold"), corner_radius=6
        ).pack(side="left")

        ctk.CTkFrame(card_func, height=1, fg_color=COR_BORDA).pack(fill="x", pady=12)

        self.frame_funcoes = ctk.CTkFrame(card_func, fg_color="transparent")
        self.frame_funcoes.pack(fill="x")

        # ── CARD: INTERVALO ────────────────
        card_int = self._card(corpo)
        LabelSecao(card_int, text="intervalo de integração").pack(anchor="w", pady=(0, 10))

        frame_lim = ctk.CTkFrame(card_int, fg_color="transparent")
        frame_lim.pack(fill="x")

        for txt, attr in [("a =", "entry_a"), ("b =", "entry_b")]:
            bloco = ctk.CTkFrame(frame_lim, fg_color="transparent")
            bloco.pack(side="left", padx=(0, 28))
            ctk.CTkLabel(
                bloco, text=txt,
                font=("Courier New", 13, "bold"), text_color=COR_TEXTO_DIM
            ).pack(side="left", padx=(0, 8))
            e = ctk.CTkEntry(
                bloco, width=110, height=38,
                fg_color=COR_ENTRY_BG, border_color=COR_BORDA,
                text_color=COR_TEXTO, font=("Courier New", 14), corner_radius=6
            )
            e.pack(side="left")
            setattr(self, attr, e)

        # ── CARD: VOLUME ───────────────────
        card_vol = self._card(corpo)
        LabelSecao(card_vol, text="volume do sólido de revolução").pack(anchor="w", pady=(0, 10))

        # Descrições dos métodos
        desc_frame = ctk.CTkFrame(card_vol, fg_color="#12151F", corner_radius=6)
        desc_frame.pack(fill="x", pady=(0, 12))

        metodos_info = [
            ("Discos / Arruelas",
             "Gira em torno do eixo X  →  V = π ∫ [f(x)]² dx"),
            ("Cascas Cilíndricas",
             "Gira em torno do eixo Y  →  V = 2π ∫ x·f(x) dx"),
        ]

        for i, (nome, formula) in enumerate(metodos_info):
            row = ctk.CTkFrame(
                desc_frame,
                fg_color="#12151F" if i % 2 == 0 else "#0F1219",
                corner_radius=0
            )
            row.pack(fill="x")
            ctk.CTkLabel(
                row, text=nome,
                font=("Courier New", 11, "bold"),
                text_color=COR_ACENTO, width=150, anchor="w"
            ).pack(side="left", padx=(14, 0), pady=6)
            ctk.CTkLabel(
                row, text=formula,
                font=("Courier New", 11),
                text_color=COR_TEXTO_DIM, anchor="w"
            ).pack(side="left", padx=(8, 14), pady=6)

        # Checkboxes de seleção
        self.var_discos = ctk.BooleanVar(value=False)
        self.var_cascas = ctk.BooleanVar(value=False)

        checks_frame = ctk.CTkFrame(card_vol, fg_color="transparent")
        checks_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkCheckBox(
            checks_frame,
            text="Calcular pelo método dos Discos (eixo X)",
            variable=self.var_discos,
            font=("Courier New", 12),
            text_color=COR_TEXTO,
            fg_color=COR_ACENTO,
            hover_color="#3D6BE0",
            border_color=COR_BORDA,
            checkmark_color="white"
        ).pack(anchor="w", pady=4)

        ctk.CTkCheckBox(
            checks_frame,
            text="Calcular pelo método das Cascas (eixo Y)",
            variable=self.var_cascas,
            font=("Courier New", 12),
            text_color=COR_TEXTO,
            fg_color=COR_ACENTO,
            hover_color="#3D6BE0",
            border_color=COR_BORDA,
            checkmark_color="white"
        ).pack(anchor="w", pady=4)

        # ── BOTÃO CALCULAR ─────────────────
        frame_btn = ctk.CTkFrame(corpo, fg_color="transparent")
        frame_btn.pack(pady=6, padx=24, fill="x")

        ctk.CTkButton(
            frame_btn, text="Calcular",
            command=self.calcular,
            height=44, fg_color=COR_ACENTO2, hover_color="#4A3570",
            font=("Georgia", 14, "bold"), corner_radius=8,
            border_width=1, border_color="#5B3F8A"
        ).pack(fill="x")

        # ── CARD: RESULTADOS ───────────────
        card_res = self._card(corpo)
        LabelSecao(card_res, text="resultados").pack(anchor="w", pady=(0, 8))

        self.texto_resultado = ctk.CTkTextbox(
            card_res, height=220,
            fg_color=COR_ENTRY_BG, border_color=COR_BORDA,
            border_width=1, text_color=COR_SUCESSO,
            font=("Courier New", 12), corner_radius=6,
            scrollbar_button_color=COR_BORDA
        )
        self.texto_resultado.pack(fill="both", expand=True)
        self.texto_resultado.insert("0.0", "// Os resultados aparecerão aqui...\n")
        self.texto_resultado.configure(state="disabled")

    # ══════════════════════════════════════
    # HELPER CARD
    # ══════════════════════════════════════

    def _card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=COR_CARD,
            corner_radius=10, border_width=1, border_color=COR_BORDA
        )
        card.pack(fill="x", padx=24, pady=7)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)
        return inner

    # ══════════════════════════════════════
    # CRIAR CAMPOS
    # ══════════════════════════════════════

    def criar_campos_funcoes(self):
        for w in self.frame_funcoes.winfo_children():
            w.destroy()
        self.funcoes_entries.clear()

        try:
            qtd = int(self.entry_qtd.get())
            if qtd <= 0:
                raise ValueError("Deve ser maior que zero.")

            cores = [COR_ACENTO, "#F87171", "#34D399", "#FBBF24", "#A78BFA"]

            for i in range(qtd):
                linha = ctk.CTkFrame(self.frame_funcoes, fg_color="transparent")
                linha.pack(fill="x", pady=5)

                ctk.CTkLabel(
                    linha, text=f"f{i+1}(x) =",
                    font=("Courier New", 13, "bold"),
                    text_color=cores[i % len(cores)],
                    width=72, anchor="e"
                ).pack(side="left", padx=(0, 10))

                entry = ctk.CTkEntry(
                    linha, height=38,
                    fg_color=COR_ENTRY_BG, border_color=COR_BORDA,
                    text_color=COR_TEXTO, font=("Courier New", 13),
                    placeholder_text="Ex: x**2 + 2*x",
                    placeholder_text_color=COR_TEXTO_DIM,
                    corner_radius=6
                )
                entry.pack(side="left", fill="x", expand=True)
                self.funcoes_entries.append(entry)

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    # ══════════════════════════════════════
    # CALCULAR
    # ══════════════════════════════════════

    def calcular(self):
        try:
            funcoes_str = [e.get() for e in self.funcoes_entries]

            if not funcoes_str:
                raise ValueError("Crie os campos de função antes de calcular.")

            a_str = self.entry_a.get().strip()
            b_str = self.entry_b.get().strip()

            if not a_str or not b_str:
                raise ValueError("Preencha os limites de integração.")

            a, b = float(a_str), float(b_str)

            if a >= b:
                raise ValueError("O limite 'a' deve ser menor que 'b'.")

            funcoes_sympy, funcoes_numpy = converter_funcoes(funcoes_str)

            self.texto_resultado.configure(state="normal")
            self.texto_resultado.delete("1.0", "end")
            self.texto_resultado.insert("end", f"[ Intervalo: {a} → {b} ]\n\n")

            # ── Integrais ──────────────────
            for i, f_sym in enumerate(funcoes_sympy):
                integral = calcular_integral(f_sym, a, b)
                self.texto_resultado.insert(
                    "end",
                    f"  f{i+1}(x) = {f_sym}\n"
                    f"  ∫ f{i+1} dx  =  {integral}\n\n"
                )

            # ── Área entre curvas ──────────
            if len(funcoes_sympy) >= 2:
                f1_sym, f2_sym = funcoes_sympy[0], funcoes_sympy[1]
                intersecoes = encontrar_intersecoes(f1_sym, f2_sym, a, b)
                area = calcular_area_entre_curvas(f1_sym, f2_sym, a, b)

                ints_fmt = (
                    ", ".join(f"{xi:.5f}" for xi in intersecoes)
                    if intersecoes else "nenhuma no intervalo"
                )

                self.texto_resultado.insert(
                    "end",
                    "─" * 40 + "\n"
                    "  ÁREA ENTRE CURVAS\n\n"
                    f"  Interseções : {ints_fmt}\n"
                    f"  Área exata  : {area}\n\n"
                )

            # ── Volume — Discos ────────────
            if self.var_discos.get():
                f1_sym = funcoes_sympy[0]
                f2_sym = funcoes_sympy[1] if len(funcoes_sympy) >= 2 else None
                f2_num = funcoes_numpy[1] if len(funcoes_numpy) >= 2 else None

                vol = calcular_volume_discos(f1_sym, a, b, f2_sym)

                metodo = "arruelas (f1² − f2²)" if f2_sym else "discos (f1²)"

                self.texto_resultado.insert(
                    "end",
                    "─" * 40 + "\n"
                    "  VOLUME — EIXO X (Discos)\n\n"
                    f"  Método       : {metodo}\n"
                    f"  Volume exato : {vol}\n\n"
                )

                plotar_volume_discos(funcoes_numpy, a, b, f2_num)

            # ── Volume — Cascas ────────────
            if self.var_cascas.get():
                f1_sym = funcoes_sympy[0]
                f2_sym = funcoes_sympy[1] if len(funcoes_sympy) >= 2 else None
                f2_num = funcoes_numpy[1] if len(funcoes_numpy) >= 2 else None

                vol = calcular_volume_cascas(f1_sym, a, b, f2_sym)

                metodo = "cascas entre f1 e f2" if f2_sym else "cascas (f1)"

                self.texto_resultado.insert(
                    "end",
                    "─" * 40 + "\n"
                    "  VOLUME — EIXO Y (Cascas)\n\n"
                    f"  Método       : {metodo}\n"
                    f"  Volume exato : {vol}\n\n"
                )

                plotar_volume_cascas(funcoes_numpy, a, b, f2_num)

            self.texto_resultado.configure(state="disabled")

            # Gráfico 2D sempre ao final
            plotar_funcoes(funcoes_sympy, funcoes_numpy, a, b)

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))


app = App()
app.mainloop()