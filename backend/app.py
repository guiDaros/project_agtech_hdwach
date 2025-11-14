import json
import time
import threading
import redis
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Adiciona a pasta raiz do backend ao path para import
sys.path.append('.') 
from database import db as database_instance 
from config import API, DATA_LIMITS, UPSTASH_REDIS_URL, REDIS_LATEST_DATA_KEY, REDIS_RISK_KEY

# ==========================================================
# --- INICIALIZAÇÃO DE SERVIÇOS ---
# ==========================================================

# Inicializa Flask
app = Flask(__name__)
CORS(app)

# 1. Inicializa o Upstash Redis
try:
    redis_client = redis.from_url(UPSTASH_REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("✅ Conexão com Upstash Redis (Cache) estabelecida.")
except Exception as e:
    print(f"❌ ERRO: Falha ao conectar ao Upstash Redis: {e}")
    print("⚠️  A API iniciará, mas rotas de tempo real /api/latest falharão.")
    redis_client = None 

# ==========================================================
# --- FUNÇÕES DE HEALTH CHECK PRIVADAS ---
# ==========================================================

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
    """Verifica o status do DB (SQLite) com uma operação leve."""
    try:
        database_instance.get_statistics()
        return 'online'
    except Exception:
        return 'offline'

# ==========================================================
# --- ROTAS DE LEITURA ---
# ==========================================================

@app.route('/api/status', methods=['GET'])
def get_api_status():
    """Retorna o status de todos os serviços (Health Check)."""
    
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


@app.route('/api/latest', methods=['GET'])
def get_latest_data_and_risk():
    """
    Rota CRÍTICA para o Frontend: 
    Lê os dados brutos e o resultado da análise do Upstash Redis (cache).
    Usa o SQLite como fallback.
    """
    if not redis_client:
        return jsonify({'error': 'Redis service unavailable'}), 503

    try:
        # 1. Tenta buscar do cache Redis
        data_json = redis_client.get(REDIS_LATEST_DATA_KEY)
        
        if data_json:
            data = json.loads(data_json)
            return jsonify({
                'success': True,
                'tempo_real': data
            }), 200

        # 2. Cache miss: Tenta o fallback no SQLite
        latest_db_reading = database_instance.get_recent_readings(limit=1)
        
        if latest_db_reading:
            # Monta uma resposta de fallback com a estrutura esperada
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
        
        # 3. Nenhum dado encontrado
        return jsonify({'success': False, 'message': 'Nenhum dado encontrado no cache ou DB.'}), 404

    except Exception as e:
        print(f"Erro ao ler do Redis/SQLite: {e}")
        return jsonify({'error': 'Erro ao buscar dados de tempo real'}), 500


@app.route('/api/historical/<int:limit>', methods=['GET'])
def get_historical_data(limit):
    """
    Retorna o histórico de leituras do SQLite para gráficos.
    """
    try:
        # Validação simples do limite para evitar abuso
        safe_limit = min(max(1, limit), DATA_LIMITS.get('max_historical_limit', 500))
        
        leituras = database_instance.get_recent_readings(limit=safe_limit)
        
        return jsonify({
            'success': True,
            'total': len(leituras),
            'historico': leituras
        }), 200
    except Exception as e:
        print(f"Erro ao ler do SQLite: {e}")
        return jsonify({'error': 'Erro ao buscar dados históricos'}), 500


# ==========================================================
# --- TASKS DE BACKGROUND E EXECUÇÃO ---
# ==========================================================

def _log_task(message):
    """Helper para logar tasks de background com timestamp."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

def cleanup_task():
    """Task de limpeza automática de dados antigos."""
    while True:
        try:
            _log_task("Iniciando limpeza de dados antigos...")
            deleted = database_instance.cleanup_old_data()
            _log_task(f"Limpeza concluída: {deleted} registros removidos")
        except Exception as e:
            _log_task(f"Erro na limpeza: {e}")
        
        # Aguarda o intervalo definido na configuração
        time.sleep(DATA_LIMITS['cleanup_interval'])


def start_background_tasks():
    """Inicia tasks em background"""
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    _log_task("Task de limpeza automática iniciada")


if __name__ == '__main__':
    print("=" * 60)
    print("🌾 API DE MONITORAMENTO DISTRIBUÍDO (FLASK)")
    print("============================================================")
    
    # Inicia tasks em background
    start_background_tasks()
    
    # Inicia servidor Flask
    app.run(
        host=API['host'],
        port=API['port'],
        debug=API['debug'],
        threaded=API['threaded']
    )