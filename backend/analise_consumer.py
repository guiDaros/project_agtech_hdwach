import pika
import redis
import json
import sys
import time

# Adiciona a pasta raiz do backend ao path para import
sys.path.append('.')

from config import (
    CLOUD_AMQP_URL, UPSTASH_REDIS_URL, RABBITMQ_QUEUE_NAME, 
    REDIS_RISK_KEY, REDIS_LATEST_DATA_KEY
)
from analysis_logic import calcular_risco, formatar_resultado_cache

r_cache = None
QUEUE_NAME = RABBITMQ_QUEUE_NAME

def connect_redis():
    """Conecta ao Upstash Redis usando a URL de configuração. Sai em caso de falha."""
    global r_cache
    try:
        # decode_responses=True faz o cliente redis retornar strings (não bytes)
        r_cache = redis.from_url(UPSTASH_REDIS_URL, decode_responses=True)
        r_cache.ping()
        print(" Conexão com Upstash Redis estabelecida.")
    except Exception as e:
        print(f" ERRO FATAL: Falha ao conectar ao Upstash Redis: {e}")
        sys.exit(1)

def callback(ch, method, properties, body):
    """Função chamada ao receber uma mensagem do RabbitMQ."""
    
    try:
        # 1. Tentar decodificar o JSON
        dados_brutos = json.loads(body.decode('utf-8'))
        
    except json.JSONDecodeError as e:
        # 2. Se falhar, é uma "poison message". Rejeitar permanentemente.
        print(f" ERRO DE DECODIFICAÇÃO JSON: {e}. Mensagem: {body}. Rejeitando (nack, requeue=False)...")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
        
    try:
        # 3. Processar a lógica de negócio
        riscos = calcular_risco(dados_brutos)
        
        # formatar_resultado_cache retorna um dicionário
        resultado_final_dict = formatar_resultado_cache(dados_brutos, riscos)
        
        # 4. Preparar dados para o cache
        # Serializar o dicionário completo para o cache principal
        resultado_final_json = json.dumps(resultado_final_dict)
        # Extrair o nível de risco para a chave separada
        nivel_geral = resultado_final_dict['nivel_geral']
        
        # 5. Usar um pipeline para executar múltiplos comandos SET de forma eficiente
        with r_cache.pipeline() as pipe:
            pipe.set(REDIS_LATEST_DATA_KEY, resultado_final_json)
            pipe.set(REDIS_RISK_KEY, nivel_geral)
            pipe.execute()

        print(f" ANÁLISE/CACHE: Nível de Risco: {nivel_geral} | Publicado no Upstash Redis.")
        
        # 6. Confirmar sucesso ao RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # 7. Se o processamento (passo 3-5) falhar, rejeitar a mensagem
        print(f" ERRO NO PROCESSAMENTO DA ANÁLISE: {e}. Rejeitando (nack, requeue=False)...")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Inicia o loop principal de escuta do RabbitMQ."""
    connection = None
    try:
        params = pika.URLParameters(CLOUD_AMQP_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print(" Conexão com CloudAMQP estabelecida.")
        
    except pika.exceptions.AMQPConnectionError as e:
        # Tenta reconectar em loop se a conexão falhar (comportamento do script original)
        print(f" ERRO: CloudAMQP não disponível. Tentando reconectar em 5s... ({e})")
        time.sleep(5)
        start_consumer() # Recomeça o processo de conexão
        return # Sai desta tentativa falha
    except Exception as e:
        print(f" ERRO FATAL: Falha inesperada ao conectar ao CloudAMQP: {e}")
        sys.exit(1)
        
    # Garante que o consumidor só processa uma mensagem por vez
    channel.basic_qos(prefetch_count=1)
        
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False # Confirmação manual é necessária (basic_ack/nack)
    )

    print(' Aguardando mensagens. Para sair, pressione CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupção detectada. Fechando conexão.')
    except pika.exceptions.ConnectionClosedByBroker:
        print(" Conexão fechada pelo broker. Tentando reconectar...")
        start_consumer() # Tenta reconectar
    except Exception as e:
        print(f"Erro inesperado durante o consumo: {e}")
    finally:
        if connection and connection.is_open:
            try:
                connection.close()
                print(" Conexão com RabbitMQ fechada.")
            except Exception as e:
                print(f" Erro ao fechar conexão RabbitMQ: {e}")


if __name__ == '__main__':
    connect_redis()
    # A conexão Redis é fatal (sai se falhar),
    # então não é preciso checar 'if r_cache'
    start_consumer()