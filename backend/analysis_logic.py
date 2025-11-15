# import json

# # Regras de risco de pragas
# PRAGAS_SOJA_REGRAS = {
#     "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
#     "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
#     "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
# }

# def calcular_risco(dados, regras=PRAGAS_SOJA_REGRAS):
#     """
#     Calcula o percentual de risco para cada praga baseado nos dados dos sensores.
#     Retorna: dict {'praga': risco_percentual}
#     """
#     riscos = {}
#     for nome, cond in regras.items():
#         pontos = 0
#         # Temperatura
#         if cond["temp"][0] <= dados.get("temperatura", 0) <= cond["temp"][1]: pontos += 1
#         # Umidade do Ar
#         if cond["umidade"][0] <= dados.get("umidade_ar", 0) <= cond["umidade"][1]: pontos += 1
#         # Umidade do Solo
#         if cond["solo"][0] <= dados.get("umidade_solo", 0) <= cond["solo"][1]: pontos += 1
#         # Luminosidade
#         if cond["luz"][0] <= dados.get("luminosidade", 0) <= cond["luz"][1]: pontos += 1
        
#         # Risco % baseado nas 4 condicoes
#         riscos[nome] = (pontos / 4) * 100 
#     return riscos

# def formatar_resultado_cache(dados_brutos, riscos):
#     """
#     Formata o resultado da análise para ser salvo como JSON no Redis.
#     Também calcula o nível de risco geral (ALTO, MODERADO, BAIXO).
#     """
    
#     # Define o nivel de risco geral
#     if any(r >= 75 for r in riscos.values()):
#         nivel_geral = "ALTO"
#     elif any(r >= 50 for r in riscos.values()):
#         nivel_geral = "MODERADO"
#     else:
#         nivel_geral = "BAIXO"

#     cache_data = {
#         "timestamp": dados_brutos['timestamp'],
#         "dados_brutos": {k: float(v) for k, v in dados_brutos.items() if k != 'timestamp'}, # Garante float para o JSON
#         "riscos_detalhados": riscos,
#         "nivel_geral": nivel_geral
#     }
    
#     return cache_data

# ======================================================
# codigo novo
# ======================================================

import json

# Regras de risco de pragas
PRAGAS_SOJA_REGRAS = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}

# Mapeia as chaves das regras (ex: 'temp') para as chaves dos dados (ex: 'temperatura')
# Isso desacopla a estrutura das regras da estrutura dos dados de entrada.
_SENSOR_RULE_MAP = {
    "temp": "temperatura",
    "umidade": "umidade_ar",
    "solo": "umidade_solo",
    "luz": "luminosidade"
}

def calcular_risco(dados, regras=PRAGAS_SOJA_REGRAS):
    """
    Calcula o percentual de risco para cada praga baseado nos dados dos sensores.
    Retorna: dict {'praga': risco_percentual}
    """
    riscos = {}
    
    # Itera sobre cada praga e suas condições
    for nome_praga, condicoes in regras.items():
        pontos = 0
        total_condicoes = len(condicoes)

        if total_condicoes == 0:
            riscos[nome_praga] = 0.0
            continue
        
        # Itera sobre as regras específicas (temp, umidade, etc.)
        for regra_key, (min_val, max_val) in condicoes.items():
            
            # Encontra a chave do sensor correspondente (ex: 'temp' -> 'temperatura')
            sensor_key = _SENSOR_RULE_MAP.get(regra_key)
            
            # Se a regra não tiver um mapeamento de sensor, pula
            if not sensor_key:
                continue
                
            # Obtém o valor do sensor, usando o default 0 (mesmo comportamento do original)
            valor_sensor = dados.get(sensor_key, 0)
            
            # Verifica se o valor está dentro do intervalo da regra
            if min_val <= valor_sensor <= max_val:
                pontos += 1
        
        # Risco % baseado no total de condicoes (remove o 'magic number' 4)
        riscos[nome_praga] = (pontos / total_condicoes) * 100
        
    return riscos

def formatar_resultado_cache(dados_brutos, riscos):
    """
    Formata o resultado da análise para ser salvo como JSON no Redis.
    Também calcula o nível de risco geral (ALTO, MODERADO, BAIXO).
    """
    
    # Define o nivel de risco geral
    risco_maximo = max(riscos.values(), default=0)
    
    if risco_maximo >= 75:
        nivel_geral = "ALTO"
    elif risco_maximo >= 50:
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