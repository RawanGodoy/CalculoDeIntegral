import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from integracao.calculos import encontrar_intersecoes


# ══════════════════════════════════════════
# GRÁFICO 2D — FUNÇÕES E ÁREA
# ══════════════════════════════════════════

def plotar_funcoes(funcoes_sympy, funcoes_numpy, a, b, n=1000):

    x_vals = np.linspace(float(a), float(b), n)
    plt.figure(figsize=(10, 6))

    cores = ['#4F7EFF', '#F87171', '#34D399', '#FBBF24', '#A78BFA']

    for i, (f_sym, f_num) in enumerate(zip(funcoes_sympy, funcoes_numpy)):
        y_vals = f_num(x_vals)
        plt.plot(x_vals, y_vals,
                 label=f'f{i+1}(x) = {f_sym}',
                 linewidth=2, color=cores[i % len(cores)])

    if len(funcoes_numpy) >= 2:
        y1 = funcoes_numpy[0](x_vals)
        y2 = funcoes_numpy[1](x_vals)

        plt.fill_between(x_vals, y1, y2,
                         interpolate=True, color='#4F7EFF',
                         alpha=0.15, label='Área entre curvas')

        intersecoes = encontrar_intersecoes(
            funcoes_sympy[0], funcoes_sympy[1], a, b)

        for xi in intersecoes:
            yi = funcoes_numpy[0](xi)
            plt.plot(xi, yi, 'wo', markersize=7, zorder=5,
                     markeredgecolor='#4F7EFF', markeredgewidth=1.5)
            plt.annotate(f'  x={xi:.3f}', (xi, yi), fontsize=9, color='white')

    _estilo_2d("Funções e Área Entre Curvas")
    plt.show()


# ══════════════════════════════════════════
# GRÁFICO 3D — SÓLIDO DE REVOLUÇÃO (eixo X)
# ══════════════════════════════════════════

def plotar_volume_discos(funcoes_numpy, a, b, f2_numpy=None, n=400, n_theta=120):
    """
    Plota o sólido de revolução em torno do eixo X.
    Usa surface com malha (x, theta) → (x, r·cos θ, r·sin θ).
    """
    x_vals  = np.linspace(float(a), float(b), n)
    theta   = np.linspace(0, 2 * np.pi, n_theta)
    X, T    = np.meshgrid(x_vals, theta)

    r_ext = np.abs(funcoes_numpy[0](x_vals))

    if f2_numpy is not None:
        r_int = np.abs(f2_numpy(x_vals))
    else:
        r_int = np.zeros_like(r_ext)

    R_ext = np.tile(r_ext, (n_theta, 1))
    R_int = np.tile(r_int, (n_theta, 1))

    fig = plt.figure(figsize=(11, 7))
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0D0F14')
    fig.patch.set_facecolor('#0D0F14')

    # Superfície exterior
    Y_ext = R_ext * np.cos(T)
    Z_ext = R_ext * np.sin(T)
    ax.plot_surface(X, Y_ext, Z_ext,
                    color='#4F7EFF', alpha=0.55, linewidth=0,
                    antialiased=True)

    # Superfície interior (se houver duas funções)
    if f2_numpy is not None:
        Y_int = R_int * np.cos(T)
        Z_int = R_int * np.sin(T)
        ax.plot_surface(X, Y_int, Z_int,
                        color='#F87171', alpha=0.40, linewidth=0,
                        antialiased=True)

    # Tampas nas extremidades
    for xi in [float(a), float(b)]:
        idx   = 0 if xi == float(a) else -1
        re    = r_ext[idx]
        ri    = r_int[idx]
        t_cap = np.linspace(0, 2 * np.pi, n_theta)
        r_cap = np.linspace(ri, re, 30)
        T_c, R_c = np.meshgrid(t_cap, r_cap)
        ax.plot_surface(
            np.full_like(T_c, xi),
            R_c * np.cos(T_c),
            R_c * np.sin(T_c),
            color='#4F7EFF', alpha=0.30, linewidth=0)

    _estilo_3d(ax, "Sólido de Revolução — Eixo X (Discos)")
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════
# GRÁFICO 3D — SÓLIDO DE REVOLUÇÃO (eixo Y)
# ══════════════════════════════════════════

def plotar_volume_cascas(funcoes_numpy, a, b, f2_numpy=None, n=400, n_theta=120):
    """
    Plota o sólido de revolução em torno do eixo Y (cascas cilíndricas).
    Cada x gera um cilindro de raio x e altura f(x).
    """
    x_vals = np.linspace(float(a), float(b), n)
    theta  = np.linspace(0, 2 * np.pi, n_theta)

    fig = plt.figure(figsize=(11, 7))
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0D0F14')
    fig.patch.set_facecolor('#0D0F14')

    # Plotamos uma amostra de cascas para não sobrecarregar
    indices = np.linspace(0, n - 1, 60, dtype=int)

    for idx in indices:
        xi   = x_vals[idx]
        h1   = funcoes_numpy[0](xi)
        h2   = f2_numpy(xi) if f2_numpy is not None else 0.0
        h_lo = min(h1, h2)
        h_hi = max(h1, h2)

        z_vals = np.array([h_lo, h_hi])
        T_c, Z_c = np.meshgrid(theta, z_vals)

        X_c = xi * np.cos(T_c)
        Y_c = xi * np.sin(T_c)

        cor   = '#4F7EFF' if f2_numpy is None or h1 >= h2 else '#F87171'
        alpha = max(0.08, 0.35 * (xi - float(a)) / (float(b) - float(a)) + 0.08)

        ax.plot_surface(X_c, Y_c, Z_c,
                        color=cor, alpha=alpha,
                        linewidth=0, antialiased=False)

    _estilo_3d(ax, "Sólido de Revolução — Eixo Y (Cascas)")
    plt.tight_layout()
    plt.show()


# ══════════════════════════════════════════
# HELPERS DE ESTILO
# ══════════════════════════════════════════

def _estilo_2d(titulo):
    plt.style.use('dark_background')
    plt.title(titulo, fontsize=14, color='white', pad=14)
    plt.xlabel("x", color='#6B7280')
    plt.ylabel("f(x)", color='#6B7280')
    plt.tick_params(colors='#6B7280')
    plt.grid(True, alpha=0.12, color='#252A3A')
    plt.axhline(0, color='#252A3A', linewidth=1)
    plt.axvline(0, color='#252A3A', linewidth=1)
    plt.legend(facecolor='#1A1E2A', edgecolor='#252A3A',
               labelcolor='white', fontsize=10)
    plt.tight_layout()


def _estilo_3d(ax, titulo):
    ax.set_title(titulo, color='white', fontsize=13, pad=14)
    ax.set_xlabel("X", color='#6B7280', labelpad=8)
    ax.set_ylabel("Y", color='#6B7280', labelpad=8)
    ax.set_zlabel("Z", color='#6B7280', labelpad=8)
    ax.tick_params(colors='#6B7280')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#252A3A')
    ax.yaxis.pane.set_edgecolor('#252A3A')
    ax.zaxis.pane.set_edgecolor('#252A3A')
    ax.grid(True, alpha=0.10)