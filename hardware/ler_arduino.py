import serial
import requests
import json
import time

# Configurações
PORTA_SERIAL = '/dev/ttyUSB0'  # Ou /dev/ttyACM0 
BAUD_RATE = 9600
API_URL = 'http://localhost:5000/dados'

def conectar_arduino():
    """Conecta na porta serial do Arduino"""
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=2)
        time.sleep(2)  # Aguarda Arduino resetar
        print(f"Conectado ao Arduino em {PORTA_SERIAL}")
        return ser
    except serial.SerialException as e:
        print(f"Erro ao conectar Arduino: {e}")
        print("Tente: ls /dev/tty* para ver portas disponíveis")
        return None

def ler_e_enviar():
    """Loop principal: lê Arduino e envia pro Flask"""
    arduino = conectar_arduino()
    
    if not arduino:
        return
    
    print("🌾 Iniciando monitoramento...")
    print("=" * 50)
    
    while True:
        try:
            # Lê linha do Serial
            if arduino.in_waiting > 0:
                linha = arduino.readline().decode('utf-8').strip()
                
                # Ignora linhas de debug do Arduino
                if not linha.startswith('{'):
                    continue
                
                # Converte JSON
                try:
                    dados = json.loads(linha)
                    
                    # Valida se tem todos os campos
                    campos = ['temperatura', 'umidade_ar', 'umidade_solo', 'luminosidade']
                    if all(campo in dados for campo in campos):
                        
                        print(f"Leitura: Temp={dados['temperatura']}°C "
                              f"Umid_Ar={dados['umidade_ar']}% "
                              f"Umid_Solo={dados['umidade_solo']} "
                              f"Luz={dados['luminosidade']}")
                        
                        # Envia pro Flask
                        response = requests.post(API_URL, json=dados, timeout=5)
                        
                        if response.status_code == 201:
                            print(f"Enviado ao banco! ID: {response.json()['id']}")
                        else:
                            print(f"Erro ao salvar: {response.json()}")
                    
                except json.JSONDecodeError:
                    print(f"JSON invalido: {linha}")
                
                print("-" * 50)
        
        except requests.exceptions.ConnectionError:
            print("Flask não está rodando! Inicie: python app.py")
            time.sleep(5)
        
        except KeyboardInterrupt:
            print("\nEncerrando monitoramento...")
            arduino.close()
            break
        
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(1)

if __name__ == '__main__':
    ler_e_enviar()