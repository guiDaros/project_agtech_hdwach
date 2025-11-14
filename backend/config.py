# import os

# # Diretório base do projeto
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # --- Configurações do Banco de Dados SQLite ---
# DATABASE = {
#     'path': os.path.join(BASE_DIR, 'dados.db'),
#     'timeout': 10,  # Timeout em segundos para operações
#     'check_same_thread': False  # Permite uso em múltiplas threads
# }

# # Otimizações SQLite (CRÍTICO para Raspberry)
# SQLITE_PRAGMAS = {
#     'journal_mode': 'WAL',  # Write-Ahead Logging (mais rápido)
#     'cache_size': -64000,   # 64MB de cache (ajuste conforme RAM disponível)
#     'synchronous': 'NORMAL',  # Balance entre segurança e velocidade
#     'temp_store': 'MEMORY',  # Tabelas temporárias em RAM
#     'mmap_size': 30000000000,  # Memory-mapped I/O (30GB - para arquivos grandes)
# }

# # --- Configurações da API Flask ---
# API = {
#     'host': '0.0.0.0',  # Aceita conexões externas (Raspberry na rede)
#     'port': 5000,
#     'debug': False,  # NUNCA True em produção na Raspberry
#     'threaded': True  # Permite múltiplas requisições simultâneas
# }

# # Limites de dados (economia de memória)
# DATA_LIMITS = {
#     'max_records_query': 100,  # Máximo de registros retornados por query
#     'retention_days': 30,  # Mantém apenas últimos 30 dias de dados
#     'cleanup_interval': 86400  # Limpeza automática a cada 24h (em segundos)
# }

# # Validação de sensores (ranges esperados)
# SENSOR_RANGES = {
#     'temperatura': {'min': -10, 'max': 60},  # °C
#     'umidade_ar': {'min': 0, 'max': 100},  # %
#     'umidade_solo': {'min': 0, 'max': 1023},  # %
#     'luminosidade': {'min': 0, 'max': 1023}  # Valor ADC típico
# }

# # ==========================================================
# # --- NOVAS CONFIGURAÇÕES DE SERVIÇOS DISTRIBUÍDOS (CLOUD) ---
# # ==========================================================

# # 1. CloudAMQP (RabbitMQ)
# # Formato esperado: amqps://user:password@host:port/vhost
# CLOUD_AMQP_URL = "amqps://lpbtrhmf:pyTiZRaaUqKmDLRAHJMpV224vLs5TNdS@gorilla.lmq.cloudamqp.com/lpbtrhmf"   

# RABBITMQ_QUEUE_NAME = 'sensor_data_raw'


# # 2. Upstash Redis
# # Formato esperado: redis://<username>:<password>@<host>:<port>
# UPSTASH_REDIS_URL = "rediss://default:AXckAAIncDJlNmZhNmQ5OTE1ZTA0ZjZjOGJmOTc2NzA5YWE0MjZjZnAyMzA1MDA@fair-cow-30500.upstash.io:6379"

# # Chaves que o Consumidor de Análise usará no Redis
# REDIS_RISK_KEY = 'current_risk_level' 
# REDIS_LATEST_DATA_KEY = 'latest_sensor_reading'

# ==========================================================
# CONFIGURAÇÕES DO PROJETO AGTECH
# ==========================================================

# ----------------------------------------------------------
# 1. Configurações do Banco de Dados SQLite
# ----------------------------------------------------------
# O banco de dados para persistência do histórico.
SQLITE_DB_NAME = 'agtech_history.db'
SQLITE_TABLE_NAME = 'leituras'

# ----------------------------------------------------------
# 2. Configurações do RabbitMQ (CloudAMQP)
# ----------------------------------------------------------
# CHAVE CRÍTICA: URL do seu CloudAMQP (RabbitMQ)
CLOUD_AMQP_URL = 'amqps://ayhhzcdt:n89cmk466nryhwk0ZO4I19W37Ises6oA@leopard.lmq.cloudamqp.com/ayhhzcdt'
RABBITMQ_QUEUE_NAME = 'leituras_sensores'

# ----------------------------------------------------------
# 3. Configurações do Redis (Upstash)
# ----------------------------------------------------------
# CHAVE CRÍTICA: URL do seu Upstash Redis
UPSTASH_REDIS_URL = 'rediss://default:AXckAAIncDJlNmZhNmQ5OTE1ZTA0ZjZjOGJmOTc2NzA5YWE0MjZjZnAyMzA1MDA@fair-cow-30500.upstash.io:6379'

REDIS_LATEST_DATA_KEY = 'latest_sensor_analysis'
REDIS_RISK_KEY = 'latest_risk_level'

# ----------------------------------------------------------
# 4. Configurações de Sensores (Ranges de Validação e Simulação)
# ----------------------------------------------------------
# Usado pelo produtor e pelos consumidores para validação
SENSOR_RANGES = {
    "temperatura": {"min": 10, "max": 40},
    "umidade_ar": {"min": 30, "max": 90},
    # Umidade do solo e Luminosidade são valores ADC (0-1023)
    "umidade_solo": {"min": 200, "max": 950}, 
    "luminosidade": {"min": 100, "max": 1000}
}