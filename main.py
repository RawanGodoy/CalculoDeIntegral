import customtkinter as ctk
from tkinter import messagebox

from integracao.parser import converter_funcoes
from integracao.calculos import (
    calcular_integral,
    calcular_area_entre_curvas,
    encontrar_intersecoes
)

from integracao.plotagem import plotar_funcoes

# ==========================================
# CONFIGURAÇÕES
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Calculadora de Integrais")
        self.geometry("800x750")

        self.funcoes_entries = []

        # ==========================================
        # TÍTULO
        # ==========================================

        titulo = ctk.CTkLabel(
            self,
            text="Calculadora de Integrais",
            font=("Arial", 28, "bold")
        )

        titulo.pack(pady=20)

        # ==========================================
        # TUTORIAL
        # ==========================================

        tutorial = (
            "COMO DIGITAR FUNÇÕES:\n\n"
            "x**2   → potência\n"
            "2*x    → multiplicação\n"
            "sin(x) → seno\n"
            "cos(x) → cosseno\n"
            "exp(x) → exponencial\n"
            "log(x) → logaritmo\n"
            "sqrt(x) → raiz quadrada"
        )

        caixa_tutorial = ctk.CTkTextbox(
            self,
            height=150
        )

        caixa_tutorial.pack(
            padx=20,
            pady=10,
            fill="x"
        )

        caixa_tutorial.insert(
            "0.0",
            tutorial
        )

        caixa_tutorial.configure(
            state="disabled"
        )

        # ==========================================
        # QUANTIDADE DE FUNÇÕES
        # ==========================================

        frame_qtd = ctk.CTkFrame(self)

        frame_qtd.pack(
            padx=20,
            pady=10,
            fill="x"
        )

        label_qtd = ctk.CTkLabel(
            frame_qtd,
            text="Quantidade de funções:"
        )

        label_qtd.pack(
            side="left",
            padx=10,
            pady=10
        )

        self.entry_qtd = ctk.CTkEntry(
            frame_qtd,
            width=100
        )

        self.entry_qtd.pack(
            side="left",
            padx=10
        )

        botao_criar = ctk.CTkButton(
            frame_qtd,
            text="Criar Campos",
            command=self.criar_campos_funcoes
        )

        botao_criar.pack(
            side="left",
            padx=10
        )

        # ==========================================
        # FRAME DAS FUNÇÕES
        # ==========================================

        self.frame_funcoes = ctk.CTkScrollableFrame(
            self,
            height=200
        )

        self.frame_funcoes.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

        # ==========================================
        # INTERVALO
        # ==========================================

        frame_intervalo = ctk.CTkFrame(self)

        frame_intervalo.pack(
            padx=20,
            pady=10,
            fill="x"
        )

        label_a = ctk.CTkLabel(
            frame_intervalo,
            text="Limite inferior (a):"
        )

        label_a.grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )

        self.entry_a = ctk.CTkEntry(
            frame_intervalo
        )

        self.entry_a.grid(
            row=0,
            column=1,
            padx=10
        )

        label_b = ctk.CTkLabel(
            frame_intervalo,
            text="Limite superior (b):"
        )

        label_b.grid(
            row=0,
            column=2,
            padx=10
        )

        self.entry_b = ctk.CTkEntry(
            frame_intervalo
        )

        self.entry_b.grid(
            row=0,
            column=3,
            padx=10
        )

        # ==========================================
        # BOTÃO CALCULAR
        # ==========================================

        botao_calcular = ctk.CTkButton(
            self,
            text="Calcular",
            command=self.calcular
        )

        botao_calcular.pack(
            pady=20
        )

        # ==========================================
        # RESULTADOS
        # ==========================================

        self.texto_resultado = ctk.CTkTextbox(
            self,
            height=220
        )

        self.texto_resultado.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

    # ==========================================
    # CRIAR CAMPOS
    # ==========================================

    def criar_campos_funcoes(self):

        for widget in self.frame_funcoes.winfo_children():
            widget.destroy()

        self.funcoes_entries.clear()

        try:

            quantidade = int(
                self.entry_qtd.get()
            )

            for i in range(quantidade):

                label = ctk.CTkLabel(
                    self.frame_funcoes,
                    text=f"Função {i+1}:"
                )

                label.pack(
                    pady=(10, 0)
                )

                entry = ctk.CTkEntry(
                    self.frame_funcoes,
                    width=500,
                    placeholder_text="Ex: x**2 + 2*x"
                )

                entry.pack(
                    pady=5
                )

                self.funcoes_entries.append(entry)

        except:

            messagebox.showerror(
                "Erro",
                "Digite uma quantidade válida."
            )

    # ==========================================
    # CALCULAR
    # ==========================================

    def calcular(self):

        try:

            funcoes_str = [
                entry.get()
                for entry in self.funcoes_entries
            ]

            a = float(
                self.entry_a.get()
            )

            b = float(
                self.entry_b.get()
            )

            funcoes_sympy, funcoes_numpy = (
                converter_funcoes(funcoes_str)
            )

            self.texto_resultado.delete(
                "1.0",
                "end"
            )

            # ======================================
            # INTEGRAIS
            # ======================================

            for f_sym in funcoes_sympy:

                integral = calcular_integral(
                    f_sym,
                    a,
                    b
                )

                texto = (
                    f"Função: {f_sym}\n"
                    f"Integral exata: {integral}\n\n"
                )

                self.texto_resultado.insert(
                    "end",
                    texto
                )

            # ======================================
            # ÁREA ENTRE CURVAS
            # ======================================

            if len(funcoes_sympy) >= 2:

                f1 = funcoes_sympy[0]
                f2 = funcoes_sympy[1]

                intersecoes = encontrar_intersecoes(
                    f1,
                    f2,
                    a,
                    b
                )

                area = calcular_area_entre_curvas(
                    f1,
                    f2,
                    a,
                    b
                )

                texto_area = (
                    "========================\n"
                    "ÁREA ENTRE CURVAS\n\n"
                    f"Interseções: {intersecoes}\n"
                    f"Área entre curvas: {area}\n\n"
                )

                self.texto_resultado.insert(
                    "end",
                    texto_area
                )

            # ======================================
            # PLOTAGEM
            # ======================================

            plotar_funcoes(
                funcoes_sympy,
                funcoes_numpy,
                a,
                b
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                str(erro))


# ==========================================
# EXECUÇÃO
# ==========================================

app = App()
app.mainloop()
