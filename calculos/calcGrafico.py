import json
import time

# Regras de Risco para a cultura de Soja (baseado no seu calcGrafico.py)
PRAGAS_SOJA = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}

def calcular_risco(dados: dict) -> dict:
    """
    Calcula o nível de risco para cada praga com base nos dados dos sensores.

    Args:
        dados: Dicionário contendo temperatura, umidade_ar, umidade_solo e luminosidade.
    
    Retorna:
        Dicionário com o risco percentual para cada praga.
    """
    riscos = {}
    
    # Certifica-se de que os dados são floats/ints
    try:
        dados_tratados = {k: float(v) for k, v in dados.items() if k != 'timestamp_leitura'}
    except (ValueError, TypeError):
        # Falha na conversão
        return {"error": "Dados de sensor inválidos para cálculo"}

    for nome, cond in PRAGAS_SOJA.items():
        pontos = 0
        
        # 1. Checagem de Temperatura
        if cond["temp"][0] <= dados_tratados["temperatura"] <= cond["temp"][1]: pontos += 1
        
        # 2. Checagem de Umidade do Ar
        if cond["umidade"][0] <= dados_tratados["umidade_ar"] <= cond["umidade"][1]: pontos += 1
        
        # 3. Checagem de Umidade do Solo (ADC)
        if cond["solo"][0] <= dados_tratados["umidade_solo"] <= cond["solo"][1]: pontos += 1
        
        # 4. Checagem de Luminosidade (ADC)
        if cond["luz"][0] <= dados_tratados["luminosidade"] <= cond["luz"][1]: pontos += 1
        
        # Risco é a média de pontos de 4 (ex: 3/4 = 75%)
        riscos[nome] = round((pontos / 4) * 100, 1) # Arredonda para 1 casa decimal
        
    return riscos

def determinar_nivel_geral(riscos: dict) -> str:
    """Determina o nível de risco geral com base no risco máximo."""
    if "error" in riscos:
        return "Indisponível"

    max_risk = max(riscos.values())
    
    if max_risk >= 75:
        return "ALTO"
    elif max_risk >= 40:
        return "MODERADO"
    else:
        return "BAIXO"

def formatar_resultado_cache(dados: dict, riscos: dict) -> dict:
    """Formata o resultado para salvar no Redis."""
    nivel_geral = determinar_nivel_geral(riscos)
    
    resultado = {
        "timestamp_leitura": dados.get("timestamp_leitura", time.time()),
        "nivel_geral": nivel_geral,
        "riscos_detalhados": riscos,
        "dados_brutos": {
            "temperatura": dados.get("temperatura"),
            "umidade_ar": dados.get("umidade_ar"),
            "umidade_solo": dados.get("umidade_solo"),
            "luminosidade": dados.get("luminosidade"),
        }
    }
    return resultado

if __name__ == '__main__':
    # Exemplo de uso para teste
    dados_exemplo = {
        "temperatura": 28.5, "umidade_ar": 75.0, 
        "umidade_solo": 500, "luminosidade": 300
    }
    riscos_calculados = calcular_risco(dados_exemplo)
    
    print("Dados Brutos:", dados_exemplo)
    print("Riscos Calculados:", riscos_calculados)
    print("Nível Geral:", determinar_nivel_geral(riscos_calculados))