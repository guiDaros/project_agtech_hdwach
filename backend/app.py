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
    redis_client = redis.from_url(UPSTASH_REDIS_URL)
    redis_client.ping()
    print("✅ Conexão com Upstash Redis (Cache) estabelecida.")
except Exception as e:
    print(f"❌ ERRO FATAL: Falha ao conectar ao Upstash Redis: {e}")
    # Permite que a API inicie, mas as rotas de tempo real falharão.
    redis_client = None 

# ==========================================================
# --- NOVAS ROTAS DE LEITURA (AGORA SÓ LEITURA) ---
# ==========================================================

@app.route('/api/status', methods=['GET'])
def get_api_status():
    """Retorna o status de todos os serviços (Health Check)."""
    redis_status = 'online'
    db_status = 'online'
    
    try:
        if redis_client: redis_client.ping()
    except Exception:
        redis_status = 'offline'

    try:
        # Tenta uma operação leve no SQLite
        database_instance.get_statistics()
    except Exception:
        db_status = 'offline'
        
    return jsonify({
        'success': True,
        'message': 'API de Monitoramento Agrícola',
        'status': 'online',
        'dependencias': {
            'SQLite (Persistência)': db_status,
            'Upstash Redis (Cache)': redis_status,
            'CloudAMQP (Consumidores)': 'Verificar Consumidores',
        },
        'timestamp': int(time.time())
    }), 200


@app.route('/api/latest', methods=['GET'])
def get_latest_data_and_risk():
    """
    Rota CRÍTICA para o Frontend: 
    Lê os dados brutos e o resultado da análise do Upstash Redis (cache).
    """
    if not redis_client:
        return jsonify({'error': 'Redis service unavailable'}), 503

    try:
        # Lê o JSON completo salvo pelo analise_consumer
        data_json = redis_client.get(REDIS_LATEST_DATA_KEY)
        
        if data_json:
            data = json.loads(data_json)
            return jsonify({
                'success': True,
                'tempo_real': data
            }), 200
        else:
            # Tenta pegar a última leitura do SQLite como fallback (caso Redis esteja vazio)
            latest_db = database_instance.get_recent_readings(limit=1)
            if latest_db:
                 return jsonify({
                    'success': True,
                    'tempo_real': {'dados_brutos': latest_db[0], 'nivel_geral': 'N/A - Cache Vazio', 'riscos_detalhados': {}}
                }), 200
            
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
        leituras = database_instance.get_recent_readings(limit=limit)
        
        return jsonify({
            'success': True,
            'total': len(leituras),
            'historico': leituras
        }), 200
    except Exception as e:
        print(f"Erro ao ler do SQLite: {e}")
        return jsonify({'error': 'Erro ao buscar dados históricos'}), 500


# ==========================================================
# --- TASKS DE BACKGROUND E EXECUÇÃO (MANTIDAS) ---
# ==========================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

def cleanup_task():
    """Task de limpeza automática de dados antigos (Mantida)."""
    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando limpeza de dados antigos...")
            deleted = database_instance.cleanup_old_data()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Limpeza concluída: {deleted} registros removidos")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Erro na limpeza: {e}")
        
        time.sleep(DATA_LIMITS['cleanup_interval'])


def start_background_tasks():
    """Inicia tasks em background"""
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task de limpeza automática iniciada")


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