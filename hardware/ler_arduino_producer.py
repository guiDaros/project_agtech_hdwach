import pika
import time
import json
import os
import random
import sys

# ==========================================================
# Configurações
# ==========================================================

# Adiciona a pasta raiz do backend ao path para import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.config import CLOUD_AMQP_URL, RABBITMQ_QUEUE_NAME

# Modo de Simulação: Ativado se a variável de ambiente SIMULATE_DATA for 'true'
SIMULATE_MODE = os.environ.get('SIMULATE_DATA', 'false').lower() == 'true'

# Tenta importar 'pyserial'
SERIAL_AVAILABLE = False
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    if not SIMULATE_MODE:
        print("⚠️  Biblioteca 'pyserial' não encontrada. Execute: pip install pyserial")
        print("⚠️  Forçando modo de simulação.")
        SIMULATE_MODE = True

# Configurações Serial (Ignoradas no modo de Simulação)
PORTA_SERIAL_PREFERIDA = '/dev/ttyUSB0' # Porta do Script 1, mantida para prioridade
BAUD_RATE = 9600
TIMEOUT_SERIAL = 2 # 2s (do Script 1) é mais seguro que 1s (do Script 2)

# ==========================================================
# Funções de Conexão e Publicação (Lógica do Script 2)
# ==========================================================

def connect_rabbitmq():
    """Tenta conectar ao CloudAMQP (RabbitMQ) e retorna o canal."""
    try:
        params = pika.URLParameters(CLOUD_AMQP_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)
        print("✅ Conexão com RabbitMQ (CloudAMQP) estabelecida.")
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ ERRO: Falha ao conectar ao CloudAMQP: {e}")
        return None, None

def publish_message(channel, data):
    """Publica a mensagem JSON na fila RabbitMQ."""
    if channel is None:
        return False
        
    try:
        # Serializa o dicionário Python para string JSON
        message = json.dumps(data) 
        
        # Publica a mensagem
        channel.basic_publish(
            exchange='', 
            routing_key=RABBITMQ_QUEUE_NAME, 
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        return True
    except pika.exceptions.ConnectionClosedByPeer:
        print("❌ Conexão RabbitMQ fechada pelo peer.")
        return False
    except Exception as e:
        print(f"❌ ERRO ao publicar: {e}")
        return False

# ==========================================================
# Funções de Leitura (Simulação vs. Hardware)
# ==========================================================

def generate_simulated_data(leitura_id):
    """Gera dados de sensor simulados (Lógica do Script 2)."""
    temp = round(random.uniform(20.0, 35.0), 2)
    umid_ar = random.randint(50, 95)
    umid_solo = random.randint(300, 1000)
    luz = random.randint(500, 1023)
    
    data = {
        'leitura_id': leitura_id,
        'timestamp': int(time.time()),
        'temperatura': temp,
        'umidade_ar': umid_ar,
        'umidade_solo': umid_solo,
        'luminosidade': luz,
    }
    return data

def encontrar_porta_arduino():
    """Tenta encontrar automaticamente a porta do Arduino (Lógica do Script 1)."""
    portas_possiveis = [PORTA_SERIAL_PREFERIDA] + [p.device for p in serial.tools.list_ports.comports() if 'tty' in p.device]
    
    for porta in portas_possiveis:
        try:
            ser = serial.Serial(porta, BAUD_RATE, timeout=TIMEOUT_SERIAL)
            time.sleep(2) # Aguarda Arduino resetar
            print(f"✅ Arduino encontrado em: {porta}")
            return ser
        except (serial.SerialException, FileNotFoundError):
            continue
    return None

def conectar_arduino():
    """Conecta na porta serial do Arduino (Lógica do Script 1, mais robusta)."""
    print("🔍 Procurando Arduino...")
    ser = encontrar_porta_arduino()
    
    if ser is None:
        print("❌ Arduino não encontrado!")
        sys.exit(1)
    return ser

# ==========================================================
# Funções de Processamento (Lógica do Script 1)
# ==========================================================

def validar_dados(dados):
    """Valida se os dados estão dentro de ranges aceitáveis (Lógica do Script 1)."""
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
    """Processa uma linha JSON do Arduino (Lógica do Script 1)."""
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

# ==========================================================
# Loops de Execução
# ==========================================================

def _run_simulation_loop(channel):
    """Loop principal para dados simulados."""
    print("🚀 Iniciando monitoramento... (Modo Simulação)")
    leitura_id = 1
    while True:
        data = generate_simulated_data(leitura_id)
        
        print(f"\n📊 Leitura #{leitura_id} (Simulada) [{time.strftime('%H:%M:%S')}]")
        print(f"   🌡️  Temperatura: {data['temperatura']:.1f}°C")
        print(f"   💧 Umidade Ar: {data['umidade_ar']:.1f}%")
        
        if not publish_message(channel, data):
            print("❌ Publicação falhou. Sinalizando para reconectar...")
            return False # Sinaliza falha
            
        leitura_id += 1
        time.sleep(5) # Intervalo do modo simulação (do Script 2)

def _run_hardware_loop(channel, arduino):
    """Loop principal para leitura do hardware (Lógica do Script 1)."""
    print("🚀 Iniciando monitoramento... (Modo Hardware)")
    print(f"📡 Arduino: {arduino.port}")
    print(f"⏱️  Intervalo: 10 segundos (configurado no Arduino)")
    
    arduino.reset_input_buffer()
    contador_leituras = 0
    contador_erros = 0
    
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
                
                dados['timestamp'] = int(time.time())

                contador_leituras += 1
                print(f"\n📊 Leitura #{contador_leituras} [{time.strftime('%H:%M:%S')}]")
                print(f"   🌡️  Temperatura: {dados['temperatura']:.1f}°C")
                print(f"   💧 Umidade Ar: {dados['umidade_ar']:.1f}%")
                print(f"   🌱 Umidade Solo: {dados['umidade_solo']} (ADC)")
                print(f"   ☀️  Luminosidade: {dados['luminosidade']} (ADC)")
                
                if publish_message(channel, dados):
                    print("   ✅ Publicado no CloudAMQP!")
                else:
                    print("   ❌ Erro ao publicar. Sinalizando para reconectar...")
                    return False # Sinaliza falha
                
                print(f"   📈 Total: {contador_leituras} leituras | {contador_erros} erros")
        
        except serial.SerialException as e:
            print(f"\n❌ Erro na comunicação serial: {e}")
            print("🔄 Tentando reconectar...")
            arduino.close()
            arduino = conectar_arduino()
            if arduino is None:
                return True # Encerra loop (limpamente)
            arduino.reset_input_buffer()
        
        except Exception as e:
            print(f"❌ Erro inesperado no loop hardware: {e}")
            contador_erros += 1
            time.sleep(1)

# ==========================================================
# Loop Principal
# ==========================================================

def main():
    """Gerencia as conexões e seleciona o modo de execução."""
    print("=" * 60)
    print("🌾 INTEGRAÇÃO ARDUINO → CLOUDAMQP (PRODUTOR)")
    print("=" * 60)
    
    # Loop de reconexão do RabbitMQ
    while True:
        connection, channel = connect_rabbitmq()
        if connection is None:
            print("Tentando reconectar em 5s...")
            time.sleep(5)
            continue

        reconnect_needed = True # Default para reconectar
        arduino_conn = None
        
        try:
            if SIMULATE_MODE:
                reconnect_needed = not _run_simulation_loop(channel)
            else:
                arduino_conn = conectar_arduino()
                if arduino_conn:
                    reconnect_needed = not _run_hardware_loop(channel, arduino_conn)
                else:
                    break # Falha ao conectar no Arduino, encerra
                    
        except KeyboardInterrupt:
            print("\n🛑 Encerrando Produtor.")
            reconnect_needed = False
            break
        except Exception as e:
            print(f"❌ ERRO FATAL no loop principal: {e}")
            break
        finally:
            if arduino_conn and arduino_conn.is_open:
                arduino_conn.close()
            if connection and connection.is_open:
                connection.close()
                print("Conexão RabbitMQ fechada.")
        
        if reconnect_needed:
            print("🔄 Conexão RabbitMQ perdida. Tentando reconectar em 5s...")
            time.sleep(5)
        else:
            break # Saída limpa (KeyboardInterrupt ou falha HW)

if __name__ == '__main__':
    main()