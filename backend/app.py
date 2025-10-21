from flask import Flask, jsonify
from flask_cors import CORS
from database import db
from routes.sensor_routes import sensor_bp
from routes.analysis_routes import analysis_bp
from routes.frontend_routes import frontend_bp  # NOVO
from config import API, DATA_LIMITS
import time
import threading

# Inicializa Flask
app = Flask(__name__)

# Habilita CORS (permite requisições do frontend do Kaiki)
CORS(app)

# Registra blueprints (rotas modulares)
app.register_blueprint(sensor_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(frontend_bp, url_prefix='/api')  # NOVO - Com prefixo /api


@app.route('/', methods=['GET'])
def home():
    """
    Endpoint raiz - informações da API
    """
    return jsonify({
        'success': True,
        'message': 'API de Monitoramento Agrícola',
        'versao': '1.0',
        'status': 'online',
        'endpoints': {
            'hardware': {
                'POST /dados': 'Recebe leituras dos sensores',
                'GET /dados': 'Lista leituras recentes',
                'GET /dados/latest': 'Última leitura (tempo real)',
                'GET /health': 'Status da API e banco'
            },
            'analise': {
                'GET /analise/estatisticas': 'Estatísticas gerais',
                'GET /analise/dados': 'Dados brutos para análise'
            },
            'frontend': {
                'GET /api/sensors/current': 'Dados atuais (formato frontend)',
                'GET /api/sensors/historical': 'Histórico (formato frontend)',
                'GET /api/pests/risk': 'Risco de pragas'
            }
        },
        'timestamp': int(time.time())
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado',
        'message': 'Verifique a documentação em GET /'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor',
        'message': 'Verifique os logs'
    }), 500


def cleanup_task():
    """
    Task de limpeza automática de dados antigos
    Roda em background a cada 24h
    """
    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando limpeza de dados antigos...")
            deleted = db.cleanup_old_data()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Limpeza concluída: {deleted} registros removidos")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Erro na limpeza: {e}")
        
        # Aguarda 24h até próxima limpeza
        time.sleep(DATA_LIMITS['cleanup_interval'])


def start_background_tasks():
    """Inicia tasks em background"""
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Task de limpeza automática iniciada")


if __name__ == '__main__':
    print("=" * 50)
    print("🌾 API de Monitoramento Agrícola")
    print("=" * 50)
    print(f"Iniciando servidor em {API['host']}:{API['port']}")
    print(f"Debug mode: {API['debug']}")
    print(f"Threaded: {API['threaded']}")
    print(f"Banco de dados: {db.db_path}")
    print("=" * 50)
    
    # Inicia tasks em background
    start_background_tasks()
    
    # Inicia servidor Flask
    app.run(
        host=API['host'],
        port=API['port'],
        debug=API['debug'],
        threaded=API['threaded']
    )