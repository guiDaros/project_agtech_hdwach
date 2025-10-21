### BACKEND

```

📍 Passo 1: Vai pra pasta do backend
bashcd /home/pi/backend

📦 Passo 2: Instala dependências (só uma vez)
bashpip install -r requirements.txt
pip install pyserial

🔥 Passo 3: Roda o Flask
bashpython app.py
```

**Deve aparecer:**
```
==================================================
🌾 API de Monitoramento Agrícola
==================================================
Iniciando servidor em 0.0.0.0:5000
...

```

### FRONTEND

```

🧪 Passo 4: Abre OUTRO terminal e testa
bash# Abre nova conexão SSH ou usa Ctrl+Shift+T (novo terminal)
curl http://localhost:5000/

# Deve retornar JSON com info da API

🔌 Passo 5: Se Arduino já tá conectado, roda o leitor
No segundo terminal:
bashcd /home/pi/hardware
python ler_arduino.py
```

**Deve aparecer:**
```
✅ Conectado ao Arduino em /dev/ttyUSB0
🌾 SISTEMA DE MONITORAMENTO AGRÍCOLA
...
📊 Leitura #1 [14:30:15]
   🌡️  Temperatura: 28.5°C
   ...
   ✅ Salvo no banco! ID: 1

✅ Verificar se tá salvando
No terceiro terminal (ou para o leitor com Ctrl+C):
bashcurl http://localhost:5000/dados?limit=5
Deve retornar as últimas 5 leituras em JSON

```


# ERROS

```


🆘 Se der erro
Erro: "No module named 'flask'"
bashpip install flask flask-cors
Erro: "No module named 'serial'"
bashpip install pyserial
Erro: "Permission denied /dev/ttyUSB0"
bashsudo usermod -a -G dialout $USER
# Depois desloga e loga de novo

Cola aqui o que apareceu no terminal! 📸

```
