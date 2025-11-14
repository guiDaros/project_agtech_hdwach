from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime
import time

# Importa a lógica de análise centralizada, removendo duplicação
from analysis_logic import calcular_risco, PRAGAS_SOJA_REGRAS

# Blueprint para rotas do frontend (Kaiki)
frontend_bp = Blueprint('frontend', __name__)

# --- Constantes de Configuração ---

_DEFAULT_HOURS = 24
_MAX_HOURS = 168 # 7 dias
_SECONDS_PER_HOUR = 3600
_READINGS_PER_HOUR_ESTIMATE = 6 # Aprox. 1 leitura a cada 10 min
_MAX_HISTORICAL_LIMIT_SENSORS = 1000
_MAX_HISTORICAL_LIMIT_RISK = 500

# Limites para status de risco
_RISK_MEDIUM_THRESHOLD = 40
_RISK_HIGH_THRESHOLD = 70

# Regras de risco para Milho (mantidas aqui, pois não estão na 'analysis_logic' central)
PRAGAS_MILHO = {
    "Lagarta-do-cartucho": {
        "temp": (25, 35),
        "umidade": (60, 85),
        "solo": (400, 800),
        "luz": (0, 500)
    },
    "Cigarrinha": {
        "temp": (22, 32),
        "umidade": (50, 80),
        "solo": (500, 900),
        "luz": (0, 600)
    },
    "Percevejo": {
        "temp": (20, 30),
        "umidade": (40, 70),
        "solo": (600, 950),
        "luz": (0, 450)
    }
}


# --- Funções Helper ---

def _get_latest_reading_or_404():
    """Busca a última leitura do DB; retorna (None, response) em caso de erro 404."""
    readings = db.get_recent_readings(limit=1)
    if not readings:
        error_response = jsonify({
            'success': False,
            'error': 'Nenhuma leitura disponível'
        }), 404
        return None, error_response
    return readings[0], None

def _format_sensor_data_kaiki(leitura):
    """Formata uma leitura do DB para o formato camelCase do frontend Kaiki."""
    return {
        'temperatura': round(leitura['temperatura'], 1),
        'umidadeAr': round(leitura['umidade_ar'], 1),
        'umidadeSolo': round(leitura['umidade_solo'], 1),
        'luminosidade': round(leitura['luminosidade'], 1),
        'timestamp': datetime.fromtimestamp(leitura['timestamp']).isoformat() + 'Z'
    }

def determinar_status(risco):
    """Determina status baseado na porcentagem de risco usando constantes."""
    if risco < _RISK_MEDIUM_THRESHOLD:
        return "baixo"
    elif risco < _RISK_HIGH_THRESHOLD:
        return "médio"
    else:
        return "alto"

# --- Rotas /sensors ---

@frontend_bp.route('/sensors/current', methods=['GET'])
def sensor_atual():
    """
    Endpoint compatível com o frontend do Kaiki
    Retorna última leitura dos sensores
    """
    try:
        leitura, error = _get_latest_reading_or_404()
        if error:
            return error
        
        response = _format_sensor_data_kaiki(leitura)
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar dados',
            'details': str(e)
        }), 500


@frontend_bp.route('/sensors/historical', methods=['GET'])
def dados_historicos():
    """
    Endpoint compatível com o frontend do Kaiki
    Retorna histórico de leituras
    """
    try:
        hours = request.args.get('hours', default=_DEFAULT_HOURS, type=int)
        hours = min(hours, _MAX_HOURS) # Trava o limite
        
        start_timestamp = int(time.time()) - (hours * _SECONDS_PER_HOUR)
        end_timestamp = int(time.time())
        
        # Calcula limite de registros baseado na estimativa, travado no teto
        limit = min(hours * _READINGS_PER_HOUR_ESTIMATE, _MAX_HISTORICAL_LIMIT_SENSORS)
        
        readings = db.get_readings_by_timerange(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit
        )
        
        if not readings:
            return jsonify([]), 200
        
        # Converte para formato do frontend usando list comprehension
        historico = [
            {
                'hora': datetime.fromtimestamp(r['timestamp']).strftime('%H:%M'),
                'temperatura': round(r['temperatura'], 1),
                'umidadeAr': round(r['umidade_ar'], 1),
                'umidadeSolo': round(r['umidade_solo'], 1),
                'luminosidade': round(r['luminosidade'], 1)
            }
            for r in readings
        ]
        
        # Ordena por hora (mais antigo primeiro para gráficos)
        historico.reverse()
        
        return jsonify(historico), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar histórico',
            'details': str(e)
        }), 500


# --- Rotas /pests ---

@frontend_bp.route('/pests/risk', methods=['GET'])
def risco_pragas():
    """
    Endpoint de risco de pragas usando lógica centralizada
    """
    try:
        plant = request.args.get('plant', default='soja').lower()
        
        # Seleciona regras: SOJA da lógica central, MILHO da local
        regras = PRAGAS_MILHO if plant == 'milho' else PRAGAS_SOJA_REGRAS
        
        leitura, error = _get_latest_reading_or_404()
        if error:
            return error
        
        # Calcula risco usando a função importada (leitura já é um dict)
        riscos = calcular_risco(leitura, regras)
        
        # Formata resposta pro frontend
        resultado = [
            {
                'praga': praga,
                'risco': round(valor_risco, 0),
                'status': determinar_status(valor_risco)
            }
            for praga, valor_risco in riscos.items()
        ]
        
        # Ordena por risco (maior primeiro)
        resultado.sort(key=lambda x: x['risco'], reverse=True)
        
        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular risco',
            'details': str(e)
        }), 500


@frontend_bp.route('/pests/risk-historical', methods=['GET'])
def risco_historico():
    """
    Calcula risco de pragas ao longo do tempo (para gráficos de tendência)
    """
    try:
        plant = request.args.get('plant', default='soja').lower()
        hours = request.args.get('hours', default=_DEFAULT_HOURS, type=int)
        hours = min(hours, _MAX_HOURS)
        
        regras = PRAGAS_MILHO if plant == 'milho' else PRAGAS_SOJA_REGRAS
        
        start_timestamp = int(time.time()) - (hours * _SECONDS_PER_HOUR)
        end_timestamp = int(time.time())
        limit = min(hours * _READINGS_PER_HOUR_ESTIMATE, _MAX_HISTORICAL_LIMIT_RISK)
        
        readings = db.get_readings_by_timerange(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit
        )
        
        if not readings:
            return jsonify([]), 200
        
        # Calcula risco para cada leitura
        historico = []
        for r in readings:
            riscos = calcular_risco(r, regras)
            
            historico.append({
                'timestamp': datetime.fromtimestamp(r['timestamp']).isoformat() + 'Z',
                'pragas': [
                    {'praga': nome, 'risco': round(valor, 0)}
                    for nome, valor in riscos.items()
                ]
            })
        
        # Ordena por timestamp (mais antigo primeiro)
        historico.reverse()
        
        return jsonify(historico), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular histórico de risco',
            'details': str(e)
        }), 500