import time

# Regras de Risco para a cultura de Soja (baseado no seu calcGrafico.py)
PRAGAS_SOJA_REGRAS = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}

# Mapeia as chaves das regras para as chaves dos dados de entrada
# Isso desacopla a lógica das regras dos nomes dos campos nos dados
_SENSOR_RULE_MAP = {
    "temp": "temperatura",
    "umidade": "umidade_ar",
    "solo": "umidade_solo",
    "luz": "luminosidade"
}

# Constantes para os níveis de risco
_RISK_HIGH_THRESHOLD = 75
_RISK_MODERATE_THRESHOLD = 40


def calcular_risco(dados: dict) -> dict:
    """
    Calcula o nível de risco para cada praga com base nos dados dos sensores.
    Mantém o comportamento de falha rápida se os dados não forem numéricos.

    Args:
        dados: Dicionário contendo temperatura, umidade_ar, umidade_solo e luminosidade.
    
    Retorna:
        Dicionário com o risco percentual para cada praga, 
        ou {"error": ...} se os dados forem inválidos.
    """
    
    # Pré-validação: Tenta converter todos os valores necessários para float.
    # Isso mantém o comportamento original de falhar se *qualquer* dado for
    # inválido (ex: "abc") ou ausente (None).
    try:
        dados_limpos = {
            sensor_key: float(dados.get(sensor_key)) 
            for sensor_key in _SENSOR_RULE_MAP.values()
        }
    except (ValueError, TypeError, AttributeError):
        # Falha na conversão (ex: float(None) ou float("abc"))
        return {"error": "Dados de sensor inválidos para cálculo"}

    riscos = {}
    
    for nome, cond in PRAGAS_SOJA_REGRAS.items():
        pontos = 0
        total_regras = len(cond)
        
        if total_regras == 0:
            riscos[nome] = 0.0
            continue
            
        # Itera sobre as regras (ex: "temp", "umidade")
        for regra_key, (min_val, max_val) in cond.items():
            
            # Encontra a chave de dados correspondente (ex: "temperatura")
            sensor_key = _SENSOR_RULE_MAP.get(regra_key)
            
            # Se a regra não tiver mapeamento, pula
            if not sensor_key:
                continue
                
            # Obtém o valor já validado
            valor_sensor = dados_limpos[sensor_key]
            
            if min_val <= valor_sensor <= max_val:
                pontos += 1
        
        # Risco é a média de pontos (ex: 3/4 = 75%)
        riscos[nome] = round((pontos / total_regras) * 100, 1)
        
    return riscos

def determinar_nivel_geral(riscos: dict) -> str:
    """Determina o nível de risco geral com base no risco máximo."""
    if "error" in riscos:
        return "Indisponível"

    # Usa default=0 para evitar erro se 'riscos' estiver vazio
    max_risk = max(riscos.values(), default=0)
    
    if max_risk >= _RISK_HIGH_THRESHOLD:
        return "ALTO"
    elif max_risk >= _RISK_MODERATE_THRESHOLD:
        return "MODERADO"
    else:
        return "BAIXO"

def formatar_resultado_cache(dados: dict, riscos: dict) -> dict:
    """Formata o resultado para salvar no Redis."""
    nivel_geral = determinar_nivel_geral(riscos)
    
    # Usa list comprehension para extrair dados brutos de forma limpa
    dados_brutos = {
        key: dados.get(key) for key in _SENSOR_RULE_MAP.values()
    }
    
    resultado = {
        "timestamp_leitura": dados.get("timestamp_leitura", time.time()),
        "nivel_geral": nivel_geral,
        "riscos_detalhados": riscos,
        "dados_brutos": dados_brutos
    }
    return resultado

if __name__ == '__main__':
    # Exemplo de uso para teste
    dados_exemplo = {
        "temperatura": 28.5, "umidade_ar": 75.0, 
        "umidade_solo": 500, "luminosidade": 300,
        "timestamp_leitura": 123456789
    }
    riscos_calculados = calcular_risco(dados_exemplo)
    
    print("Dados Brutos:", dados_exemplo)
    print("Riscos Calculados:", riscos_calculados)
    
    resultado_formatado = formatar_resultado_cache(dados_exemplo, riscos_calculados)
    print("\nResultado Formatado:")
    print(resultado_formatado)
    
    # Teste de falha
    dados_falha = {"temperatura": "abc"}
    riscos_falha = calcular_risco(dados_falha)
    print("\nTeste de Falha:", riscos_falha)
    print("Nível Geral (Falha):", determinar_nivel_geral(riscos_falha))