# ==========================================================
# CONFIGURAÇÕES ORIGINAIS (COMENTADAS)
# ==========================================================

# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DATABASE = {
#     'path': os.path.join(BASE_DIR, 'dados.db'),
#     'timeout': 10,
#     'check_same_thread': False
# }

# SQLITE_PRAGMAS = {
#     'journal_mode': 'WAL',
#     'cache_size': -64000,
#     'synchronous': 'NORMAL',
#     'temp_store': 'MEMORY',
#     'mmap_size': 30000000000,
# }

# API = {
#     'host': '0.0.0.0',
#     'port': 5000,
#     'debug': False,
#     'threaded': True
# }

# DATA_LIMITS = {
#     'max_records_query': 100,
#     'retention_days': 30,
#     'cleanup_interval': 86400
# }

# SENSOR_RANGES = {
#     'temperatura': {'min': -10, 'max': 60},
#     'umidade_ar': {'min': 0, 'max': 100},
#     'umidade_solo': {'min': 0, 'max': 1023},
#     'luminosidade': {'min': 0, 'max': 1023}
# }

# CLOUD_AMQP_URL = "amqps://lpbtrhmf:pyTiZRaaUqKmDLRAHJMpV224vLs5TNdS@gorilla.lmq.cloudamqp.com/lpbtrhmf"
# RABBITMQ_QUEUE_NAME = 'sensor_data_raw'

# UPSTASH_REDIS_URL = "rediss://default:AXckAAIncDJlNmZhNmQ5OTE1ZTA0ZjZjOGJmOTc2NzA5YWE0MjZjZnAyMzA1MDA@fair-cow-30500.upstash.io:6379"
# REDIS_RISK_KEY = 'current_risk_level' 
# REDIS_LATEST_DATA_KEY = 'latest_sensor_reading'


# ==========================================================
# CONFIGURAÇÕES ATUAIS DO PROJETO AGTECH (ATIVAS)
# ==========================================================

# ----------------------------------------------------------
# 1. Banco de Dados SQLite
# ----------------------------------------------------------
SQLITE_DB_NAME = 'agtech_history.db'
SQLITE_TABLE_NAME = 'leituras'

# 🔥 VARIÁVEL NECESSÁRIA PARA O database.py FUNCIONAR
DATABASE = {
    "path": SQLITE_DB_NAME,
    "timeout": 10,
    "check_same_thread": False
}

# 🔥 PRAGMAS necessários pelo database.py
SQLITE_PRAGMAS = {
    'journal_mode': 'WAL',
    'cache_size': -64000,
    'synchronous': 'NORMAL',
    'temp_store': 'MEMORY'
}

# 🔥 LIMITES usados pelo database.py
DATA_LIMITS = {
    'max_records_query': 100,
    'retention_days': 7,
    'cleanup_interval': 86400
}

# ----------------------------------------------------------
# 2. RabbitMQ
# ----------------------------------------------------------
CLOUD_AMQP_URL = 'amqps://ayhhzcdt:n89cmk466nryhwk0ZO4I19W37Ises6oA@leopard.lmq.cloudamqp.com/ayhhzcdt'
RABBITMQ_QUEUE_NAME = 'leituras_sensores'

# ----------------------------------------------------------
# 3. Redis
# ----------------------------------------------------------
UPSTASH_REDIS_URL = 'rediss://default:AXckAAIncDJlNmZhNmQ5OTE1ZTA0ZjZjOGJmOTc2NzA5YWE0MjZjZnAyMzA1MDA@fair-cow-30500.upstash.io:6379'

REDIS_LATEST_DATA_KEY = 'latest_sensor_analysis'
REDIS_RISK_KEY = 'latest_risk_level'

# ----------------------------------------------------------
# 4. Ranges de Sensores
# ----------------------------------------------------------
SENSOR_RANGES = {
    "temperatura": {"min": 10, "max": 40},
    "umidade_ar": {"min": 30, "max": 90},
    "umidade_solo": {"min": 200, "max": 950},
    "luminosidade": {"min": 100, "max": 1000}
}

API = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
    "threaded": True
}
