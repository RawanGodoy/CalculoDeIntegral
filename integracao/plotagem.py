import numpy as np
import matplotlib.pyplot as plt


def plotar_funcoes(
        funcoes_sympy,
        funcoes_numpy,
        a,
        b,
        n=1000):

    x_vals = np.linspace(a, b, n)

    plt.figure(figsize=(10, 6))

    cores = [
        'blue',
        'red',
        'green',
        'purple',
        'orange'
    ]

    # ======================================
    # PLOT DAS FUNÇÕES
    # ======================================

    for i, (f_sym, f_num) in enumerate(
            zip(funcoes_sympy, funcoes_numpy)):

        y_vals = f_num(x_vals)

        plt.plot(
            x_vals,
            y_vals,
            label=f'f(x) = {f_sym}',
            linewidth=2,
            color=cores[i % len(cores)]
        )

    # ======================================
    # ÁREA ENTRE CURVAS
    # ======================================

    if len(funcoes_numpy) >= 2:

        y1 = funcoes_numpy[0](x_vals)
        y2 = funcoes_numpy[1](x_vals)

        # Pintar SOMENTE a interseção
        plt.fill_between(
            x_vals,
            y1,
            y2,
            where=(y1 != y2),
            interpolate=True,
            color='gray',
            alpha=0.4,
            label='Área entre curvas'
        )

    # ======================================
    # EIXOS
    # ======================================

    plt.axhline(
        0,
        color='black',
        linewidth=1
    )

    plt.axvline(
        0,
        color='black',
        linewidth=1
    )

    # ======================================
    # ESTILO
    # ======================================

    plt.title(
        "Área Entre Curvas",
        fontsize=16
    )

    plt.xlabel("x")
    plt.ylabel("f(x)")

    plt.grid(True, alpha=0.3)

    plt.legend()

    plt.show()