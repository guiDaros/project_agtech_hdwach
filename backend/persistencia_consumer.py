import pika
import json
import time
import sys

# Importa a classe Database do seu módulo de persistência
sys.path.append('.') # Adiciona a pasta raiz do backend ao path para import
from database import db as database_instance # Importa a instância global 'db'
from config import CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME

# Configurações do RabbitMQ
QUEUE_NAME = RABBITMQ_QUEUE_NAME

def connect_rabbitmq():
    """
    Tenta conectar ao CloudAMQP em loop até ter sucesso.
    Retorna: (connection, channel)
    """
    while True:
        try:
            params = pika.URLParameters(CLOUD_AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            print("INFO: Conexão com CloudAMQP estabelecida.")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"ERRO: CloudAMQP não disponível. Tentando reconectar em 5s... ({e})")
            time.sleep(5)

def callback(ch, method, properties, body):
    """Função chamada quando uma mensagem é recebida para Persistência."""
    
    try:
        # 1. Decodificar JSON
        data = json.loads(body.decode('utf-8'))
        
        # 2. Extrair dados
        temperatura = data.get('temperatura')
        umidade_ar = data.get('umidade_ar')
        umidade_solo = data.get('umidade_solo')
        luminosidade = data.get('luminosidade')
        
        # 3. SALVAMENTO NO SQLITE
        reading_id = database_instance.insert_reading(
            temperatura, umidade_ar, umidade_solo, luminosidade
        )

        print(f"PERSISTÊNCIA: Leitura ID {reading_id} salva no SQLite.")
        
        # 4. Confirmar (ACK)
        ch.basic_ack(delivery_tag=method.delivery_tag) 

    except json.JSONDecodeError as e:
        # Erro de "Poison Message": JSON mal formatado.
        print(f" ERRO JSON: {e}. Mensagem não pode ser processada. Descartando (ACK).")
        ch.basic_ack(delivery_tag=method.delivery_tag) # ACK: não faz sentido reprocessar

    except (ValueError, TypeError) as e:
        # Se os dados forem inválidos (falha na validação do database.py)
        # TypeError p/ o caso de 'None' ser comparado (ex: None <= 10)
        print(f"VALIDAÇÃO FALHOU (Não Persistido): {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag) # ACK: não faz sentido reprocessar dados ruins
        
    except Exception as e:
        # Qualquer outro erro (ex: problema no SQLite, falha de conexão DB)
        print(f"ERRO NO PROCESSAMENTO: {e}. Rejeitando a mensagem (requeue)...")
        # Rejeita e envia de volta para a fila (requeue=True)
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) 

def start_persistencia_consumer():
    connection, channel = connect_rabbitmq()
    
    print('INFO: Consumidor de Persistência esperando mensagens. Pressione CTRL+C para sair.')
    
    # Define que o consumidor só receberá 1 mensagem por vez
    channel.basic_qos(prefetch_count=1) 
    
    # Inicia o consumo
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Encerrando Consumidor de Persistência.")
    except pika.exceptions.ConnectionClosedByBroker:
        print("Conexão fechada pelo broker. Reiniciando...")
        start_persistencia_consumer() # Tenta reconectar
    except Exception as e:
        print(f"Erro inesperado no consumidor: {e}")
    finally:
        if connection and connection.is_open:
            try:
                connection.close()
                print("INFO: Conexão com RabbitMQ fechada.")
            except Exception as e:
                print(f"Erro ao fechar conexão: {e}")


if __name__ == '__main__':
    start_persistencia_consumer()