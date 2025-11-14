import json

# Regras de risco de pragas (movidas do seu calcGrafico.py)
PRAGAS_SOJA_REGRAS = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}

def calcular_risco(dados, regras=PRAGAS_SOJA_REGRAS):
    """
    Calcula o percentual de risco para cada praga baseado nos dados dos sensores.
    Retorna: dict {'praga': risco_percentual}
    """
    riscos = {}
    for nome, cond in regras.items():
        pontos = 0
        # Checa a Temperatura
        if cond["temp"][0] <= dados.get("temperatura", 0) <= cond["temp"][1]: pontos += 1
        # Checa a Umidade do Ar
        if cond["umidade"][0] <= dados.get("umidade_ar", 0) <= cond["umidade"][1]: pontos += 1
        # Checa a Umidade do Solo
        if cond["solo"][0] <= dados.get("umidade_solo", 0) <= cond["solo"][1]: pontos += 1
        # Checa a Luminosidade
        if cond["luz"][0] <= dados.get("luminosidade", 0) <= cond["luz"][1]: pontos += 1
        
        # O risco é a porcentagem de condições atendidas (4 é o máximo)
        riscos[nome] = (pontos / 4) * 100 
    return riscos

def formatar_resultado_cache(dados_brutos, riscos):
    """
    Formata o resultado da análise para ser salvo como JSON no Redis.
    Também calcula o nível de risco geral (ALTO, MODERADO, BAIXO).
    """
    
    # Define o nível de risco geral
    if any(r >= 75 for r in riscos.values()):
        nivel_geral = "ALTO"
    elif any(r >= 50 for r in riscos.values()):
        nivel_geral = "MODERADO"
    else:
        nivel_geral = "BAIXO"

    cache_data = {
        "timestamp": dados_brutos['timestamp'],
        "dados_brutos": {k: float(v) for k, v in dados_brutos.items() if k != 'timestamp'}, # Garante float para o JSON
        "riscos_detalhados": riscos,
        "nivel_geral": nivel_geral
    }
    
    return json.dumps(cache_data)