import requests
import time
import sys
import json
import serial

# Configurações
API_URL = 'http://localhost:5000/dados'
INTERVALO_LEITURA = 10  # mesmo intervalo do Arduino
_REQUEST_TIMEOUT = 5

# Ajuste a porta conforme necessário:
# Arduino Uno -> /dev/ttyACM0
# Arduino Nano / CH340 -> /dev/ttyUSB0
PORTA_SERIAL = '/dev/ttyACM0'

BAUD_RATE = 9600

# Sessão de requests para reuso de conexão (mais eficiente)
session = requests.Session()

# ========= Conectar Arduino ==========
def conectar_arduino():
    """Tenta conectar ao Arduino em loop até ter sucesso."""
    while True:
        try:
            print(f"🔌 Conectando ao Arduino em {PORTA_SERIAL}...")
            ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=2)
            time.sleep(2)  # tempo pro Arduino reiniciar
            print("✅ Arduino conectado!")
            return ser
        except Exception as e:
            print(f"❌ Arduino não encontrado: {e}")
            print("🔁 Tentando novamente em 5 segundos...")
            time.sleep(5)

# ========= Enviar leitura ==========
def enviar_leitura(dados):
    """Envia os dados (payload JSON) para o backend Flask."""
    try:
        response = session.post(API_URL, json=dados, timeout=_REQUEST_TIMEOUT)

        if response.status_code == 201:
            print(f"📡 Enviado! ID: {response.json()['id']}")
            return True
        else:
            print(f"❌ Erro no envio: {response.status_code} | {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Backend Flask offline")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout de {_REQUEST_TIMEOUT}s ao enviar")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

# ========= Helper de Processamento ==========
def _processar_linha_arduino(linha):
    """Helper privado que trata a lógica de uma linha recebida."""
    if not linha:
        # Ignora linhas vazias (ex: timeouts de leitura)
        return

    print(f"🔍 Recebido do Arduino: {linha}")

    try:
        dados = json.loads(linha)
    except json.JSONDecodeError:
        print("⚠ JSON inválido recebido, ignorado")
        return

    if "erro" in dados:
        print(f"⚠ Erro do Arduino: {dados['erro']}")
        return

    # Enviar para o backend
    enviar_leitura(dados)

# ========= Loop principal ==========
def main_loop():
    """Loop principal que lê da serial e coordena o processamento."""
    ser = conectar_arduino()

    while True:
        try:
            # Decodifica como utf-8, ignorando bytes malformados
            linha = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Processa a linha lida
            _processar_linha_arduino(linha)

        except serial.SerialException:
            print("❌ Conexão com Arduino perdida! Tentando reconectar...")
            ser.close() # Fecha a conexão antiga/quebrada
            ser = conectar_arduino()

        except KeyboardInterrupt:
            print("\n🛑 Finalizado pelo usuário.")
            ser.close()
            sys.exit(0)

# ========= Execução ==========
if __name__ == '__main__':
    print("🌾 Iniciando integração Arduino → Raspberry → Flask...")
    main_loop()