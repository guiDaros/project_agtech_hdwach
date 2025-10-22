from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime
import time

# Blueprint para rotas do frontend (Kaiki)
frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/sensors/current', methods=['GET'])
def sensor_atual():
    """
    Endpoint compatível com o frontend do Kaiki
    Retorna última leitura dos sensores
    
    Query params:
    - plant: soja ou milho (aceito mas não usado por enquanto)
    
    Response formato Kaiki:
    {
        "temperatura": 28.5,
        "umidadeAr": 65,
        "umidadeSolo": 42,
        "luminosidade": 78,
        "timestamp": "2025-10-20T14:30:00Z"
    }
    """
    try:
        # Busca última leitura
        readings = db.get_recent_readings(limit=1)
        
        if not readings:
            return jsonify({
                'success': False,
                'error': 'Nenhuma leitura disponível'
            }), 404
        
        leitura = readings[0]
        
        # Converte para formato do frontend (camelCase + ISO timestamp)
        response = {
            'temperatura': round(leitura['temperatura'], 1),
            'umidadeAr': round(leitura['umidade_ar'], 1),
            'umidadeSolo': round(leitura['umidade_solo'], 1),
            'luminosidade': round(leitura['luminosidade'], 1),
            'timestamp': datetime.fromtimestamp(leitura['timestamp']).isoformat() + 'Z'
        }
        
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
    
    Query params:
    - plant: soja ou milho (aceito mas não usado)
    - hours: número de horas de histórico (padrão: 24, máx: 168)
    
    Response formato Kaiki:
    [
        {
            "hora": "14:30",
            "temperatura": 28.5,
            "umidadeAr": 65,
            "umidadeSolo": 42,
            "luminosidade": 78
        }
    ]
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        # Limita máximo a 7 dias (168 horas)
        hours = min(hours, 168)
        
        # Calcula timestamp inicial
        start_timestamp = int(time.time()) - (hours * 3600)
        end_timestamp = int(time.time())
        
        # Busca dados do período (aproximadamente 1 leitura a cada 10 min)
        readings = db.get_readings_by_timerange(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=min(hours * 6, 1000)
        )
        
        if not readings:
            return jsonify([]), 200
        
        # Converte para formato do frontend
        historico = []
        for r in readings:
            dt = datetime.fromtimestamp(r['timestamp'])
            historico.append({
                'hora': dt.strftime('%H:%M'),
                'temperatura': round(r['temperatura'], 1),
                'umidadeAr': round(r['umidade_ar'], 1),
                'umidadeSolo': round(r['umidade_solo'], 1),
                'luminosidade': round(r['luminosidade'], 1)
            })
        
        # Ordena por hora (mais antigo primeiro para gráficos)
        historico.reverse()
        
        return jsonify(historico), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar histórico',
            'details': str(e)
        }), 500


# ============================================================
# LÓGICA DO EDU - CÁLCULO DE RISCO DE PRAGAS
# ============================================================

# Regras de risco para Soja (baseado no código do Edu)
PRAGAS_SOJA = {
    "Lagarta-da-soja": {
        "temp": (22, 34),
        "umidade": (60, 90),
        "solo": (300, 700),
        "luz": (0, 600)
    },
    "Percevejo-marrom": {
        "temp": (20, 32),
        "umidade": (30, 70),
        "solo": (600, 900),
        "luz": (0, 500)
    },
    "Mosca-branca": {
        "temp": (24, 34),
        "umidade": (30, 60),
        "solo": (600, 950),
        "luz": (0, 400)
    }
}

# Regras de risco para Milho (placeholder - pode ajustar depois)
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


def calcular_risco_edu(dados, regras):
    """
    Calcula risco de pragas usando a lógica EXATA do Edu
    
    Parâmetros:
    - dados: dict com temperatura, umidade_ar, umidade_solo, luminosidade
    - regras: dict com condições de cada praga
    
    Retorna:
    - dict com nome da praga e porcentagem de risco
    """
    riscos = {}
    
    for nome, cond in regras.items():
        pontos = 0
        
        # Verifica cada condição (igual o Edu fez)
        if cond["temp"][0] <= dados["temperatura"] <= cond["temp"][1]:
            pontos += 1
        
        if cond["umidade"][0] <= dados["umidade_ar"] <= cond["umidade"][1]:
            pontos += 1
        
        if cond["solo"][0] <= dados["umidade_solo"] <= cond["solo"][1]:
            pontos += 1
        
        if cond["luz"][0] <= dados["luminosidade"] <= cond["luz"][1]:
            pontos += 1
        
        # Calcula porcentagem (4 condições = 100%)
        riscos[nome] = (pontos / 4) * 100
    
    return riscos


def determinar_status(risco):
    """
    Determina status baseado na porcentagem de risco
    """
    if risco < 40:
        return "baixo"
    elif risco < 70:
        return "médio"
    else:
        return "alto"


@frontend_bp.route('/pests/risk', methods=['GET'])
def risco_pragas():
    """
    Endpoint de risco de pragas usando lógica do Edu
    
    Query params:
    - plant: soja ou milho (padrão: soja)
    
    Response formato Kaiki:
    [
        {
            "praga": "Lagarta-da-soja",
            "risco": 75,
            "status": "alto"
        }
    ]
    """
    try:
        plant = request.args.get('plant', default='soja').lower()
        
        # Seleciona regras baseado na planta
        if plant == 'milho':
            regras = PRAGAS_MILHO
        else:
            regras = PRAGAS_SOJA
        
        # Busca última leitura
        readings = db.get_recent_readings(limit=1)
        
        if not readings:
            return jsonify({
                'success': False,
                'error': 'Nenhuma leitura disponível'
            }), 404
        
        leitura = readings[0]
        
        # Prepara dados no formato que o Edu usa
        dados = {
            "temperatura": leitura['temperatura'],
            "umidade_ar": leitura['umidade_ar'],
            "umidade_solo": leitura['umidade_solo'],
            "luminosidade": leitura['luminosidade']
        }
        
        # Calcula risco usando função do Edu
        riscos = calcular_risco_edu(dados, regras)
        
        # Formata resposta pro frontend
        resultado = []
        for praga, valor_risco in riscos.items():
            resultado.append({
                'praga': praga,
                'risco': round(valor_risco, 0),  # Arredonda pra inteiro
                'status': determinar_status(valor_risco)
            })
        
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
    
    Query params:
    - plant: soja ou milho (padrão: soja)
    - hours: horas de histórico (padrão: 24)
    
    Response:
    [
        {
            "timestamp": "2025-10-20T14:30:00Z",
            "pragas": [
                {"praga": "Lagarta-da-soja", "risco": 75},
                ...
            ]
        }
    ]
    """
    try:
        plant = request.args.get('plant', default='soja').lower()
        hours = request.args.get('hours', default=24, type=int)
        hours = min(hours, 168)
        
        # Seleciona regras
        regras = PRAGAS_MILHO if plant == 'milho' else PRAGAS_SOJA
        
        # Busca histórico
        start_timestamp = int(time.time()) - (hours * 3600)
        end_timestamp = int(time.time())
        
        readings = db.get_readings_by_timerange(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=min(hours * 6, 500)
        )
        
        if not readings:
            return jsonify([]), 200
        
        # Calcula risco pra cada leitura
        historico = []
        for r in readings:
            dados = {
                "temperatura": r['temperatura'],
                "umidade_ar": r['umidade_ar'],
                "umidade_solo": r['umidade_solo'],
                "luminosidade": r['luminosidade']
            }
            
            riscos = calcular_risco_edu(dados, regras)
            
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