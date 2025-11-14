import serial
import json
import time
import sys
import pika
import os

# --- Configurações ---

# Adiciona a pasta raiz (pai) ao path para importar 'backend.config'
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

# Tenta importar as configurações do backend
try:
    from backend.config import CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME
except ImportError:
    print("❌ ERRO FATAL: Não foi possível encontrar 'backend.config'.")
    print("Verifique se a estrutura de pastas está correta (ex: hardware/ e backend/ na mesma raiz).")
    sys.exit(1)

# Configurações de Hardware
PORTA_SERIAL_PREFERIDA = '/dev/ttyUSB0'  # Porta comum para Arduino Nano/CH340
BAUD_RATE = 9600
TIMEOUT_SERIAL = 2
QUEUE_NAME = RABBITMQ_QUEUE_NAME

# --- Conexão RabbitMQ ---

def connect_rabbitmq():
    """Tenta conectar ao CloudAMQP (RabbitMQ) em loop até ter sucesso."""
    while True:
        try:
            params = pika.URLParameters(CLOUD_AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print("✅ Conexão com RabbitMQ (CloudAMQP) estabelecida.")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ ERRO RabbitMQ: Conexão falhou: {e}. Tentando novamente em 5s...")
            time.sleep(5)

# --- Conexão Arduino ---

def encontrar_porta_arduino():
    """Tenta encontrar automaticamente a porta do Arduino."""
    # Lista de portas priorizadas (incluindo a preferida)
    portas_possiveis = [
        PORTA_SERIAL_PREFERIDA, 
        '/dev/ttyUSB1', 
        '/dev/ttyACM0', 
        '/dev/ttyACM1'
    ]
    
    for porta in portas_possiveis:
        try:
            ser = serial.Serial(porta, BAUD_RATE, timeout=TIMEOUT_SERIAL)
            time.sleep(2)  # Aguarda Arduino resetar
            print(f"✅ Arduino encontrado em: {porta}")
            return ser
        except (serial.SerialException, FileNotFoundError):
            continue
    
    return None

def conectar_arduino():
    """Conecta na porta serial do Arduino, tentando a porta preferida e depois buscando."""
    print("🔍 Procurando Arduino...")
    
    # Tenta porta configurada primeiro
    try:
        ser = serial.Serial(PORTA_SERIAL_PREFERIDA, BAUD_RATE, timeout=TIMEOUT_SERIAL)
        time.sleep(2)
        print(f"✅ Conectado ao Arduino em {PORTA_SERIAL_PREFERIDA}")
        return ser
    except (serial.SerialException, FileNotFoundError):
        print(f"⚠️ Porta {PORTA_SERIAL_PREFERIDA} não encontrada, buscando automaticamente...")
    
    # Tenta encontrar automaticamente
    ser = encontrar_porta_arduino()
    
    if ser is None:
        print("❌ Arduino não encontrado!")
        sys.exit(1)
    
    return ser

# --- Processamento e Validação ---

def validar_dados(dados):
    """Valida se os dados estão dentro de ranges aceitáveis."""
    try:
        temp = float(dados.get('temperatura', 0))
        umid_ar = float(dados.get('umidade_ar', 0))
        umid_solo = float(dados.get('umidade_solo', 0))
        lum = float(dados.get('luminosidade', 0))
        
        if not (-10 <= temp <= 60):
            return False, f"Temperatura fora do range: {temp}°C"
        if not (0 <= umid_ar <= 100):
            return False, f"Umidade ar fora do range: {umid_ar}%"
        if not (0 <= umid_solo <= 1023):
            return False, f"Umidade solo fora do range: {umid_solo}"
        if not (0 <= lum <= 1023):
            return False, f"Luminosidade fora do range: {lum}"
            
        return True, "OK"
    except (ValueError, TypeError) as e:
        return False, f"Erro ao validar: {e}"

def processar_linha(linha):
    """Processa uma linha JSON do Arduino."""
    try:
        linha = linha.strip()
        if not linha.startswith('{'):
            return None, "Linha não é JSON"
            
        dados = json.loads(linha)
        campos_obrigatorios = ['temperatura', 'umidade_ar', 'umidade_solo', 'luminosidade']
        
        if not all(campo in dados for campo in campos_obrigatorios):
            return None, "JSON incompleto"
            
        return dados, None
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"

# --- Publicação ---

def publish_to_rabbitmq(channel, dados):
    """Envia dados para a fila do RabbitMQ."""
    try:
        # Adiciona timestamp
        dados['timestamp'] = int(time.time())
        message = json.dumps(dados)
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        return True, "Publicado"
        
    except (pika.exceptions.ConnectionClosedByPeer, pika.exceptions.StreamLostError) as e:
        print(f"❌ ERRO RabbitMQ: {e}")
        # Levanta a exceção para ser capturada pelo loop 'main' e forçar a reconexão
        raise e
    except Exception as e:
        print(f"❌ ERRO ao publicar: {e}")
        return False, str(e)

# --- Loop Principal ---

def loop_principal(arduino, channel):
    """Loop principal de leitura, processamento e envio."""
    contador_leituras = 0
    contador_erros = 0
    
    print("\n" + "=" * 60)
    print("🌾 SISTEMA DE MONITORAMENTO AGRÍCOLA (PRODUTOR)")
    print(f"📡 Arduino: {arduino.port}")
    print(f"📦 RabbitMQ Fila: {QUEUE_NAME}")
    print("=" * 60)
    print("\n🚀 Iniciando monitoramento...\n")
    
    time.sleep(3)
    arduino.reset_input_buffer()
    
    while True:
        try:
            if arduino.in_waiting > 0:
                linha = arduino.readline().decode('utf-8', errors='ignore').strip()
                
                if not linha: continue
                
                if not linha.startswith('{'):
                    print(f"📋 Arduino: {linha}")
                    continue
                
                dados, erro = processar_linha(linha)
                
                if erro:
                    print(f"⚠️ {erro}: {linha}")
                    contador_erros += 1
                    continue
                
                valido, msg_validacao = validar_dados(dados)
                
                if not valido:
                    print(f"❌ Validação falhou: {msg_validacao}")
                    contador_erros += 1
                    continue
                
                # Exibe leitura
                contador_leituras += 1
                print(f"\n📊 Leitura #{contador_leituras} [{time.strftime('%H:%M:%S')}]")
                print(f"   🌡️  Temperatura: {dados['temperatura']:.1f}°C")
                print(f"   💧 Umidade Ar: {dados['umidade_ar']:.1f}%")
                
                # Envia para RabbitMQ
                sucesso, mensagem = publish_to_rabbitmq(channel, dados) 
                
                if sucesso:
                    print("   ✅ Publicado no CloudAMQP!")
                else:
                    print(f"   ❌ Erro ao publicar: {mensagem}")
                    contador_erros += 1
                
                print(f"   📈 Total: {contador_leituras} leituras | {contador_erros} erros")
        
        except serial.SerialException as e:
            print(f"\n❌ Erro na comunicação serial: {e}")
            print("🔄 Tentando reconectar...")
            arduino.close()
            arduino = conectar_arduino()
            if arduino is None:
                raise e # Se falhar a reconexão, encerra
            arduino.reset_input_buffer()
        
        except Exception as e:
            # Se for um erro de Pika, levanta para o 'main' reconectar
            if isinstance(e, (pika.exceptions.ConnectionClosedByPeer, pika.exceptions.StreamLostError)):
                raise e
            
            print(f"❌ Erro inesperado no loop: {e}")
            contador_erros += 1
            time.sleep(1)

# --- Execução ---

def main():
    """Gerencia as conexões e o loop principal."""
    arduino = None
    connection = None
    
    try:
        # 1. Conecta ao Arduino (sai se falhar)
        arduino = conectar_arduino()
        
        # 2. Loop principal de conexão RabbitMQ
        while True:
            try:
                # Conecta ao RabbitMQ (tenta indefinidamente)
                connection, channel = connect_rabbitmq()
                
                # Inicia o loop de leitura (que roda até uma falha de conexão)
                loop_principal(arduino, channel)
                
            except (pika.exceptions.ConnectionClosedByPeer, pika.exceptions.StreamLostError, pika.exceptions.AMQPConnectionError):
                print("\n🔄 CONEXÃO RABBITMQ PERDIDA! Tentando reconectar em 5 segundos...\n")
                if connection and connection.is_open:
                    connection.close()
                time.sleep(5)
                continue # Volta ao início do 'while True' para reconectar
                
            except Exception as e:
                print(f"❌ ERRO FATAL não recuperável: {e}")
                break # Sai do 'while True'
                
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando monitoramento...")
    except Exception as e:
        print(f"❌ ERRO FATAL (Hardware): {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
            print("Conexão RabbitMQ fechada.")
        if arduino and arduino.is_open:
            arduino.close()
            print("Conexão Arduino fechada.")
        sys.exit(0)

if __name__ == '__main__':
    main()