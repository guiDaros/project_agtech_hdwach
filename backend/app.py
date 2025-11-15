import time
import threading
import sys
from flask import Flask, jsonify
from flask_cors import CORS
sys.path.append('.') 
from extensions import db, redis_client 

from routes.frontend_routes import frontend_bp
from routes.analysis_routes import analysis_bp 

from config import API, DATA_LIMITS

app = Flask(__name__)
CORS(app)

app.register_blueprint(frontend_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

def _log_task(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def cleanup_task():
    while True:
        try:
            _log_task("Iniciando limpeza de dados antigos...")
            deleted = db.cleanup_old_data()
            _log_task(f"Limpeza concluída: {deleted} registros removidos")
        except Exception as e:
            _log_task(f"Erro na limpeza: {e}")
        
        time.sleep(DATA_LIMITS['cleanup_interval'])

def start_background_tasks():
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    _log_task("Task de limpeza automática iniciada")


if __name__ == '__main__':
    print("=" * 60)
    print("🌾 API DE MONITORAMENTO DISTRIBUÍDO (FLASK)")
    print("============================================================")
    
    start_background_tasks()
    
    app.run(
        host=API['host'],
        port=API['port'],
        debug=API['debug'],
        threaded=API['threaded']
    )