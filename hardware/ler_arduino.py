import serial
import requests
import json
import time
import sys

# ====== CONFIGURAÇÕES ======
PORTA_SERIAL = '/dev/ttyUSB0'  # Ou /dev/ttyACM0 (depende do Arduino)
BAUD_RATE = 9600
API_URL = 'http://localhost:5000/dados'
TIMEOUT_SERIAL = 2

# ====== FUNÇÕES ======

def encontrar_porta_arduino():
    """
    Tenta encontrar automaticamente a porta do Arduino
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
    """Conecta na porta serial do Arduino"""
    print("🔍 Procurando Arduino...")
    
    # Tenta porta configurada primeiro
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=TIMEOUT_SERIAL)
        time.sleep(2)
        print(f"✅ Conectado ao Arduino em {PORTA_SERIAL}")
        return ser
    except (serial.SerialException, FileNotFoundError):
        print(f"⚠️ Porta {PORTA_SERIAL} não encontrada")
    
    # Tenta encontrar automaticamente
    ser = encontrar_porta_arduino()
    
    if ser is None:
        print("❌ Arduino não encontrado!")
        print("💡 Verifique:")
        print("   1. Arduino está conectado via USB")
        print("   2. Drivers instalados")
        print("   3. Execute: ls /dev/tty* | grep -E 'USB|ACM'")
        sys.exit(1)
    
    return ser


def validar_dados(dados):
    """
    Valida se os dados estão dentro de ranges aceitáveis
    """
    try:
        temp = float(dados.get('temperatura', 0))
        umid_ar = float(dados.get('umidade_ar', 0))
        umid_solo = float(dados.get('umidade_solo', 0))
        lum = float(dados.get('luminosidade', 0))
        
        # Validações básicas
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


def enviar_ao_flask(dados):
    """
    Envia dados para a API Flask
    """
    try:
        response = requests.post(API_URL, json=dados, timeout=5)
        
        if response.status_code == 201:
            resultado = response.json()
            return True, f"ID: {resultado.get('id', 'N/A')}"
        else:
            erro = response.json().get('error', 'Erro desconhecido')
            return False, erro
    
    except requests.exceptions.ConnectionError:
        return False, "Flask não está rodando"
    except requests.exceptions.Timeout:
        return False, "Timeout ao enviar"
    except Exception as e:
        return False, str(e)


def processar_linha(linha):
    """
    Processa uma linha JSON do Arduino
    """
    try:
        # Remove espaços e quebras de linha
        linha = linha.strip()
        
        # Ignora linhas que não são JSON
        if not linha.startswith('{'):
            return None, "Linha não é JSON"
        
        # Parseia JSON
        dados = json.loads(linha)
        
        # Valida estrutura
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
    arduino = conectar_arduino()
    
    print("\n" + "=" * 60)
    print("🌾 SISTEMA DE MONITORAMENTO AGRÍCOLA")
    print("=" * 60)
    print(f"📡 Arduino: {arduino.port}")
    print(f"🌐 API Flask: {API_URL}")
    print(f"⏱️  Intervalo: 10 segundos (configurado no Arduino)")
    print("=" * 60)
    print("\n🚀 Iniciando monitoramento...\n")
    
    contador_leituras = 0
    contador_erros = 0
    
    # Limpa buffer inicial (mensagens de inicialização do Arduino)
    time.sleep(3)
    arduino.reset_input_buffer()
    
    while True:
        try:
            # Verifica se tem dados disponíveis
            if arduino.in_waiting > 0:
                # Lê linha do Serial
                linha = arduino.readline().decode('utf-8', errors='ignore').strip()
                
                # Ignora linhas vazias
                if not linha:
                    continue
                
                # Ignora mensagens de debug do Arduino
                if not linha.startswith('{'):
                    print(f"📋 Arduino: {linha}")
                    continue
                
                # Processa JSON
                dados, erro = processar_linha(linha)
                
                if erro:
                    print(f"⚠️ {erro}: {linha}")
                    contador_erros += 1
                    continue
                
                # Valida dados
                valido, msg_validacao = validar_dados(dados)
                
                if not valido:
                    print(f"❌ Validação falhou: {msg_validacao}")
                    contador_erros += 1
                    continue
                
                # Exibe leitura
                contador_leituras += 1
                print(f"\n📊 Leitura #{contador_leituras} [{time.strftime('%H:%M:%S')}]")
                print(f"   🌡️  Temperatura: {dados['temperatura']:.1f}°C")
                print(f"   💧 Umidade Ar: {dados['umidade_ar']:.1f}%")
                print(f"   🌱 Umidade Solo: {dados['umidade_solo']} (ADC)")
                print(f"   ☀️  Luminosidade: {dados['luminosidade']} (ADC)")
                
                # Envia para Flask
                sucesso, mensagem = enviar_ao_flask(dados)
                
                if sucesso:
                    print(f"   ✅ Salvo no banco! {mensagem}")
                else:
                    print(f"   ❌ Erro ao salvar: {mensagem}")
                    contador_erros += 1
                
                print(f"   📈 Total: {contador_leituras} leituras | {contador_erros} erros")
        
        except serial.SerialException as e:
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
            print(f"📊 Estatísticas finais:")
            print(f"   - Leituras: {contador_leituras}")
            print(f"   - Erros: {contador_erros}")
            print(f"   - Taxa de sucesso: {(contador_leituras/(contador_leituras+contador_erros)*100):.1f}%")
            arduino.close()
            sys.exit(0)
        
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            contador_erros += 1
            time.sleep(1)


# ====== EXECUÇÃO ======

if __name__ == '__main__':
    print("=" * 60)
    print("🌾 INTEGRAÇÃO ARDUINO → FLASK")
    print("=" * 60)
    
    # Verifica se Flask está rodando
    print("🔍 Verificando se Flask está rodando...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=3)
        if response.status_code == 200:
            print("✅ Flask está online!")
        else:
            print("⚠️ Flask respondeu mas com erro")
    except:
        print("❌ Flask não está rodando!")
        print("💡 Execute em outro terminal: python app.py")
        print("\nContinuando mesmo assim (dados não serão salvos)...\n")
        time.sleep(2)
    
    # Inicia loop principal
    loop_principal()