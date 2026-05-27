import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

x = sp.Symbol('x')

# Transformações seguras: permite "2x" ser lido como "2*x", etc.
TRANSFORMACOES = (
    standard_transformations
    + (implicit_multiplication_application,)
)

# Escopo permitido: apenas funções matemáticas conhecidas + a variável x
ESCOPO_SEGURO = {
    'x': x,
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'exp': sp.exp,
    'log': sp.log,
    'sqrt': sp.sqrt,
    'pi': sp.pi,
    'E': sp.E,
    'abs': sp.Abs,
    'Abs': sp.Abs,
}


def converter_funcoes(funcoes_str):
    """
    Converte uma lista de strings em funções SymPy e NumPy.
    Usa parse_expr com escopo restrito para evitar execução de código arbitrário.
    """

    funcoes_sympy = []
    funcoes_numpy = []

    for f_str in funcoes_str:

        f_str = f_str.strip()

        if not f_str:
            raise ValueError("Uma das funções está vazia.")

        try:
            f_sym = parse_expr(
                f_str,
                local_dict=ESCOPO_SEGURO,
                transformations=TRANSFORMACOES
            )
        except Exception:
            raise ValueError(
                f"Não foi possível interpretar a função: '{f_str}'\n"
                "Verifique a sintaxe (ex: x**2, sin(x), 2*x)."
            )

        f_num = sp.lambdify(x, f_sym, 'numpy')

        funcoes_sympy.append(f_sym)
        funcoes_numpy.append(f_num)

    return funcoes_sympy, funcoes_numpy