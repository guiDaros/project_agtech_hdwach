# 🌾 Sistema Inteligente de Monitoramento de Risco Agrícola

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Next.js](https://img.shields.io/badge/next.js-14+-black.svg)](https://nextjs.org/)

> Sistema completo de monitoramento em tempo real para detecção de riscos de pragas e fungos em plantações, utilizando IoT, análise de dados e **arquitetura de microsserviços distribuídos**.

---

## 🎯 Sobre o Projeto

Desenvolvido como projeto da disciplina **Hardware Architecture (2025.2)**, este sistema integra sensores IoT, processamento de dados em tempo real e interface web para auxiliar produtores agrícolas na identificação precoce de condições favoráveis ao desenvolvimento de pragas e fungos.

### 🌟 Diferenciais

- **Monitoramento 24/7** com alertas automáticos
- **Análise baseada em dados** de temperatura, umidade e luminosidade
- **Interface intuitiva** com visualizações em tempo real
- **Baixo custo** utilizando hardware open-source
- **Arquitetura Distribuída:** Utiliza RabbitMQ e Redis para processamento assíncrono e cache ultra-rápido
- **Escalável** e adaptável para diferentes culturas

---

## 🎥 Demonstração

### Dashboard Principal
![Dashboard](docs/images/dashboard.png)

### Alertas de Risco
![Alertas](docs/images/alertas.png)

### Gráficos em Tempo Real
![Gráficos](docs/images/graficos.png)

---

## 🏗️ Arquitetura Distribuída (Microsserviços) 🚀

Este projeto utiliza uma arquitetura orientada a mensagens para garantir alta disponibilidade e processamento assíncrono dos dados.
```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ CAMADA DE HARDWARE                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│ Arduino/Raspberry Pi (Produtor)                                                            │
│ ├── Sensores (DHT11, HW080, LDR)                                                           │
│ └── Script Python (Leitor Serial)                                                          │
└────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                     │ JSON de Dados Brutos
                                     ↓
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ CAMADA DE FILA (ASSÍNCRONA)                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│ CloudAMQP (RabbitMQ) - Fila Central                                                        │
│ └── Garante a entrega e desacopla os processos (Análise e Persistência)                   │
└────────────────────────────────────┬────────────────────┬───────────────────────────────────┘
                                     │ Mensagem Duplicada │
                  Consumidor de Análise ↓                 ↓ Consumidor de Persistência
┌─────────────────────────────────────┴────────────────────┴───────────────────────────────────┐
│ CAMADA DE PROCESSAMENTO E ARMAZENAMENTO                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│ Backend Python (Flask)                                                                     │
│ ├── Consumidor de Análise (Cálculo de Risco) → Upstash Redis (Cache)                      │
│ ├── Consumidor de Persistência (Salvamento) → SQLite Database (Histórico)                 │
│ └── Flask API (Busca dados em Tempo Real no Redis)                                         │
└─────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                     │ HTTP/REST (API)
                                     ↓
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ CAMADA DE APRESENTAÇÃO                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│ Next.js Dashboard                                                                          │
│ └── Consome dados em Tempo Real (do Redis, via Flask) e Histórico (do SQLite, via Flask)  │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologias

### Hardware
- **Arduino Uno** - Coleta de dados dos sensores
- **Raspberry Pi 3/4** - Processamento e API
- **Sensores:** DHT11, HW080, LDR

### Backend (Python)
- **Python 3.8+**
- **Flask 3.0.0** - Framework web
- **RabbitMQ (via CloudAMQP)** - Fila de mensagens para comunicação assíncrona
- **Redis (via Upstash)** - Cache de dados em tempo real para latência ultra-baixa
- **SQLite** - Banco de dados embarcado para armazenamento histórico
- **PySerial** - Comunicação serial
- **Pandas** - Análise de dados

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipagem estática
- **Recharts** - Gráficos interativos
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes

### Ferramentas
- **Git** - Controle de versão
- **VSCode** - Editor de código

---

## ✨ Funcionalidades

### ✅ Monitoramento em Tempo Real
- Coleta de dados a cada 10 segundos
- **Leitura Instantânea:** A API serve os dados de tempo real **diretamente do Redis** para latência mínima

### 📊 Análise de Risco
- Cálculo automático de probabilidade de pragas
- Três níveis de alerta: **Baixo**, **Médio**, **Alto**
- Os resultados da análise são **cacheados no Redis** (chave `REDIS_RISK_KEY`)

### 💾 Persistência e Distribuição de Dados
- **SQLite:** Armazenamento eficiente do histórico
- **RabbitMQ:** Garante que todos os dados sejam processados, mesmo com falhas temporárias dos consumidores
- **Redis:** Usado como cache, reduzindo a carga de leitura sobre o SQLite

### 📈 Visualizações
- Gráficos de linha para temperatura, umidade e luminosidade
- Gráfico de barras para risco de pragas
- Histórico de 24 horas

### 🔔 Alertas Inteligentes
- Notificações quando condições favoráveis são detectadas
- Status colorido por nível de risco

---

## 📥 Instalação

### Pré-requisitos

- Raspberry Pi 3/4 com Raspbian OS
- Arduino Uno com sensores conectados
- Python 3.8 ou superior
- Node.js 18+ (para o frontend)
- **Contas** ativas no **CloudAMQP** e **Upstash Redis** (URLs configuradas no `backend/config.py`)

### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/seu-usuario/monitoramento-agricola.git
cd monitoramento-agricola
```

### 2️⃣ Backend (Raspberry Pi)
```bash
cd backend

# Instalar dependências
pip install -r requirements.txt
pip install pyserial

# Configurar permissões da porta serial
sudo usermod -a -G dialout $USER
# (Reinicie a sessão após este comando)
```

### 3️⃣ Arduino
```bash
# Upload do código para o Arduino
cd ../hardware
# Abra arduino_sensors.ino na Arduino IDE
# Compile e faça upload para o Arduino
```

### 4️⃣ Frontend (Computador Local)
```bash
cd ../frontend

# Instalar dependências
npm install

# Configurar variável de ambiente
echo "NEXT_PUBLIC_API_URL=http://IP_DA_RASPBERRY:5000/api" > .env.local
# Substitua IP_DA_RASPBERRY pelo IP real da sua Raspberry Pi
```

---

## 🚀 Como Usar (Iniciando Microsserviços)

É necessário iniciar 4 processos diferentes para que o sistema funcione:

### Iniciar Backend (Raspberry Pi)
```bash
# Terminal 1 - API Flask (Servidor REST e Busca no Redis)
cd backend
python3 app.py

# Terminal 2 - Consumidor de Persistência (Lê do RabbitMQ e Salva no SQLite)
python3 persistencia_consumer.py

# Terminal 3 - Consumidor de Análise (Lê do RabbitMQ, Calcula Risco e Salva no Redis)
python3 analise_consumer.py

# Terminal 4 - Produtor (Simulação para Teste ou Leitura Serial do Arduino)
cd ../hardware
SIMULATE_DATA=true python3 ler_arduino_producer.py
```

### Iniciar Frontend (Computador Local)
```bash
cd frontend
npm run dev
```

### Acessar Dashboard

Abra o navegador em: **http://localhost:3000**

---

## 📁 Estrutura do Projeto
```
monitoramento-agricola/
├── backend/
│   ├── app.py                      # Aplicação Flask principal (API REST)
│   ├── config.py                   # Configurações e credenciais Cloud/DB
│   ├── database.py                 # Operações SQLite
│   ├── persistencia_consumer.py    # Processo 2: Salva no SQLite
│   ├── analise_consumer.py         # Processo 3: Analisa e Salva no Redis
│   ├── analysis_logic.py           # Lógica do cálculo de risco
│   ├── requirements.txt            # Dependências Python
│   └── routes/
│       └── ...
│
├── hardware/
│   ├── ler_arduino_producer.py     # Processo 4: Lê dados e publica no RabbitMQ
│   └── arduino_sensors.ino         # Código do Arduino
│
├── frontend/
│   └── ...
│
├── docs/
├── README.md
└── LICENSE
```

---

## 🌐 API Endpoints

### Dados em Tempo Real (Lê do Redis)

**GET** `/api/latest`

Retorna a última leitura analisada (dados brutos + nível de risco).

**Response:**
```json
{
  "success": true,
  "tempo_real": {
    "leitura_id": 150,
    "temperatura": 31.5,
    "umidade_ar": 88,
    "nivel_geral": "ALTO",
    "riscos_detalhados": { }
  },
  "origem": "Upstash Redis Cache"
}
```

### Histórico (Lê do SQLite)

**GET** `/api/historical/<limit>`

Retorna histórico de leituras do SQLite.

### Status

**GET** `/api/status`

Health check do sistema (API, Redis e SQLite).

---

## 👥 Equipe

| Nome | Função | LinkedIn |
|------|--------|----------|
| Guilherme | Backend & Integração & Pipelines de Dados | [linkedin.com/in/guilherme-vassoller-daros](https://linkedin.com/in/guilherme-vassoller-daros) |
| Luis | Hardware & Sensores | [linkedin.com/in/luis-eduardo-canal-908aba363](https://linkedin.com/in/luis-eduardo-canal-908aba363) |
| Kaiki | Frontend & UI/UX | [linkedin.com/in/kaiki-andré-pauletto-a046a5277](https://linkedin.com/in/kaiki-andré-pauletto-a046a5277) |
| Eduardo | Análise & Pipelines de Dados | [linkedin.com/in/eduardo-herter](https://linkedin.com/in/eduardo-herter) |

**Professor Orientador:** Me. Fernando P. Pinheiro

**Disciplina:** Hardware Architecture – 2025.2

---

## 📊 Performance

### Otimizações Chave

- **RabbitMQ (CloudAMQP):** Desacoplamento e persistência de mensagens para garantir o processamento 100%
- **Redis (Upstash):** Cache de resultados da análise, garantindo latência de leitura da API de < 5ms
- **SQLite com modo WAL:** Alta concorrência de escrita para o banco de dados histórico

### Métricas de Desempenho

- **Latência da API (/api/latest):** < 5ms (busca direta no Redis)
- **Latência da API (/api/historical):** < 50ms (busca no SQLite)
- **Uptime:** 99.5% em testes de 7 dias

---

## 🔮 Melhorias Futuras

- [ ] Implementar Machine Learning para previsão de surtos e IA para sugestões
- [ ] Adicionar suporte para múltiplas culturas (milho, trigo, etc)
- [ ] Sistema de notificações via SMS/WhatsApp
- [ ] Integração com estações meteorológicas
- [ ] Modo offline com sincronização posterior
- [ ] Dashboard melhorado

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  <sub>Se gostou, considere deixar uma ⭐</sub>
</p>
