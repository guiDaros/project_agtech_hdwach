import json
import time
from flask import Blueprint, jsonify
from extensions import db, redis_client
from config import DATA_LIMITS, REDIS_LATEST_DATA_KEY, REDIS_RISK_KEY

frontend_bp = Blueprint('api', __name__)

def _check_redis_status():
    """Verifica o status do Redis."""
    if not redis_client:
        return 'offline'
    try:
        redis_client.ping()
        return 'online'
    except Exception:
        return 'offline'

def _check_db_status():
    try:
        db.get_statistics()
        return 'online'
    except Exception:
        return 'offline'


@frontend_bp.route('/status', methods=['GET'])
def get_api_status():
    return jsonify({
        'success': True,
        'message': 'API de Monitoramento Agrícola',
        'status': 'online',
        'dependencias': {
            'SQLite (Persistência)': _check_db_status(),
            'Upstash Redis (Cache)': _check_redis_status(),
            'CloudAMQP (Consumidores)': 'Verificar Consumidores',
        },
        'timestamp': int(time.time())
    }), 200


@frontend_bp.route('/latest', methods=['GET'])
def get_latest_data_and_risk():
    if not redis_client:
        return jsonify({'error': 'Redis service unavailable'}), 503

    try:
        data_json = redis_client.get(REDIS_LATEST_DATA_KEY)
        
        if data_json:
            data = json.loads(data_json)
            return jsonify({
                'success': True,
                'tempo_real': data
            }), 200

        latest_db_reading = db.get_recent_readings(limit=1)
        
        if latest_db_reading:
            fallback_data = {
                'dados_brutos': latest_db_reading[0], 
                'nivel_geral': 'N/A - Cache Vazio', 
                'riscos_detalhados': {},
                'timestamp': latest_db_reading[0].get('timestamp', int(time.time()))
            }
            return jsonify({
                'success': True,
                'tempo_real': fallback_data
            }), 200
        
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado no cache ou DB.'}), 404

    except Exception as e:
        print(f"Erro ao ler do Redis/SQLite: {e}")
        return jsonify({'error': 'Erro ao buscar dados de tempo real'}), 500


@frontend_bp.route('/historical/<int:limit>', methods=['GET'])
def get_historical_data(limit):
    try:
        safe_limit = min(max(1, limit), DATA_LIMITS.get('max_historical_limit', 500))
        leituras = db.get_recent_readings(limit=safe_limit)
        return jsonify({
            'success': True,
            'total': len(leituras),
            'historico': leituras
        }), 200
    except Exception as e:
        print(f"Erro ao ler do SQLite: {e}")
        return jsonify({'error': 'Erro ao buscar dados do banco'}), 500