import sympy as sp
import numpy as np

x = sp.Symbol('x')


def calcular_integral(f_sym, a, b):

    return sp.integrate(
        f_sym,
        (x, a, b)
    )


def calcular_area_entre_curvas(
        f1_sym,
        f2_sym,
        a,
        b,
        n=1000):

    f1 = sp.lambdify(x, f1_sym, 'numpy')
    f2 = sp.lambdify(x, f2_sym, 'numpy')

    x_vals = np.linspace(a, b, n)

    y1 = f1(x_vals)
    y2 = f2(x_vals)

    area = np.trapezoid(
    np.abs(y1 - y2),
    x_vals
)

    return area


def encontrar_intersecoes(
        f1_sym,
        f2_sym,
        a,
        b,
        n=1000):

    f = sp.lambdify(
        x,
        f1_sym - f2_sym,
        'numpy'
    )

    x_vals = np.linspace(a, b, n)

    intersecoes = []

    for i in range(len(x_vals) - 1):

        x1 = x_vals[i]
        x2 = x_vals[i + 1]

        y1 = f(x1)
        y2 = f(x2)

        # Mudança de sinal
        if y1 * y2 < 0:

            try:

                raiz = sp.nsolve(
                    f1_sym - f2_sym,
                    x,
                    (x1, x2)
                )

                raiz = float(raiz)

                # Evita duplicatas
                if not any(
                    abs(raiz - r) < 1e-5
                    for r in intersecoes
                ):

                    intersecoes.append(raiz)

            except:
                pass

    return intersecoes