import random
import time
import matplotlib.pyplot as plt

def coletar_dados():
    return {
        "temperatura": random.uniform(20, 35),
        "umidade_ar": random.uniform(40, 90),
        "umidade_solo": random.randint(0, 1023),
        "luminosidade": random.randint(0, 1023)
    }

pragasSoja = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}

def calcular_risco(dados, regras):
    riscos = {}
    for nome, cond in regras.items():
        pontos = 0
        if cond["temp"][0] <= dados["temperatura"] <= cond["temp"][1]: pontos += 1
        if cond["umidade"][0] <= dados["umidade_ar"] <= cond["umidade"][1]: pontos += 1
        if cond["solo"][0] <= dados["umidade_solo"] <= cond["solo"][1]: pontos += 1
        if cond["luz"][0] <= dados["luminosidade"] <= cond["luz"][1]: pontos += 1
        riscos[nome] = (pontos / 4) * 100 
    return riscos

plt.style.use('default')

fig, ax = plt.subplots(figsize=(8, 4))
plt.ion()  

while True:
    dados = coletar_dados()
    riscos = calcular_risco(dados, pragasSoja)

    ax.clear()

    pragas = list(riscos.keys())
    valores = list(riscos.values())
    cores = ['#79C99E', '#4E937A', '#2C666E']
    
    barras = ax.barh(pragas, valores, color=cores, edgecolor='none', height=0.5)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Risco (%)", fontsize=10, labelpad=8)
    ax.set_title("Monitoramento de Risco — Soja", fontsize=14, fontweight='bold', pad=10)
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    ax.grid(True, axis='x', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    for barra, valor in zip(barras, valores):
        ax.text(valor + 1, barra.get_y() + barra.get_height()/2,
                f"{valor:.0f}%", va='center', ha='left', fontsize=9, color='#333333')

    plt.tight_layout()
    plt.pause(0.1)

    print(f"Dados coletados: {dados}")
    time.sleep(10)

