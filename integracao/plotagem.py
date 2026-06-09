import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from integracao.calculos import encontrar_intersecoes


# ══════════════════════════════════════════
# GRÁFICO 2D — FUNÇÕES E ÁREA
# ══════════════════════════════════════════

def plotar_funcoes(funcoes_sympy, funcoes_numpy, a, b, n=1000):

    # Define o intervalo do gráfico de 'a' até 'b' dividido em 1000 pontos
    # e inicializa a janela com um tamanho padrão de visualização (10x6)
    x_vals = np.linspace(float(a), float(b), n)
    plt.figure(figsize=(10, 6))

    cores = ['#4F7EFF', '#F87171', '#34D399', '#FBBF24', '#A78BFA']

    # Este laço passa desenhando cada função na tela, calculando os valores 
    # de Y para cada ponto X e aplicando uma cor diferente para cada curva
    for i, (f_sym, f_num) in enumerate(zip(funcoes_sympy, funcoes_numpy)):
        y_vals = f_num(x_vals)
        plt.plot(x_vals, y_vals,
                 label=f'f{i+1}(x) = {f_sym}',
                 linewidth=2, color=cores[i % len(cores)])

    # Se houver duas ou mais funções, identifica o teto (y1) e o piso (y2) 
    # para pintar a área presa entre as curvas e destacar seus cruzamentos
    if len(funcoes_numpy) >= 2:
        y1 = funcoes_numpy[0](x_vals)
        y2 = funcoes_numpy[1](x_vals)

        # fill_between faz o preenchimento translúcido da área de integração
        plt.fill_between(x_vals, y1, y2,
                         interpolate=True, color='#4F7EFF',
                         alpha=0.15, label='Área entre curvas')

        # Procura e marca com bolinhas brancas os pontos exatos de interseção
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
    
    """
    # Mapeia o espaço 3D: 'x_vals' caminha em linha reta (Eixo X) e 'theta'
    # configura um giro redondo completo de 360 graus (de 0 até 2*pi)
    x_vals  = np.linspace(float(a), float(b), n)
    theta   = np.linspace(0, 2 * np.pi, n_theta)
    X, T    = np.meshgrid(x_vals, theta)

    # O raio de fora é moldado pela função principal. Se houver uma segunda função,
    # ela cria um raio interno menor, gerando o efeito de um sólido oco (uma arruela)
    r_ext = np.abs(funcoes_numpy[0](x_vals))

    if f2_numpy is not None:
        r_int = np.abs(f2_numpy(x_vals))
    else:
        r_int = np.zeros_like(r_ext)

    R_ext = np.tile(r_ext, (n_theta, 1))
    R_int = np.tile(r_int, (n_theta, 1))

    # Cria o cenário tridimensional e aplica o fundo escuro do projeto
    fig = plt.figure(figsize=(11, 7))
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0D0F14')
    fig.patch.set_facecolor('#0D0F14')

    # Transforma as funções em superfícies redondas usando as fórmulas de círculo (Seno e Cosseno).
    # O código desenha a casca exterior (azul) e a parede do buraco interno (vermelha, se houver)
    Y_ext = R_ext * np.cos(T)
    Z_ext = R_ext * np.sin(T)
    ax.plot_surface(X, Y_ext, Z_ext,
                    color='#4F7EFF', alpha=0.55, linewidth=0,
                    antialiased=True)

    if f2_numpy is not None:
        Y_int = R_int * np.cos(T)
        Z_int = R_int * np.sin(T)
        ax.plot_surface(X, Y_int, Z_int,
                        color='#F87171', alpha=0.40, linewidth=0,
                        antialiased=True)

    # Cria "tampas" circulares nas pontas do intervalo (em x=a e x=b).
    # Evita que o sólido pareça um cano aberto, dando o visual de um objeto maciço
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
    # Prepara o intervalo de alcance e o giro completo de 360 graus para moldar os cilindros
    x_vals = np.linspace(float(a), float(b), n)
    theta  = np.linspace(0, 2 * np.pi, n_theta)

    fig = plt.figure(figsize=(11, 7))
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0D0F14')
    fig.patch.set_facecolor('#0D0F14')

    # Seleciona apenas 60 posições espaçadas para desenhar os cilindros.
    # Criar esse espaço vazio entre eles servem para conseguir 
    # enxergar as "camadas" ou "cascas" individuais que constroem o volume total
    indices = np.linspace(0, n - 1, 60, dtype=int)

    for idx in indices:
        xi   = x_vals[idx]
        h1   = funcoes_numpy[0](xi)
        h2   = f2_numpy(xi) if f2_numpy is not None else 0.0
        h_lo = min(h1, h2)
        h_hi = max(h1, h2)

        # Monta os tubos verticais: a posição X vira o raio do cilindro, o Seno e Cosseno
        # fazem o contorno redondo (efeito carrossel) e o Z define a altura (do piso ao teto)
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
    # Formata o visual do gráfico 2D: ativa o fundo escuro, define os títulos, 
    # as cores cinzas dos eixos, a grade sutil e desenha as linhas centrais (x=0 e y=0)
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
    # Formata o visual do espaço 3D: dá nome aos eixos X, Y e Z, altera a cor dos números 
    # e desliga o preenchimento opaco das paredes do cubo para dar um efeito transparente limpo
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