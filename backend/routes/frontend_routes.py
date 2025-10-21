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


@frontend_bp.route('/pests/risk', methods=['GET'])
def risco_pragas():
    """
    Endpoint de risco de pragas
    Calcula probabilidade baseado em condições ambientais
    
    Query params:
    - plant: soja ou milho (usado para definir pragas específicas)
    
    Response formato Kaiki:
    [
        {
            "praga": "Lagarta do Cartucho",
            "risco": 65,
            "status": "médio"
        }
    ]
    
    Nota: Lógica básica - Edu vai refinar com modelo mais complexo
    """
    try:
        plant = request.args.get('plant', default='soja')
        
        # Busca últimas 10 leituras para calcular média
        readings = db.get_recent_readings(limit=10)
        
        if not readings:
            return jsonify([]), 200
        
        # Calcula médias das condições
        avg_temp = sum(r['temperatura'] for r in readings) / len(readings)
        avg_umid_ar = sum(r['umidade_ar'] for r in readings) / len(readings)
        avg_umid_solo = sum(r['umidade_solo'] for r in readings) / len(readings)
        
        pragas = []
        
        # === LÓGICA DE RISCO (PLACEHOLDER - EDU VAI MELHORAR) ===
        
        # 1. Lagartas (temperatura alta + umidade moderada)
        if avg_temp > 25:
            risco_lagarta = 0
            
            # Temperatura favorável (25-35°C)
            if 25 <= avg_temp <= 35:
                risco_lagarta += min((avg_temp - 20) * 8, 50)
            
            # Umidade favorável (60-85%)
            if 60 <= avg_umid_ar <= 85:
                risco_lagarta += min((avg_umid_ar - 50) * 0.8, 30)
            
            # Solo úmido favorece
            if avg_umid_solo > 40:
                risco_lagarta += 20
            
            risco_lagarta = min(int(risco_lagarta), 100)
            
            if risco_lagarta > 20:
                status = "baixo" if risco_lagarta < 40 else ("médio" if risco_lagarta < 70 else "alto")
                nome_praga = "Lagarta do Cartucho" if plant == "milho" else "Lagarta da Soja"
                pragas.append({
                    'praga': nome_praga,
                    'risco': risco_lagarta,
                    'status': status
                })
        
        # 2. Fungos (alta umidade do ar)
        if avg_umid_ar > 70:
            risco_fungo = 0
            
            # Umidade muito alta
            if avg_umid_ar > 80:
                risco_fungo += min((avg_umid_ar - 60) * 2, 60)
            else:
                risco_fungo += min((avg_umid_ar - 60) * 1.5, 40)
            
            # Temperatura favorável para fungos (20-30°C)
            if 20 <= avg_temp <= 30:
                risco_fungo += 30
            
            risco_fungo = min(int(risco_fungo), 100)
            
            if risco_fungo > 20:
                status = "baixo" if risco_fungo < 40 else ("médio" if risco_fungo < 70 else "alto")
                nome_fungo = "Ferrugem Asiática" if plant == "soja" else "Mancha Branca"
                pragas.append({
                    'praga': nome_fungo,
                    'risco': risco_fungo,
                    'status': status
                })
        
        # 3. Percevejos (condições secas + temperatura alta)
        if avg_umid_solo < 45 or avg_temp > 30:
            risco_percevejo = 0
            
            # Solo seco
            if avg_umid_solo < 40:
                risco_percevejo += min((50 - avg_umid_solo) * 2, 50)
            
            # Temperatura alta
            if avg_temp > 30:
                risco_percevejo += min((avg_temp - 28) * 10, 40)
            
            risco_percevejo = min(int(risco_percevejo), 100)
            
            if risco_percevejo > 20:
                status = "baixo" if risco_percevejo < 40 else ("médio" if risco_percevejo < 70 else "alto")
                pragas.append({
                    'praga': 'Percevejo',
                    'risco': risco_percevejo,
                    'status': status
                })
        
        # 4. Ácaros (calor + seco)
        if avg_temp > 28 and avg_umid_ar < 60:
            risco_acaro = 0
            
            # Temperatura alta
            risco_acaro += min((avg_temp - 25) * 8, 50)
            
            # Ar seco
            if avg_umid_ar < 50:
                risco_acaro += min((60 - avg_umid_ar) * 1.5, 40)
            
            risco_acaro = min(int(risco_acaro), 100)
            
            if risco_acaro > 20:
                status = "baixo" if risco_acaro < 40 else ("médio" if risco_acaro < 70 else "alto")
                pragas.append({
                    'praga': 'Ácaro Rajado',
                    'risco': risco_acaro,
                    'status': status
                })
        
        # Se não detectou nenhum risco significativo
        if not pragas:
            pragas.append({
                'praga': 'Condições Favoráveis',
                'risco': 15,
                'status': 'baixo'
            })
        
        # Ordena por risco (maior primeiro)
        pragas.sort(key=lambda x: x['risco'], reverse=True)
        
        return jsonify(pragas), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular risco',
            'details': str(e)
        }), 500