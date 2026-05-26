import sympy as sp

x = sp.Symbol('x')


def converter_funcoes(funcoes_str):

    funcoes_sympy = [
        sp.sympify(f)
        for f in funcoes_str
    ]

    funcoes_numpy = [
        sp.lambdify(x, f, 'numpy')
        for f in funcoes_sympy
    ]

    return funcoes_sympy, funcoes_numpy