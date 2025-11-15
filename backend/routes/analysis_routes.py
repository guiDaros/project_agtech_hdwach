import json
from flask import Blueprint, jsonify
from extensions import redis_client
from config import REDIS_LATEST_DATA_KEY
analysis_bp = Blueprint('analysis', __name__)

# (Regras e KEY_MAP não mudam)
PRAGAS_SOJA_REGRAS = {
    "Lagarta-da-soja": {"temp": (22, 34), "umidade": (60, 90), "solo": (300, 700), "luz": (0, 600)},
    "Percevejo-marrom": {"temp": (20, 32), "umidade": (30, 70), "solo": (600, 900), "luz": (0, 500)},
    "Mosca-branca": {"temp": (24, 34), "umidade": (30, 60), "solo": (600, 950), "luz": (0, 400)}
}
KEY_MAP = {
    "temp": "temperatura",
    "umidade": "umidade_ar",
    "solo": "umidade_solo",
    "luz": "luminosidade"
}


# ==========================================================
# === A NOVA LÓGICA DE CÁLCULO (GRADUAL) ===
# ==========================================================
def _calculate_pest_probabilities(dados_brutos):
    """
    Calcula uma probabilidade percentual (0-100) para cada praga,
    baseado em quão "ideal" o valor atual está dentro da faixa de risco.
    """
    probabilidades = {}
    if not dados_brutos:
        return {}

    for praga, regras in PRAGAS_SOJA_REGRAS.items():
        factor_scores = [] # Lista para guardar os scores (0.0 a 1.0) de cada fator

        for regra_key, (min_val, max_val) in regras.items():
            dado_key = KEY_MAP.get(regra_key)
            
            if not dado_key or dado_key not in dados_brutos:
                print(f"Aviso: Chave '{dado_key}' (para '{regra_key}') não encontrada.")
                factor_scores.append(0.0) # Se o sensor falhar, 0% de risco para esse fator
                continue 

            valor_atual = dados_brutos[dado_key]

            # --- Lógica de Risco Gradual ---
            factor_score = 0.0 # Risco é 0 se estiver FORA da faixa
            if min_val <= valor_atual <= max_val:
                # O valor está na faixa de risco.
                # Calculamos o quão perto do "ponto ideal" (o centro) ele está.
                center = (min_val + max_val) / 2
                max_distance = (max_val - min_val) / 2
                
                # Evita divisão por zero se min_val == max_val
                if max_distance == 0:
                    # Se min == max e o valor bateu, é 100%
                    factor_score = 1.0 if valor_atual == center else 0.0
                else:
                    current_distance = abs(valor_atual - center)
                    # (1.0 - (distancia_atual / distancia_maxima))
                    # Perto do centro -> (1.0 - ~0.0) -> ~1.0 (Risco Alto)
                    # Perto da borda -> (1.0 - ~1.0) -> ~0.0 (Risco Baixo)
                    factor_score = 1.0 - (current_distance / max_distance)

            factor_scores.append(factor_score)
        
        # A probabilidade final é a MÉDIA dos scores de todos os fatores
        if factor_scores:
            probabilidade_total = (sum(factor_scores) / len(factor_scores)) * 100
            probabilidades[praga] = round(probabilidade_total, 1) # Arredonda
        else:
            probabilidades[praga] = 0

    return probabilidades
# ==========================================================
# === FIM DA NOVA LÓGICA ===
# ==========================================================


@analysis_bp.route('/risk', methods=['GET'])
def get_pest_risk_analysis():
    # (O resto desta função está correto e não muda)
    
    if not redis_client:
        return jsonify({'error': 'Redis service unavailable'}), 503

    try:
        data_json = redis_client.get(REDIS_LATEST_DATA_KEY)
        if not data_json:
            return jsonify({'success': False, 'message': 'Nenhum dado no cache.'}), 404
        
        data = json.loads(data_json)
        dados_brutos = data.get('dados_brutos') 

        if not dados_brutos:
            return jsonify({'success': False, 'message': 'Cache em formato inesperado (sem "dados_brutos").'}), 404

        # Esta função agora faz o cálculo "real"
        probabilidades = _calculate_pest_probabilities(dados_brutos)

        risk_list = []
        for praga, risco in probabilidades.items():
            status = "baixo"
            if risco > 70:
                status = "alto"
            elif risco > 40:
                status = "médio"
            
            risk_list.append({
                "praga": praga,
                "risco": risco,
                "status": status
            })

        return jsonify({
            'success': True,
            'risks': risk_list 
        }), 200

    except Exception as e:
        print(f"Erro em /analysis/risk: {e}")
        return jsonify({'error': 'Erro interno ao calcular riscos'}), 500