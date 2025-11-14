# import pika
# import json
# import time
# import sys
# import redis
# import os

# # Adiciona a pasta raiz do backend ao path para import
# sys.path.append('.') 
# from config import (
#     CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME, UPSTASH_REDIS_URL,
#     REDIS_RISK_KEY, REDIS_LATEST_DATA_KEY
# )
# from analysis_logic import calcular_risco, formatar_resultado_cache

# # ==========================================================
# # --- INICIALIZAÇÃO DE SERVIÇOS ---
# # ==========================================================

# # 1. RabbitMQ (CloudAMQP)
# RABBITMQ_CONNECTION = None
# RABBITMQ_CHANNEL = None

# def connect_rabbitmq():
#     """Tenta conectar ao CloudAMQP (RabbitMQ)."""
#     global RABBITMQ_CONNECTION, RABBITMQ_CHANNEL
#     while True:
#         try:
#             params = pika.URLParameters(CLOUD_AMQP_URL)
#             connection = pika.BlockingConnection(params)
#             channel = connection.channel()
#             channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)
            
#             RABBITMQ_CONNECTION = connection
#             RABBITMQ_CHANNEL = channel
#             return channel
#         except pika.exceptions.AMQPConnectionError as e:
#             print(f"❌ ERRO: CloudAMQP não disponível. Tentando reconectar em 5s... ({e})")
#             time.sleep(5)

# # 2. Redis (Upstash)
# try:
#     # A biblioteca 'redis' suporta a conexão via URL para Upstash
#     redis_client = redis.from_url(UPSTASH_REDIS_URL)
#     # Testa a conexão
#     redis_client.ping()
#     print("✅ Conexão com Upstash Redis estabelecida.")
# except Exception as e:
#     print(f"❌ ERRO FATAL: Falha ao conectar ao Upstash Redis: {e}")
#     sys.exit(1)


# # ==========================================================
# # --- LÓGICA DO CONSUMIDOR ---
# # ==========================================================

# def callback(ch, method, properties, body):
#     """Função chamada quando uma mensagem é recebida para Análise e Cache."""
    
#     try:
#         data = json.loads(body)
        
#         # 1. Executa a Análise (Calcula Riscos)
#         riscos_calculados = calcular_risco(data)
        
#         # 2. Formata o resultado para cache
#         resultado_final = formatar_resultado_cache(data, riscos_calculados)

#         # 3. SALVAMENTO NO REDIS (UPSTASH)
#         # Salva o resultado principal (nível de risco geral e detalhes)
#         redis_client.set(REDIS_LATEST_DATA_KEY, json.dumps(resultado_final))
        
#         # Salva o nível de risco geral separadamente (pode ser útil para uma consulta rápida)
#         redis_client.set(REDIS_RISK_KEY, resultado_final['nivel_geral'])

#         print(f"✅ ANÁLISE/CACHE: Nível de Risco: {resultado_final['nivel_geral']} | Publicado no Upstash Redis.")
        
#         # Confirma que a mensagem foi processada com sucesso (ACK)
#         ch.basic_ack(delivery_tag=method.delivery_tag) 

#     except Exception as e:
#         print(f"❌ ERRO NO PROCESSAMENTO DA ANÁLISE: {e}. Rejeitando a mensagem...")
#         # Rejeita e envia de volta para a fila (requeue=True)
#         ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) 

# def start_analise_consumer():
#     channel = connect_rabbitmq()
    
#     print('INFO: Consumidor de Análise esperando mensagens. Pressione CTRL+C para sair.')
    
#     # Define que o consumidor só receberá 1 mensagem por vez
#     channel.basic_qos(prefetch_count=1) 
    
#     # Inicia o consumo
#     channel.basic_consume(queue=RABBITMQ_QUEUE_NAME, on_message_callback=callback)
    
#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         print("🛑 Encerrando Consumidor de Análise.")
#         if RABBITMQ_CONNECTION and RABBITMQ_CONNECTION.is_open:
#             RABBITMQ_CONNECTION.close()

# if __name__ == '__main__':
#     # Certifique-se de que a biblioteca 'redis' está instalada: pip install redis
#     start_analise_consumer()

import pika
import redis
import json
import time
import sys

# Adiciona o diretório raiz ao path para importação
sys.path.append('.')

# Importa as configurações do backend/config.py
from config import CLOUD_AMQP_URL, UPSTASH_REDIS_URL, RABBITMQ_QUEUE_NAME, REDIS_RISK_KEY, REDIS_LATEST_DATA_KEY
# Importa a lógica de análise do backend/analysis_logic.py
from analysis_logic import calcular_risco, formatar_resultado_cache 

# Variáveis globais de conexão (serão inicializadas em main)
r_cache = None
QUEUE_NAME = RABBITMQ_QUEUE_NAME

def connect_redis():
    """Conecta ao Upstash Redis usando a URL de configuração."""
    global r_cache
    try:
        # A biblioteca redis-py aceita diretamente a URL rediss://
        r_cache = redis.from_url(UPSTASH_REDIS_URL, decode_responses=True)
        r_cache.ping()
        print("✅ Conexão com Upstash Redis estabelecida.")
    except Exception as e:
        print(f"❌ ERRO FATAL: Falha ao conectar ao Upstash Redis: {e}")
        sys.exit(1)

def callback(ch, method, properties, body):
    """Função chamada ao receber uma mensagem do RabbitMQ."""
    
    # === A CORREÇÃO ESTÁ AQUI ===
    try:
        # 1. Decodificar a mensagem JSON para um dicionário Python
        # O corpo (body) da mensagem é uma string JSON (bytes), precisa de .decode() e json.loads()
        dados_brutos = json.loads(body.decode('utf-8'))
        
    except json.JSONDecodeError as e:
        print(f"❌ ERRO DE DECODIFICAÇÃO JSON: {e}. Mensagem: {body}. Rejeitando a mensagem...")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Rejeita a mensagem permanentemente
        return
        
    # === A PARTIR DAQUI, 'dados_brutos' É UM DICIONÁRIO PYTHON ===
    try:
        # 2. Executa a lógica de análise
        riscos = calcular_risco(dados_brutos)
        
        # 3. Formata o resultado para o cache
        cache_data_json = formatar_resultado_cache(dados_brutos, riscos)
        
        # 4. Salva no Upstash Redis
        # O resultado é salvo como uma string JSON no Redis para ser lido pela API
        r_cache.set(REDIS_LATEST_DATA_KEY, cache_data_json)
        
        # 5. Opcional: Salva o nível de risco (útil para dashboards)
        data_obj = json.loads(cache_data_json) # Transforma de volta para objeto para pegar o nível
        r_cache.set(REDIS_RISK_KEY, data_obj['nivel_geral'])

        # Log de sucesso
        print(f"✅ ANÁLISE/CACHE: Nível de Risco: {data_obj['nivel_geral']} | Publicado no Upstash Redis.")
        
        # 6. Confirma a mensagem para o RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Registra qualquer erro de processamento e rejeita a mensagem
        print(f"❌ ERRO NO PROCESSAMENTO DA ANÁLISE: {e}. Rejeitando a mensagem...")
        # basic_nack rejeita a mensagem, garantindo que ela não volte para a fila
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Inicia o loop principal de escuta do RabbitMQ."""
    # Tenta estabelecer a conexão RabbitMQ
    try:
        params = pika.URLParameters(CLOUD_AMQP_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print("✅ Conexão com CloudAMQP estabelecida.")
    except Exception as e:
        print(f"❌ ERRO FATAL: Falha ao conectar ao CloudAMQP: {e}")
        sys.exit(1)
        
    # Configura o consumo da fila
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False # Desliga o auto-ack para confirmar manualmente após o processamento
    )

    print(' [*] Aguardando mensagens. Para sair, pressione CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupção detectada. Fechando conexão.')
    except Exception as e:
        print(f"Erro durante o consumo: {e}")
    finally:
        try:
            connection.close()
        except:
            pass # Ignora erros de fechamento


if __name__ == '__main__':
    # Tenta conectar ao Redis primeiro
    connect_redis()
    
    # Garante que o Redis está conectado antes de iniciar o consumidor
    if r_cache:
        start_consumer()