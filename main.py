import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from integracao.parser import converter_funcoes
from integracao.calculos import (
    calcular_integral,
    calcular_area_entre_curvas,
    encontrar_intersecoes,
    calcular_volume_discos,
    calcular_volume_cascas,
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── Paleta Google Classroom-inspired ───────────────────────────────
BG          = "#F0F4F8"   # cinza-azulado muito suave
SURFACE     = "#FFFFFF"   # cards / sidebar
SURFACE2    = "#F8F9FA"   # inputs / linhas alt
BORDER      = "#DADCE0"   # bordas Google
ACCENT      = "#1A73E8"   # azul Google
ACCENT_DARK = "#1557B0"
ACCENT_SOFT = "#E8F0FE"   # azul bem claro (badge / hover)
GREEN       = "#188038"   # verde Google
GREEN_SOFT  = "#E6F4EA"
TEAL        = "#007B83"
TEXT        = "#202124"   # quase preto Google
TEXT2       = "#5F6368"   # cinza médio Google
TEXT3       = "#BDC1C6"   # placeholder
RESULT_VAL  = "#1A73E8"   # valores em azul
TAG_COLORS  = ["#1A73E8","#D93025","#188038","#E37400","#7627BB"]

F_LABEL     = ("Inter", 12)
F_BOLD      = ("Inter", 12, "bold")
F_SMALL     = ("Inter", 10)
F_SECAO     = ("Inter", 10, "bold")
F_MONO      = ("Courier New", 12)
F_MONO_S    = ("Courier New", 11)


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Calculadora de Integrais")
        self.geometry("1160x840")
        self.minsize(960, 720)
        self.configure(fg_color=BG)
        self.funcoes_entries = []
        self._fig = None
        self._ultimo_calculo = None
        self._construir_layout()

    # ════════════════════════════════════════════════════════════════
    # LAYOUT RAIZ
    # ════════════════════════════════════════════════════════════════

    def _construir_layout(self):
        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        # Sidebar
        self._sidebar = ctk.CTkScrollableFrame(
            root, width=360,
            fg_color=SURFACE, corner_radius=0,
            border_width=0,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT3,
        )
        self._sidebar.pack(side="left", fill="y")

        # Divisor sutil
        ctk.CTkFrame(root, width=1, fg_color=BORDER,
                     corner_radius=0).pack(side="left", fill="y")

        # Painel direito
        self._painel = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
        self._painel.pack(side="left", fill="both", expand=True)

        self._construir_sidebar()
        self._construir_painel()

    # ════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ════════════════════════════════════════════════════════════════

    def _construir_sidebar(self):
        sb = self._sidebar

        # ── Header ──────────────────────────────────────────────────
        hdr = ctk.CTkFrame(sb, fg_color=ACCENT, corner_radius=0)
        hdr.pack(fill="x")

        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            inner, text="∫",
            font=("Georgia", 30, "bold"),
            text_color="white"
        ).pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text="Calculadora de Integrais",
                     font=("Inter", 14, "bold"),
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(info, text="Simbólico  ·  Área  ·  Volume",
                     font=("Inter", 10),
                     text_color="#C5D8FF").pack(anchor="w")

        # ── Sintaxe ──────────────────────────────────────────────────
        self._section(sb, "Sintaxe")

        exemplos = [
            ("x**2",    "potência"),
            ("2*x",     "multiplicação"),
            ("sin(x)",  "seno"),
            ("cos(x)",  "cosseno"),
            ("exp(x)",  "exponencial"),
            ("log(x)",  "logaritmo"),
            ("sqrt(x)", "raiz quadrada"),
            ("pi",      "π"),
        ]

        tbl = ctk.CTkFrame(sb, fg_color=SURFACE,
                           corner_radius=8,
                           border_width=1, border_color=BORDER)
        tbl.pack(fill="x", padx=16, pady=(0, 12))

        for i, (s, d) in enumerate(exemplos):
            bg = SURFACE if i % 2 == 0 else SURFACE2
            row = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            ctk.CTkLabel(row, text=s, font=F_MONO,
                         text_color=ACCENT, width=95, anchor="w"
                         ).pack(side="left", padx=(12, 0), pady=5)
            ctk.CTkLabel(row, text=d, font=F_MONO_S,
                         text_color=TEXT2, anchor="w"
                         ).pack(side="left", padx=(6, 12))

        self._div(sb)

        # ── Funções ───────────────────────────────────────────────────
        self._section(sb, "Funções")

        frow = ctk.CTkFrame(sb, fg_color="transparent")
        frow.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(frow, text="Quantidade",
                     font=F_LABEL, text_color=TEXT2
                     ).pack(side="left")

        self.entry_qtd = ctk.CTkEntry(
            frow, width=58, height=32,
            fg_color=SURFACE2, border_color=BORDER,
            text_color=TEXT, font=F_MONO,
            corner_radius=6
        )
        self.entry_qtd.pack(side="left", padx=10)

        ctk.CTkButton(
            frow, text="Criar campos",
            command=self.criar_campos_funcoes,
            height=32,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="white",
            font=("Inter", 11, "bold"),
            corner_radius=6
        ).pack(side="left")

        ctk.CTkFrame(sb, height=1,
                     fg_color=BORDER).pack(fill="x", padx=16, pady=8)

        self.frame_funcoes = ctk.CTkFrame(sb, fg_color="transparent")
        self.frame_funcoes.pack(fill="x", padx=16)

        self._div(sb)

        # ── Intervalo ─────────────────────────────────────────────────
        self._section(sb, "Intervalo de integração")

        irow = ctk.CTkFrame(sb, fg_color="transparent")
        irow.pack(fill="x", padx=16, pady=(0, 12))

        for txt, attr in [("a =", "entry_a"), ("b =", "entry_b")]:
            bloco = ctk.CTkFrame(irow, fg_color="transparent")
            bloco.pack(side="left", padx=(0, 20))
            ctk.CTkLabel(bloco, text=txt,
                         font=("Courier New", 13, "bold"),
                         text_color=TEXT2
                         ).pack(side="left", padx=(0, 6))
            e = ctk.CTkEntry(
                bloco, width=90, height=34,
                fg_color=SURFACE2, border_color=BORDER,
                text_color=TEXT, font=F_MONO,
                corner_radius=6
            )
            e.pack(side="left")
            setattr(self, attr, e)

        self._div(sb)

        # ── Volume ─────────────────────────────────────────────────────
        self._section(sb, "Volume do sólido")

        vol_card = ctk.CTkFrame(sb, fg_color=ACCENT_SOFT,
                                corner_radius=8,
                                border_width=1, border_color="#C5D8FF")
        vol_card.pack(fill="x", padx=16, pady=(0, 10))

        for nome, formula in [
            ("Discos — eixo X",  "V = π ∫ f(x)² dx"),
            ("Cascas — eixo Y",  "V = 2π ∫ x·f(x) dx"),
        ]:
            r = ctk.CTkFrame(vol_card, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(r, text=nome,
                         font=("Inter", 10, "bold"),
                         text_color=ACCENT, width=130, anchor="w"
                         ).pack(side="left")
            ctk.CTkLabel(r, text=formula,
                         font=F_MONO_S, text_color=TEXT2, anchor="w"
                         ).pack(side="left")

        self.var_discos = ctk.BooleanVar(value=False)
        self.var_cascas = ctk.BooleanVar(value=False)

        cf = ctk.CTkFrame(sb, fg_color="transparent")
        cf.pack(fill="x", padx=16, pady=(0, 12))

        for texto, var in [
            ("Calcular por Discos (eixo X)", self.var_discos),
            ("Calcular por Cascas (eixo Y)", self.var_cascas),
        ]:
            ctk.CTkCheckBox(
                cf, text=texto, variable=var,
                font=F_LABEL, text_color=TEXT,
                fg_color=ACCENT, hover_color=ACCENT_DARK,
                border_color=BORDER, checkmark_color="white",
                corner_radius=4
            ).pack(anchor="w", pady=4)

        self._div(sb)

        # ── Botão Calcular ─────────────────────────────────────────────
        ctk.CTkButton(
            sb, text="Calcular",
            command=self.calcular,
            height=44,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="white",
            font=("Inter", 14, "bold"),
            corner_radius=8,
        ).pack(fill="x", padx=16, pady=(10, 16))

    # ════════════════════════════════════════════════════════════════
    # PAINEL DIREITO
    # ════════════════════════════════════════════════════════════════

    def _construir_painel(self):
        p = self._painel

        # ── Barra de abas ─────────────────────────────────────────────
        tabbar = ctk.CTkFrame(p, fg_color=SURFACE,
                              corner_radius=0, height=48)
        tabbar.pack(fill="x")
        tabbar.pack_propagate(False)

        ctk.CTkFrame(tabbar, height=1, fg_color=BORDER,
                     corner_radius=0).pack(fill="x", side="bottom")

        self._tab_btn   = {}
        self._tab_frame = {}

        conteudo = ctk.CTkFrame(p, fg_color=BG, corner_radius=0)
        conteudo.pack(fill="both", expand=True)

        for nome in ["Gráfico", "Resultados"]:
            frame = ctk.CTkFrame(conteudo, fg_color=BG, corner_radius=0)
            self._tab_frame[nome] = frame

            btn = ctk.CTkButton(
                tabbar, text=nome,
                command=lambda n=nome: self._mudar_aba(n),
                height=46, width=120,
                fg_color="transparent",
                hover_color=ACCENT_SOFT,
                text_color=TEXT2,
                font=("Inter", 13, "bold"),
                corner_radius=0,
            )
            btn.pack(side="left")
            self._tab_btn[nome] = btn

        # ── Aba Gráfico ───────────────────────────────────────────────
        gf = self._tab_frame["Gráfico"]

        sel = ctk.CTkFrame(gf, fg_color=SURFACE,
                           corner_radius=0)
        sel.pack(fill="x")
        ctk.CTkFrame(sel, height=1, fg_color=BORDER).pack(fill="x", side="bottom")

        ctk.CTkLabel(sel, text="Visualizar:",
                     font=F_LABEL, text_color=TEXT2
                     ).pack(side="left", padx=(16, 8), pady=10)

        self.var_grafico = ctk.StringVar(value="2D")
        for opcao in ["2D", "3D — Discos", "3D — Cascas"]:
            ctk.CTkRadioButton(
                sel, text=opcao,
                variable=self.var_grafico, value=opcao,
                command=self._atualizar_grafico,
                font=F_LABEL,
                text_color=TEXT,
                fg_color=ACCENT,
                hover_color=ACCENT_DARK,
                border_color=BORDER,
            ).pack(side="left", padx=12, pady=10)

        self._graf_container = ctk.CTkFrame(
            gf, fg_color=SURFACE,
            corner_radius=12,
            border_width=1, border_color=BORDER
        )
        self._graf_container.pack(fill="both", expand=True,
                                  padx=16, pady=12)

        self._placeholder()

        # ── Aba Resultados ────────────────────────────────────────────
        rf = self._tab_frame["Resultados"]

        rh = ctk.CTkFrame(rf, fg_color=SURFACE, corner_radius=0)
        rh.pack(fill="x")
        ctk.CTkFrame(rh, height=1, fg_color=BORDER).pack(fill="x", side="bottom")

        rh_inner = ctk.CTkFrame(rh, fg_color="transparent")
        rh_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(rh_inner, text="Resultados",
                     font=("Inter", 13, "bold"), text_color=TEXT
                     ).pack(side="left")

        ctk.CTkButton(
            rh_inner, text="Limpar",
            command=self._limpar_resultados,
            height=28, width=68,
            fg_color=SURFACE2, hover_color=BORDER,
            text_color=TEXT2, font=("Inter", 11),
            corner_radius=6, border_width=1, border_color=BORDER
        ).pack(side="right")

        self._scroll_res = ctk.CTkScrollableFrame(
            rf, fg_color=BG, corner_radius=0,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT3,
        )
        self._scroll_res.pack(fill="both", expand=True)

        self._mudar_aba("Gráfico")

    # ════════════════════════════════════════════════════════════════
    # HELPERS UI
    # ════════════════════════════════════════════════════════════════

    def _section(self, parent, texto):
        ctk.CTkLabel(parent, text=texto,
                     font=("Inter", 11, "bold"),
                     text_color=TEXT
                     ).pack(anchor="w", padx=16, pady=(14, 6))

    def _div(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color=BORDER,
                     corner_radius=0).pack(fill="x", pady=2)

    def _mudar_aba(self, nome):
        for n, f in self._tab_frame.items():
            f.pack_forget()
        self._tab_frame[nome].pack(fill="both", expand=True)
        for n, b in self._tab_btn.items():
            if n == nome:
                b.configure(fg_color=ACCENT_SOFT, text_color=ACCENT)
            else:
                b.configure(fg_color="transparent", text_color=TEXT2)

    def _placeholder(self):
        for w in self._graf_container.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._graf_container,
            text="Clique em Calcular para gerar o gráfico.",
            font=("Inter", 13), text_color=TEXT3,
            justify="center"
        ).pack(expand=True)

    def _limpar_resultados(self):
        for w in self._scroll_res.winfo_children():
            w.destroy()

    def _add_card(self, titulo, linhas, cor=None):
        if cor is None:
            cor = ACCENT

        outer = ctk.CTkFrame(
            self._scroll_res,
            fg_color=SURFACE,
            corner_radius=10,
            border_width=1, border_color=BORDER
        )
        outer.pack(fill="x", padx=16, pady=6)

        # topo colorido suave
        topo = ctk.CTkFrame(outer, fg_color=ACCENT_SOFT,
                            corner_radius=8)
        topo.pack(fill="x", padx=10, pady=(10, 0))

        # ponto colorido + título
        dot_row = ctk.CTkFrame(topo, fg_color="transparent")
        dot_row.pack(fill="x", padx=10, pady=8)

        ctk.CTkFrame(dot_row, width=10, height=10,
                     fg_color=cor, corner_radius=5
                     ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(dot_row, text=titulo,
                     font=("Inter", 12, "bold"),
                     text_color=cor
                     ).pack(side="left")

        # linhas de dados
        body = ctk.CTkFrame(outer, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(8, 12))

        for i, (chave, valor) in enumerate(linhas):
            row = ctk.CTkFrame(body,
                               fg_color=SURFACE if i % 2 == 0 else SURFACE2,
                               corner_radius=6)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=chave,
                         font=("Inter", 10),
                         text_color=TEXT2,
                         width=110, anchor="w"
                         ).pack(side="left", padx=(10, 0), pady=6)

            ctk.CTkLabel(row, text=str(valor),
                         font=F_MONO,
                         text_color=ACCENT,
                         anchor="w", wraplength=330
                         ).pack(side="left", padx=(8, 10), pady=6)

    # ════════════════════════════════════════════════════════════════
    # CRIAR CAMPOS
    # ════════════════════════════════════════════════════════════════

    def criar_campos_funcoes(self):
        for w in self.frame_funcoes.winfo_children():
            w.destroy()
        self.funcoes_entries.clear()

        try:
            qtd = int(self.entry_qtd.get())
            if qtd <= 0:
                raise ValueError

            for i in range(qtd):
                row = ctk.CTkFrame(self.frame_funcoes,
                                   fg_color="transparent")
                row.pack(fill="x", pady=4)

                ctk.CTkLabel(
                    row, text=f"f{i+1}(x) =",
                    font=("Courier New", 12, "bold"),
                    text_color=TAG_COLORS[i % len(TAG_COLORS)],
                    width=68, anchor="e"
                ).pack(side="left", padx=(0, 8))

                e = ctk.CTkEntry(
                    row, height=34,
                    fg_color=SURFACE2, border_color=BORDER,
                    text_color=TEXT, font=F_MONO,
                    placeholder_text="ex: x**2 + 1",
                    placeholder_text_color=TEXT3,
                    corner_radius=6
                )
                e.pack(side="left", fill="x", expand=True)
                self.funcoes_entries.append(e)

        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida.")

    # ════════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ════════════════════════════════════════════════════════════════

    def _embed(self, fig):
        for w in self._graf_container.winfo_children():
            w.destroy()
        if self._fig:
            plt.close(self._fig)
        self._fig = fig

        canvas = FigureCanvasTkAgg(fig, master=self._graf_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ── Barra de ferramentas ─────────────────────────────────────
        toolbar_frame = tk.Frame(
            self._graf_container,
            bg=SURFACE2, bd=0, highlightthickness=0
        )
        toolbar_frame.pack(fill="x", side="bottom")

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.config(bg=SURFACE2)
        toolbar.update()

        # Botão "Ver tudo" — restaura zoom original
        tk.Button(
            toolbar_frame,
            text="⟲  Ver tudo",
            command=lambda: self._reset_zoom(fig, canvas),
            bg=ACCENT_SOFT, fg=ACCENT,
            font=("Inter", 10, "bold"),
            relief="flat", bd=0,
            padx=10, pady=3,
            cursor="hand2",
            activebackground=ACCENT_SOFT,
            activeforeground=ACCENT_DARK,
        ).pack(side="right", padx=8, pady=4)

        self._canvas_atual = canvas
        self._ax_limites_originais = self._capturar_limites(fig)

    def _capturar_limites(self, fig):
        """Guarda xlim/ylim originais de todos os axes 2D."""
        limites = {}
        for ax in fig.get_axes():
            if not hasattr(ax, "get_zlim"):
                limites[ax] = (ax.get_xlim(), ax.get_ylim())
        return limites

    def _reset_zoom(self, fig, canvas):
        """Restaura o zoom para o estado original."""
        if not hasattr(self, "_ax_limites_originais"):
            return
        for ax, (xlim, ylim) in self._ax_limites_originais.items():
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
        canvas.draw_idle()

    def _style_ax(self, ax, titulo):
        ax.set_title(titulo, fontsize=11, color=TEXT,
                     fontweight="bold", pad=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(BORDER)
        ax.tick_params(colors=TEXT2, labelsize=8)
        ax.set_xlabel("x", color=TEXT2, fontsize=10)
        ax.set_ylabel("f(x)", color=TEXT2, fontsize=10)
        ax.grid(True, alpha=0.35, color=BORDER, ls="--")
        ax.axhline(0, color=BORDER, lw=1)
        ax.axvline(0, color=BORDER, lw=1)

    def _plot_2d(self, f_sym, f_num, a, b):
        COLS   = TAG_COLORS
        fa, fb = float(a), float(b)
        span   = fb - fa

        # Intervalo amplo para mostrar a função inteira
        x_min  = fa - span * 1.5
        x_max  = fb + span * 1.5
        xv_full = np.linspace(x_min, x_max, 1600)
        xv_int  = np.linspace(fa, fb, 800)   # só o intervalo [a,b]

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE2)

        for i, (fs, fn) in enumerate(zip(f_sym, f_num)):
            cor = COLS[i % len(COLS)]

            # Curva completa — mais fina e translúcida fora do intervalo
            ax.plot(xv_full, fn(xv_full),
                    lw=1.2, color=cor, alpha=0.30, zorder=2)

            # Curva dentro do intervalo — grossa e sólida
            ax.plot(xv_int, fn(xv_int),
                    label=f"f{i+1}(x) = {fs}",
                    lw=2.4, color=cor, alpha=1.0, zorder=3)

        # Sombreamento da área entre curvas — só em [a, b]
        if len(f_num) >= 2:
            y1, y2 = f_num[0](xv_int), f_num[1](xv_int)
            ax.fill_between(xv_int, y1, y2, interpolate=True,
                            color=ACCENT, alpha=0.12,
                            label="Área entre curvas")
            for xi in encontrar_intersecoes(f_sym[0], f_sym[1], a, b):
                yi = f_num[0](xi)
                ax.plot(xi, yi, "o", color=ACCENT, ms=7,
                        markerfacecolor=SURFACE,
                        markeredgewidth=2, zorder=5)
                ax.annotate(f"  {xi:.2f}", (xi, yi),
                            color=TEXT2, fontsize=8)

        # Linhas verticais marcando os limites [a, b]
        for lim, lbl in [(fa, f"a = {fa}"), (fb, f"b = {fb}")]:
            ax.axvline(lim, color=ACCENT, lw=1.2,
                       ls="--", alpha=0.55, zorder=2)
            ax.text(lim, ax.get_ylim()[1] if ax.get_ylim()[1] != 1.0 else 0,
                    f"  {lbl}", color=ACCENT, fontsize=8,
                    va="bottom", ha="left")

        self._style_ax(ax, "Funções — visão completa  (área sombreada em [a, b])")
        ax.legend(fontsize=9, facecolor=SURFACE,
                  edgecolor=BORDER, labelcolor=TEXT2,
                  framealpha=1)

        # Zoom inicial mostra a função inteira
        # (o usuário pode dar zoom manual com a toolbar)
        ax.set_xlim(x_min, x_max)
        fig.tight_layout()
        return fig

    def _style_ax3d(self, ax, titulo):
        ax.set_title(titulo, fontsize=10, color=TEXT,
                     fontweight="bold", pad=10)
        for fn, lbl in [(ax.set_xlabel,"X"),
                        (ax.set_ylabel,"Y"),
                        (ax.set_zlabel,"Z")]:
            fn(lbl, color=TEXT2, labelpad=6, fontsize=9)
        ax.tick_params(colors=TEXT2, labelsize=7)
        for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
            pane.fill = False
            pane.set_edgecolor(BORDER)
        ax.grid(True, alpha=0.25)

    def _plot_3d_discos(self, f_num, a, b, f2=None):
        n, nt = 260, 90
        xv    = np.linspace(float(a), float(b), n)
        theta = np.linspace(0, 2*np.pi, nt)
        X, T  = np.meshgrid(xv, theta)
        re = np.abs(f_num[0](xv))
        ri = np.abs(f2(xv)) if f2 else np.zeros_like(re)
        RE = np.tile(re, (nt, 1))
        RI = np.tile(ri, (nt, 1))

        fig = plt.figure(figsize=(6, 4.5))
        fig.patch.set_facecolor(SURFACE)
        ax  = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(SURFACE2)

        ax.plot_surface(X, RE*np.cos(T), RE*np.sin(T),
                        color=ACCENT, alpha=0.45, lw=0)
        if f2:
            ax.plot_surface(X, RI*np.cos(T), RI*np.sin(T),
                            color="#D93025", alpha=0.30, lw=0)
        for xi_i, xi_v in [(0, float(a)), (-1, float(b))]:
            tc = np.linspace(0, 2*np.pi, nt)
            rc = np.linspace(ri[xi_i], re[xi_i], 28)
            Tc, Rc = np.meshgrid(tc, rc)
            ax.plot_surface(np.full_like(Tc, xi_v),
                            Rc*np.cos(Tc), Rc*np.sin(Tc),
                            color=ACCENT, alpha=0.18, lw=0)

        self._style_ax3d(ax, "Sólido de Revolução — Eixo X")
        fig.tight_layout()
        return fig

    def _plot_3d_cascas(self, f_num, a, b, f2=None):
        n, nt = 260, 90
        xv    = np.linspace(float(a), float(b), n)
        theta = np.linspace(0, 2*np.pi, nt)
        span  = float(b) - float(a)

        fig = plt.figure(figsize=(6, 4.5))
        fig.patch.set_facecolor(SURFACE)
        ax  = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(SURFACE2)

        for idx in np.linspace(0, n-1, 55, dtype=int):
            xi  = xv[idx]
            h1  = f_num[0](xi)
            h2  = f2(xi) if f2 else 0.0
            Tc, Zc = np.meshgrid(theta, [min(h1,h2), max(h1,h2)])
            alpha  = max(0.07, 0.30*(xi-float(a))/span + 0.07)
            ax.plot_surface(xi*np.cos(Tc), xi*np.sin(Tc), Zc,
                            color=ACCENT, alpha=alpha,
                            lw=0, antialiased=False)

        self._style_ax3d(ax, "Sólido de Revolução — Eixo Y")
        fig.tight_layout()
        return fig

    def _atualizar_grafico(self):
        if not self._ultimo_calculo:
            return
        d  = self._ultimo_calculo
        op = self.var_grafico.get()
        f2 = d["f_num"][1] if len(d["f_num"]) >= 2 else None

        if op == "2D":
            fig = self._plot_2d(d["f_sym"], d["f_num"], d["a"], d["b"])
        elif op == "3D — Discos":
            fig = self._plot_3d_discos(d["f_num"], d["a"], d["b"], f2)
        else:
            fig = self._plot_3d_cascas(d["f_num"], d["a"], d["b"], f2)

        self._embed(fig)
        self._mudar_aba("Gráfico")

    # ════════════════════════════════════════════════════════════════
    # CALCULAR
    # ════════════════════════════════════════════════════════════════

    def calcular(self):
        try:
            fs_str = [e.get().strip() for e in self.funcoes_entries]
            if not fs_str or all(s == "" for s in fs_str):
                raise ValueError("Crie e preencha as funções.")

            a_s = self.entry_a.get().strip()
            b_s = self.entry_b.get().strip()
            if not a_s or not b_s:
                raise ValueError("Preencha os limites de integração.")

            a, b = float(a_s), float(b_s)
            if a >= b:
                raise ValueError("'a' deve ser menor que 'b'.")

            f_sym, f_num = converter_funcoes(fs_str)

            self._ultimo_calculo = {
                "f_sym": f_sym, "f_num": f_num, "a": a, "b": b
            }

            self._limpar_resultados()

            # ── Integrais ─────────────────────────────────────────
            for i, fs in enumerate(f_sym):
                intg = calcular_integral(fs, a, b)
                self._add_card(
                    f"Integral de f{i+1}(x)",
                    [("Função",    str(fs)),
                     ("∫ f dx",    str(intg)),
                     ("Intervalo", f"[ {a},  {b} ]")],
                    cor=TAG_COLORS[i % len(TAG_COLORS)]
                )

            # ── Área ──────────────────────────────────────────────
            if len(f_sym) >= 2:
                ints = encontrar_intersecoes(f_sym[0], f_sym[1], a, b)
                area = calcular_area_entre_curvas(f_sym[0], f_sym[1], a, b)
                self._add_card(
                    "Área entre f1 e f2",
                    [("Interseções", ", ".join(f"{xi:.4f}" for xi in ints)
                                     or "nenhuma no intervalo"),
                     ("Área exata",  str(area))],
                    cor=TEAL
                )

            # ── Volume Discos ─────────────────────────────────────
            if self.var_discos.get():
                f2s = f_sym[1] if len(f_sym) >= 2 else None
                vol = calcular_volume_discos(f_sym[0], a, b, f2s)
                self._add_card(
                    "Volume — Discos (eixo X)",
                    [("Método",       "arruelas f1²−f2²" if f2s else "discos f1²"),
                     ("Volume exato", str(vol))],
                    cor=ACCENT
                )

            # ── Volume Cascas ─────────────────────────────────────
            if self.var_cascas.get():
                f2s = f_sym[1] if len(f_sym) >= 2 else None
                vol = calcular_volume_cascas(f_sym[0], a, b, f2s)
                self._add_card(
                    "Volume — Cascas (eixo Y)",
                    [("Método",       "cascas f1−f2" if f2s else "cascas f1"),
                     ("Volume exato", str(vol))],
                    cor=GREEN
                )

            # ── Gráfico 2D ────────────────────────────────────────
            self.var_grafico.set("2D")
            self._embed(self._plot_2d(f_sym, f_num, a, b))
            self._mudar_aba("Gráfico")

        except Exception as e:
            messagebox.showerror("Erro", str(e))


app = App()
app.mainloop()