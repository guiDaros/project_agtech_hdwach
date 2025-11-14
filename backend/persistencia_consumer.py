import pika
import json
import time
import sys
# Importa a classe Database do seu módulo de persistência
sys.path.append('.') # Adiciona a pasta raiz do backend ao path para import
from database import db as database_instance # Importa a instância global 'db'
from config import CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME

# Configurações do RabbitMQ (CloudAMQP)
CLOUD_AMQP_URL = CLOUD_AMQP_URL 
QUEUE_NAME = RABBITMQ_QUEUE_NAME

# Conexões globais
RABBITMQ_CONNECTION = None
RABBITMQ_CHANNEL = None

def connect_rabbitmq():
    """Tenta conectar ao CloudAMQP."""
    global RABBITMQ_CONNECTION, RABBITMQ_CHANNEL
    while True:
        try:
            params = pika.URLParameters(CLOUD_AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            RABBITMQ_CONNECTION = connection
            RABBITMQ_CHANNEL = channel
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ ERRO: CloudAMQP não disponível. Tentando reconectar em 5s... ({e})")
            time.sleep(5)

def callback(ch, method, properties, body):
    """Função chamada quando uma mensagem é recebida para Persistência."""
    
    try:
        data = json.loads(body)
        
        # O Produtor (ler_arduino.py) envia os campos:
        temperatura = data.get('temperatura')
        umidade_ar = data.get('umidade_ar')
        umidade_solo = data.get('umidade_solo')
        luminosidade = data.get('luminosidade')
        
        # 1. SALVAMENTO NO SQLITE (USANDO A LÓGICA DO SEU database.py)
        # O método insert_reading já cuida da validação e do timestamp
        reading_id = database_instance.insert_reading(
            temperatura, umidade_ar, umidade_solo, luminosidade
        )

        print(f"✅ PERSISTÊNCIA: Leitura ID {reading_id} salva no SQLite.")
        
        # Confirma que a mensagem foi processada com sucesso (ACK)
        ch.basic_ack(delivery_tag=method.delivery_tag) 

    except ValueError as e:
        # Se os dados forem inválidos (falha na validação do seu database.py)
        print(f"⚠️ VALIDAÇÃO FALHOU (Não Persistido): {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag) # ACK: não faz sentido reprocessar dados ruins
        
    except Exception as e:
        # Qualquer outro erro (ex: problema no SQLite)
        print(f"❌ ERRO NO PROCESSAMENTO: {e}. Rejeitando a mensagem...")
        # Rejeita e envia de volta para a fila (requeue=True)
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) 

def start_persistencia_consumer():
    channel = connect_rabbitmq()
    
    print('INFO: Consumidor de Persistência esperando mensagens. Pressione CTRL+C para sair.')
    
    # Define que o consumidor só receberá 1 mensagem por vez (garante distribuição justa da carga)
    channel.basic_qos(prefetch_count=1) 
    
    # Inicia o consumo
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Encerrando Consumidor de Persistência.")
        if RABBITMQ_CONNECTION and RABBITMQ_CONNECTION.is_open:
            RABBITMQ_CONNECTION.close()

if __name__ == '__main__':
    start_persistencia_consumer()