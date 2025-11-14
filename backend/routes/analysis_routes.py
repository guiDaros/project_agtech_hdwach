from flask import Blueprint, request, jsonify
from database import db
import time

# Blueprint para rotas de análise
analysis_bp = Blueprint('analysis', __name__)

# Constantes de configuração para este blueprint
_SECONDS_PER_DAY = 86400
_DEFAULT_LIMIT = 100
_MAX_ANALYSIS_LIMIT = 1000
_MAX_ANALYSIS_DAYS = 30


@analysis_bp.route('/analise/estatisticas', methods=['GET'])
def estatisticas_gerais():
    """
    Retorna estatísticas agregadas básicas do banco
    """
    try:
        stats = db.get_statistics()
        
        if not stats or stats.get('total_registros', 0) == 0:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado disponível'
            }), 404
        
        # Calcula período de coleta
        if stats['primeira_leitura'] and stats['ultima_leitura']:
            periodo_dias = (stats['ultima_leitura'] - stats['primeira_leitura']) / _SECONDS_PER_DAY
            stats['periodo_coleta_dias'] = round(periodo_dias, 2)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao calcular estatísticas',
            'details': str(e)
        }), 500


@analysis_bp.route('/analise/dados', methods=['GET'])
def dados_para_analise():
    """
    Retorna dados brutos para o Edu processar com Pandas
    
    Query params opcionais:
    - start: timestamp inicial (Unix)
    - end: timestamp final (Unix)
    - limit: máximo de registros (padrão: 100, máx: 1000)
    """
    try:
        # Parâmetros opcionais
        start_timestamp = request.args.get('start', type=int)
        end_timestamp = request.args.get('end', type=int)
        limit = request.args.get('limit', default=_DEFAULT_LIMIT, type=int)
        
        # Limita máximo de registros (proteção da Raspberry)
        limit = min(limit, _MAX_ANALYSIS_LIMIT)
        
        # Se tiver range de tempo
        if start_timestamp and end_timestamp:
            if start_timestamp >= end_timestamp:
                return jsonify({
                    'success': False,
                    'error': '"start" deve ser menor que "end"'
                }), 400
            
            # Valida período máximo
            max_period = _MAX_ANALYSIS_DAYS * _SECONDS_PER_DAY
            if (end_timestamp - start_timestamp) > max_period:
                return jsonify({
                    'success': False,
                    'error': f'Período máximo: {_MAX_ANALYSIS_DAYS} dias'
                }), 400
            
            readings = db.get_readings_by_timerange(
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                limit=limit
            )
            
            periodo_info = {
                'start': start_timestamp,
                'end': end_timestamp,
                'dias': round((end_timestamp - start_timestamp) / _SECONDS_PER_DAY, 2)
            }
        else:
            # Apenas leituras recentes
            readings = db.get_recent_readings(limit=limit)
            periodo_info = None
        
        return jsonify({
            'success': True,
            'count': len(readings),
            'periodo': periodo_info,
            'data': readings
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao buscar dados',
            'details': str(e)
        }), 500