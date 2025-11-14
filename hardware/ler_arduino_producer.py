import serial
import json
import time
import sys
import pika # Biblioteca RabbitMQ

# Adiciona o diretório '..' (a raiz do projeto) ao path para acessar config.py
# Isso é necessário porque o produtor está na pasta 'hardware'
sys.path.append('..') 
from backend.config import CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME

# ====== CONFIGURAÇÕES DE COMUNICAÇÃO ======
PORTA_SERIAL = '/dev/ttyUSB0'  # Ajuste conforme necessário
BAUD_RATE = 9600
TIMEOUT_SERIAL = 2
# Configurações do RabbitMQ (CloudAMQP)
QUEUE_NAME = RABBITMQ_QUEUE_NAME # Lida pelo config.py
# A conexão RabbitMQ será definida globalmente
RABBITMQ_CONNECTION = None
RABBITMQ_CHANNEL = None


# ====== FUNÇÕES DE CONEXÃO ======

def connect_rabbitmq():
    """Tenta conectar ao RabbitMQ (usando URL do CloudAMQP) e define as variáveis globais de conexão/canal."""
    global RABBITMQ_CONNECTION, RABBITMQ_CHANNEL
    while True:
        try:
            # CHAVE: Usando pika.URLParameters para CloudAMQP
            params = pika.URLParameters(CLOUD_AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            # Declara a fila, tornando-a durável
            channel.queue_declare(queue=QUEUE_NAME, durable=True) 
            
            RABBITMQ_CONNECTION = connection
            RABBITMQ_CHANNEL = channel
            print("✅ Conexão com RabbitMQ (CloudAMQP) estabelecida.")
            return True
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ ERRO: Não foi possível conectar ao CloudAMQP. Tentando novamente em 5s... ({e})")
            time.sleep(5)
            # Retorna False para que a execução possa continuar no loop principal (embora não consiga publicar)
            return False 

# FUNÇÃO encontrar_porta_arduino, conectar_arduino, validar_dados, publish_to_rabbitmq, processar_linha e loop_principal...

def encontrar_porta_arduino():
    """
    Tenta encontrar automaticamente a porta do Arduino (Lógica mantida)
    """
    portas_possiveis = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
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
    """Conecta na porta serial do Arduino (Lógica mantida)"""
    print("🔍 Procurando Arduino...")
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=TIMEOUT_SERIAL)
        time.sleep(2)
        print(f"✅ Conectado ao Arduino em {PORTA_SERIAL}")
        return ser
    except (serial.SerialException, FileNotFoundError):
        print(f"⚠️ Porta {PORTA_SERIAL} não encontrada, buscando automaticamente...")
    
    ser = encontrar_porta_arduino()
    if ser is None:
        print("❌ Arduino não encontrado!")
        sys.exit(1)
    return ser

def validar_dados(dados):
    """
    Valida se os dados estão dentro de ranges aceitáveis (Lógica mantida)
    """
    try:
        temp = float(dados.get('temperatura', 0))
        umid_ar = float(dados.get('umidade_ar', 0))
        umid_solo = float(dados.get('umidade_solo', 0))
        lum = float(dados.get('luminosidade', 0))
        
        # Validações básicas (ajustadas para Python)
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


def publish_to_rabbitmq(dados):
    """
    NOVA FUNÇÃO: Envia dados para a fila do RabbitMQ
    """
    global RABBITMQ_CHANNEL
    if RABBITMQ_CHANNEL is None or RABBITMQ_CHANNEL.is_closed:
        print("❌ ERRO RabbitMQ: Canal fechado. Tentando reconectar...")
        connect_rabbitmq()
        if RABBITMQ_CHANNEL is None or RABBITMQ_CHANNEL.is_closed:
             return False, "Falha na reconexão RabbitMQ."

    try:
        message = json.dumps(dados)
        RABBITMQ_CHANNEL.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            # Mensagem persistente: não se perde em caso de queda do RabbitMQ
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
        return True, "Publicado na fila com sucesso"

    except Exception as e:
        # Pode ocorrer se a rede cair após a conexão inicial
        print(f"❌ ERRO ao publicar: {e}")
        return False, str(e)


def processar_linha(linha):
    """
    Processa uma linha JSON do Arduino (Lógica mantida)
    """
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


def loop_principal():
    """
    Loop principal de leitura e envio
    """
    # 1. Conecta ao Arduino
    arduino = conectar_arduino()
    
    print("\n" + "=" * 60)
    print("🌾 SISTEMA DE MONITORAMENTO AGRÍCOLA (PRODUTOR)")
    print("=" * 60)
    print(f"📡 Arduino: {arduino.port}")
    print(f"📦 RabbitMQ Fila: {QUEUE_NAME} em CloudAMQP")
    print("⏱️  Intervalo: 10 segundos (configurado no Arduino)")
    print("=" * 60)
    print("\n🚀 Iniciando monitoramento...\n")
    
    contador_leituras = 0
    contador_erros = 0
    
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
                
                # Adiciona o timestamp antes de publicar
                dados['timestamp'] = int(time.time())

                # Exibe leitura (mantido)
                contador_leituras += 1
                print(f"\n📊 Leitura #{contador_leituras} [{time.strftime('%H:%M:%S')}]")
                print(f"   🌡️  Temperatura: {dados['temperatura']:.1f}°C")
                print(f"   💧 Umidade Ar: {dados['umidade_ar']:.1f}%")
                print(f"   🌱 Umidade Solo: {dados['umidade_solo']} (ADC)")
                print(f"   ☀️  Luminosidade: {dados['luminosidade']} (ADC)")
                
                # CHAVE: Envia para o RabbitMQ
                sucesso, mensagem = publish_to_rabbitmq(dados) 
                
                if sucesso:
                    print(f"   ✅ Publicado no CloudAMQP! {mensagem}")
                else:
                    # Se falhar, tenta reconectar ao broker para a próxima mensagem
                    print(f"   ❌ Erro ao publicar: {mensagem}")
                    contador_erros += 1
                    connect_rabbitmq() # Tenta restaurar a conexão
                
                print(f"   📈 Total: {contador_leituras} leituras | {contador_erros} erros")
        
        except serial.SerialException as e:
            # Lógica de reconexão serial mantida
            print(f"\n❌ Erro na comunicação serial: {e}")
            print("🔄 Tentando reconectar em 5 segundos...")
            time.sleep(5)
            try:
                arduino.close()
                arduino = conectar_arduino()
            except:
                print("❌ Falha ao reconectar. Encerrando...")
                sys.exit(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Encerrando monitoramento...")
            if RABBITMQ_CONNECTION and RABBITMQ_CONNECTION.is_open:
                RABBITMQ_CONNECTION.close()
            arduino.close()
            sys.exit(0)
        
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            contador_erros += 1
            time.sleep(1)


# ====== EXECUÇÃO ======

if __name__ == '__main__':
    print("=" * 60)
    print("🌾 INTEGRAÇÃO ARDUINO → CLOUDAMQP (PRODUTOR)")
    print("=" * 60)
    
    # 2. Conecta ao RabbitMQ antes de iniciar o loop principal
    connect_rabbitmq()

    # Inicia loop principal
    loop_principal()