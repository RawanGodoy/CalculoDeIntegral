import sympy as sp
import numpy as np

x = sp.Symbol('x')


# ══════════════════════════════════════════
# INTEGRAL
# ══════════════════════════════════════════

def calcular_integral(f_sym, a, b):
    return sp.integrate(f_sym, (x, a, b))


# ══════════════════════════════════════════
# INTERSEÇÕES
# ══════════════════════════════════════════

def encontrar_intersecoes(f1_sym, f2_sym, a, b, n=1000):
    """
    Detecta interseções por mudança de sinal e refina com sp.nsolve.
    """
    f_diff = sp.lambdify(x, f1_sym - f2_sym, 'numpy')
    x_vals = np.linspace(float(a), float(b), n)
    intersecoes = []

    for i in range(len(x_vals) - 1):
        x1, x2 = x_vals[i], x_vals[i + 1]
        y1, y2 = f_diff(x1), f_diff(x2)

        if y1 * y2 < 0:
            chute = (x1 + x2) / 2
            try:
                raiz = float(sp.nsolve(f1_sym - f2_sym, x, chute))
                if not any(abs(raiz - r) < 1e-5 for r in intersecoes):
                    intersecoes.append(raiz)
            except Exception:
                pass

    return intersecoes


# ══════════════════════════════════════════
# ÁREA ENTRE CURVAS
# ══════════════════════════════════════════

def calcular_area_entre_curvas(f1_sym, f2_sym, a, b):
    """
    Área exata dividindo o intervalo nas interseções e integrando
    (f_superior - f_inferior) em cada subintervalo.
    """
    intersecoes = encontrar_intersecoes(f1_sym, f2_sym, a, b)
    pontos = sorted(set([float(a)] + intersecoes + [float(b)]))

    f1_num = sp.lambdify(x, f1_sym, 'numpy')
    f2_num = sp.lambdify(x, f2_sym, 'numpy')

    area_total = sp.sympify(0)

    for i in range(len(pontos) - 1):
        x_ini, x_fim = pontos[i], pontos[i + 1]
        x_meio = (x_ini + x_fim) / 2

        if f1_num(x_meio) >= f2_num(x_meio):
            integrando = f1_sym - f2_sym
        else:
            integrando = f2_sym - f1_sym

        area_total += sp.integrate(integrando, (x, x_ini, x_fim))

    return area_total


# ══════════════════════════════════════════
# VOLUME — MÉTODO DOS DISCOS (eixo X)
# ══════════════════════════════════════════

def calcular_volume_discos(f_sym, a, b, f2_sym=None):
    """
    Revolução em torno do eixo X.

    Uma função  → V = π ∫ [f(x)]² dx
    Duas funções → V = π ∫ [f1(x)² - f2(x)²] dx  (arruelas)

    Divide o intervalo nas interseções para garantir que
    f_externo² - f_interno² seja sempre positivo.
    """
    if f2_sym is None:
        integrando = sp.pi * f_sym**2
        return sp.integrate(integrando, (x, a, b))

    # Método das arruelas: determina qual é exterior em cada subintervalo
    intersecoes = encontrar_intersecoes(f_sym, f2_sym, a, b)
    pontos = sorted(set([float(a)] + intersecoes + [float(b)]))

    f1_num = sp.lambdify(x, f_sym,  'numpy')
    f2_num = sp.lambdify(x, f2_sym, 'numpy')

    volume_total = sp.sympify(0)

    for i in range(len(pontos) - 1):
        x_ini, x_fim = pontos[i], pontos[i + 1]
        x_meio = (x_ini + x_fim) / 2

        r_ext = f_sym  if abs(f1_num(x_meio)) >= abs(f2_num(x_meio)) else f2_sym
        r_int = f2_sym if abs(f1_num(x_meio)) >= abs(f2_num(x_meio)) else f_sym

        integrando = sp.pi * (r_ext**2 - r_int**2)
        volume_total += sp.integrate(integrando, (x, x_ini, x_fim))

    return volume_total


# ══════════════════════════════════════════
# VOLUME — MÉTODO DAS CASCAS (eixo Y)
# ══════════════════════════════════════════

def calcular_volume_cascas(f_sym, a, b, f2_sym=None):
    """
    Revolução em torno do eixo Y pelo método das cascas cilíndricas.

    Uma função  → V = 2π ∫ x·f(x) dx
    Duas funções → V = 2π ∫ x·|f1(x) - f2(x)| dx
                   (divide o intervalo nas interseções)
    """
    if f2_sym is None:
        integrando = 2 * sp.pi * x * f_sym
        return sp.integrate(integrando, (x, a, b))

    intersecoes = encontrar_intersecoes(f_sym, f2_sym, a, b)
    pontos = sorted(set([float(a)] + intersecoes + [float(b)]))

    f1_num = sp.lambdify(x, f_sym,  'numpy')
    f2_num = sp.lambdify(x, f2_sym, 'numpy')

    volume_total = sp.sympify(0)

    for i in range(len(pontos) - 1):
        x_ini, x_fim = pontos[i], pontos[i + 1]
        x_meio = (x_ini + x_fim) / 2

        if f1_num(x_meio) >= f2_num(x_meio):
            diff = f_sym - f2_sym
        else:
            diff = f2_sym - f_sym

        integrando = 2 * sp.pi * x * diff
        volume_total += sp.integrate(integrando, (x, x_ini, x_fim))

    return volume_total
