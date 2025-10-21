import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações do Banco de Dados
DATABASE = {
    'path': os.path.join(BASE_DIR, 'dados.db'),
    'timeout': 10,  # Timeout em segundos para operações
    'check_same_thread': False  # Permite uso em múltiplas threads
}

# Otimizações SQLite (CRÍTICO para Raspberry)
SQLITE_PRAGMAS = {
    'journal_mode': 'WAL',  # Write-Ahead Logging (mais rápido)
    'cache_size': -64000,   # 64MB de cache (ajuste conforme RAM disponível)
    'synchronous': 'NORMAL',  # Balance entre segurança e velocidade
    'temp_store': 'MEMORY',  # Tabelas temporárias em RAM
    'mmap_size': 30000000000,  # Memory-mapped I/O
}

# Configurações da API Flask
API = {
    'host': '0.0.0.0',  # Aceita conexões externas (Raspberry na rede)
    'port': 5000,
    'debug': False,  # NUNCA True em produção na Raspberry
    'threaded': True  # Permite múltiplas requisições simultâneas
}

# Limites de dados (economia de memória)
DATA_LIMITS = {
    'max_records_query': 100,  # Máximo de registros retornados por query
    'retention_days': 30,  # Mantém apenas últimos 30 dias de dados
    'cleanup_interval': 86400  # Limpeza automática a cada 24h (em segundos)
}

# Validação de sensores (ranges esperados)
SENSOR_RANGES = {
    'temperatura': {'min': -10, 'max': 60},  # °C
    'umidade_ar': {'min': 0, 'max': 100},  # %
    'umidade_solo': {'min': 0, 'max': 1023},  # %
    'luminosidade': {'min': 0, 'max': 1023}  # Valor ADC típico
}
