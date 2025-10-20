import requests
import time

# Configurações
API_URL = 'http://localhost:5000/dados'  # Localhost porque roda na mesma Raspberry
INTERVALO_LEITURA = 60  # Segundos entre cada envio

def enviar_leitura(temperatura, umidade_ar, umidade_solo, luminosidade):
    """
    Envia uma leitura pro backend Flask
    """
    try:
        payload = {
            'temperatura': temperatura,
            'umidade_ar': umidade_ar,
            'umidade_solo': umidade_solo,
            'luminosidade': luminosidade
        }
        
        response = requests.post(API_URL, json=payload, timeout=5)
        
        if response.status_code == 201:
            print(f"✅ Dados enviados com sucesso! ID: {response.json()['id']}")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Backend Flask não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


# EXEMPLO DE USO (Luis substitui com código real dos sensores)
if __name__ == '__main__':
    print("🌾 Iniciando coleta de dados...")
    
    while True:
        # AQUI O LUIS COLOCA O CÓDIGO DELE DE LEITURA DOS SENSORES
        # Exemplo com valores simulados:
        temp = 29.5      # Luis substitui por: sensor_temp.read()
        umid_ar = 75.0   # Luis substitui por: sensor_umid_ar.read()
        umid_solo = 40.0 # Luis substitui por: sensor_umid_solo.read()
        lum = 800.0      # Luis substitui por: sensor_ldr.read()
        
        # Envia pro backend
        enviar_leitura(temp, umid_ar, umid_solo, lum)
        
        # Aguarda próxima leitura
        time.sleep(INTERVALO_LEITURA)



# ===================================

# import requests
# import time

# # Configurações
# API_URL = 'http://localhost:5000/dados'  # Localhost porque roda na mesma Raspberry
# INTERVALO_LEITURA = 60  # Segundos entre cada envio

# def enviar_leitura(temperatura, umidade_ar, umidade_solo, luminosidade):
#     """
#     Envia uma leitura pro backend Flask
#     """
#     try:
#         payload = {
#             'temperatura': temperatura,
#             'umidade_ar': umidade_ar,
#             'umidade_solo': umidade_solo,
#             'luminosidade': luminosidade
#         }
        
#         response = requests.post(API_URL, json=payload, timeout=5)
        
#         if response.status_code == 201:
#             print(f"✅ Dados enviados com sucesso! ID: {response.json()['id']}")
#             return True
#         else:
#             print(f"❌ Erro ao enviar: {response.json()}")
#             return False
            
#     except requests.exceptions.ConnectionError:
#         print("❌ Erro: Backend Flask não está rodando")
#         return False
#     except Exception as e:
#         print(f"❌ Erro inesperado: {e}")
#         return False


# # EXEMPLO DE USO (Luis substitui com código real dos sensores)
# if __name__ == '__main__':
#     print("🌾 Iniciando coleta de dados...")
    
#     while True:
#         # AQUI O LUIS COLOCA O CÓDIGO DELE DE LEITURA DOS SENSORES
#         # Exemplo com valores simulados:
#         temp = 29.5      # Luis substitui por: sensor_temp.read()
#         umid_ar = 75.0   # Luis substitui por: sensor_umid_ar.read()
#         umid_solo = 40.0 # Luis substitui por: sensor_umid_solo.read()
#         lum = 800.0      # Luis substitui por: sensor_ldr.read()
        
#         # Envia pro backend
#         enviar_leitura(temp, umid_ar, umid_solo, lum)
        
#         # Aguarda próxima leitura
#         time.sleep(INTERVALO_LEITURA)