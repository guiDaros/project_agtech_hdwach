from flask import Blueprint, request, jsonify
from database import db
import time

# Blueprint para rotas de sensores
sensor_bp = Blueprint('sensor', __name__)


@sensor_bp.route('/dados', methods=['POST'])
def receber_dados():
    """
    Recebe dados do Raspberry Pi (Luis)
    
    Esperado JSON:
    {
        "temperatura": 29.5,
        "umidade_ar": 75.0,
        "umidade_solo": 40.0,
        "luminosidade": 800.0
    }
    """
    try:
        # Valida se é JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Valida campos obrigatórios
        required_fields = ['temperatura', 'umidade_ar', 'umidade_solo', 'luminosidade']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos faltando: {", ".join(missing_fields)}'
            }), 400
        
        # Converte para float (proteção contra strings)
        try:
            temperatura = float(data['temperatura'])
            umidade_ar = float(data['umidade_ar'])
            umidade_solo = float(data['umidade_solo'])
            luminosidade = float(data['luminosidade'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Todos os valores devem ser numéricos'
            }), 400
        
        # Insere no banco (validação acontece aqui)
        reading_id = db.insert_reading(
            temperatura=temperatura,
            umidade_ar=umidade_ar,
            umidade_solo=umidade_solo,
            luminosidade=luminosidade
        )
        
        return jsonify({
            'success': True,
            'message': 'Dados recebidos e armazenados',
            'id': reading_id,
            'timestamp': int(time.time())
        }), 201
    
    except ValueError as e:
        # Erro de validação dos sensores
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        # Erro inesperado
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500


@sensor_bp.route('/dados', methods=['GET'])
def listar_dados():
    """
    Retorna leituras recentes (para o dashboard do Kaiki)
    
    Query params opcionais:
    - limit: quantidade de registros (padrão: 50, máx: 100)
    - start: timestamp inicial (filtro por período)
    - end: timestamp final (filtro por período)
    
    Exemplos:
    GET /dados?limit=20
    GET /dados?start=1697500000&end=1697510000
    """
    try:
        # Parâmetros opcionais
        limit = request.args.get('limit', default=50, type=int)
        start_timestamp = request.args.get('start', type=int)
        end_timestamp = request.args.get('end', type=int)
        
        # Se tiver range de tempo
        if start_timestamp and end_timestamp:
            if start_timestamp >= end_timestamp:
                return jsonify({
                    'success': False,
                    'error': 'start deve ser menor que end'
                }), 400
            
            readings = db.get_readings_by_timerange(
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                limit=limit
            )
        else:
            # Apenas leituras recentes
            readings = db.get_recent_readings(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(readings),
            'data': readings
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar dados',
            'details': str(e)
        }), 500


@sensor_bp.route('/dados/latest', methods=['GET'])
def ultima_leitura():
    """
    Retorna apenas a última leitura (otimizado para dashboards em tempo real)
    Mais rápido que /dados?limit=1
    """
    try:
        readings = db.get_recent_readings(limit=1)
        
        if not readings:
            return jsonify({
                'success': False,
                'error': 'Nenhuma leitura disponível'
            }), 404
        
        return jsonify({
            'success': True,
            'data': readings[0]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar última leitura',
            'details': str(e)
        }), 500


@sensor_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de saúde - verifica se API e banco estão funcionando
    Útil para monitoramento
    """
    try:
        # Tenta buscar estatísticas (testa conexão com BD)
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'database': 'connected',
            'total_readings': stats.get('total_registros', 0),
            'timestamp': int(time.time())
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }), 500