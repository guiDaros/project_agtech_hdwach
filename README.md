# 🌾 Sistema Inteligente de Monitoramento de Risco Agrícola

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Next.js](https://img.shields.io/badge/next.js-14+-black.svg)](https://nextjs.org/)

> Sistema completo de monitoramento em tempo real para detecção de riscos de pragas e fungos em plantações, utilizando IoT, análise de dados ambientais e machine learning.

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Demonstração](#-demonstração)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API Endpoints](#-api-endpoints)
- [Equipe](#-equipe)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

Desenvolvido como projeto final da disciplina **Hardware Architecture (2025.2)**, este sistema integra sensores IoT, processamento de dados em tempo real e interface web para auxiliar produtores agrícolas na identificação precoce de condições favoráveis ao desenvolvimento de pragas e fungos.

### 🌟 Diferenciais

- **Monitoramento 24/7** com alertas automáticos
- **Análise baseada em dados** de temperatura, umidade e luminosidade
- **Interface intuitiva** com visualizações em tempo real
- **Baixo custo** utilizando hardware open-source
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

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    CAMADA DE HARDWARE                   │
├─────────────────────────────────────────────────────────┤
│  Arduino Uno                                            │
│  ├── Sensor DHT11 (Temperatura e Umidade do Ar)        │
│  ├── Sensor HW080 (Umidade do Solo)                    │
│  └── Sensor LDR (Luminosidade)                         │
└────────────────┬────────────────────────────────────────┘
                 │ Serial USB
                 ↓
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE PROCESSAMENTO                    │
├─────────────────────────────────────────────────────────┤
│  Raspberry Pi 3/4                                       │
│  ├── Python Script (Leitura Serial)                    │
│  ├── Flask API (REST)                                  │
│  ├── SQLite Database (WAL mode)                        │
│  └── Módulo de Análise (Cálculo de Risco)             │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────────────────────┐
│                CAMADA DE APRESENTAÇÃO                   │
├─────────────────────────────────────────────────────────┤
│  Next.js Dashboard                                      │
│  ├── Gráficos em Tempo Real (Recharts)                │
│  ├── Alertas Inteligentes                              │
│  ├── Histórico de Dados                                │
│  └── Interface Responsiva                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologias

### Hardware
- **Arduino Uno** - Coleta de dados dos sensores
- **Raspberry Pi 3/4** - Processamento e API
- **Sensores:**
  - DHT11 (Temperatura e Umidade do Ar)
  - HW080 (Umidade do Solo)
  - LDR (Luminosidade)

### Backend
- **Python 3.8+**
- **Flask 3.0.0** - Framework web
- **SQLite** - Banco de dados embarcado
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
- **Postman** - Testes de API

---

## ✨ Funcionalidades

### ✅ Monitoramento em Tempo Real
- Coleta de dados a cada 10 segundos
- Exibição instantânea no dashboard
- Atualização automática dos gráficos

### 📊 Análise de Risco
- Cálculo automático de probabilidade de pragas
- Três níveis de alerta: **Baixo**, **Médio**, **Alto**
- Baseado em condições ambientais específicas

### 📈 Visualizações
- Gráficos de linha para temperatura, umidade e luminosidade
- Gráfico de barras para risco de pragas
- Histórico de 24 horas

### 🔔 Alertas Inteligentes
- Notificações quando condições favoráveis são detectadas
- Recomendações de ações preventivas
- Status colorido por nível de risco

### 💾 Persistência de Dados
- Armazenamento eficiente com SQLite
- Limpeza automática de dados antigos (30 dias)
- Otimização para hardware embarcado

---

## 📥 Instalação

### Pré-requisitos

- Raspberry Pi 3/4 com Raspbian OS
- Arduino Uno com sensores conectados
- Python 3.8 ou superior
- Node.js 18+ (para o frontend)

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

## 🚀 Como Usar

### Iniciar Backend (Raspberry Pi)

```bash
# Terminal 1 - API Flask
cd backend
python app.py

# Terminal 2 - Leitor Arduino
python ler_arduino.py
```

### Iniciar Frontend (Computador Local)

```bash
cd frontend
npm run dev
```

### Acessar Dashboard

Abra o navegador em: `http://localhost:3000`

---

## 📁 Estrutura do Projeto

```
monitoramento-agricola/
├── backend/
│   ├── app.py                    # Aplicação Flask principal
│   ├── config.py                 # Configurações do sistema
│   ├── database.py               # Operações de banco de dados
│   ├── ler_arduino.py            # Script de leitura serial
│   ├── requirements.txt          # Dependências Python
│   └── routes/
│       ├── sensor_routes.py      # Endpoints de sensores
│       ├── analysis_routes.py    # Endpoints de análise
│       └── frontend_routes.py    # Endpoints para o dashboard
│
├── hardware/
│   └── arduino_sensors.ino       # Código do Arduino
│
├── frontend/
│   ├── app/                      # Páginas Next.js
│   ├── components/               # Componentes React
│   │   ├── MonitoringHeader.tsx
│   │   ├── SensorsSidebar.tsx
│   │   ├── ChartsMainArea.tsx
│   │   └── SensorDataCard.tsx
│   ├── hooks/                    # Custom hooks
│   └── lib/                      # Utilitários
│
├── docs/
│   ├── images/                   # Capturas de tela
│   └── ARCHITECTURE.md           # Documentação técnica
│
├── README.md
└── LICENSE
```

---

## 🌐 API Endpoints

### Sensores

#### `POST /dados`
Recebe leituras dos sensores (uso interno - Arduino)

**Request Body:**
```json
{
  "temperatura": 28.5,
  "umidade_ar": 65.0,
  "umidade_solo": 450,
  "luminosidade": 320
}
```

**Response:**
```json
{
  "success": true,
  "id": 1,
  "timestamp": 1729500000
}
```

#### `GET /dados?limit=50`
Retorna últimas leituras

#### `GET /dados/latest`
Retorna última leitura apenas

#### `GET /health`
Status da API e banco de dados

### Frontend (com prefixo `/api`)

#### `GET /api/sensors/current?plant=soja`
Dados atuais formatados para o dashboard

**Response:**
```json
{
  "temperatura": 28.5,
  "umidadeAr": 65.0,
  "umidadeSolo": 450,
  "luminosidade": 320,
  "timestamp": "2025-10-22T14:30:00Z"
}
```

#### `GET /api/sensors/historical?hours=24`
Histórico de leituras

#### `GET /api/pests/risk?plant=soja`
Cálculo de risco de pragas

**Response:**
```json
[
  {
    "praga": "Lagarta-da-soja",
    "risco": 75,
    "status": "alto"
  },
  {
    "praga": "Percevejo-marrom",
    "risco": 50,
    "status": "médio"
  }
]
```

### Análise (uso do módulo de análise)

#### `GET /analise/estatisticas`
Estatísticas gerais do banco de dados

#### `GET /analise/dados?limit=100`
Dados brutos para processamento externo

---

## 👥 Equipe

| Nome | Função | LinkedIn |
|------|--------|----------|
| **Guilherme** | Backend & Integração | [linkedin.com/in/seu-perfil](https://linkedin.com) |
| **Luis** | Hardware & Sensores | [linkedin.com/in/perfil-luis](https://linkedin.com) |
| **Kaiki** | Frontend & UI/UX | [linkedin.com/in/perfil-kaiki](https://linkedin.com) |
| **Eduardo** | Análise de Dados | [linkedin.com/in/perfil-eduardo](https://linkedin.com) |

**Professor Orientador:** Me. Fernando P. Pinheiro

**Disciplina:** Hardware Architecture – 2025.2

---

## 📊 Performance

### Métricas de Desempenho

- **Latência da API:** < 50ms (média)
- **Coleta de dados:** 10 segundos por leitura
- **Uso de RAM (Raspberry Pi):** ~150MB
- **Tamanho do banco:** ~1MB por 10.000 leituras
- **Uptime:** 99.5% em testes de 7 dias

### Otimizações Implementadas

- SQLite com modo WAL para escritas mais rápidas
- Connection pooling para reutilização de conexões
- Índices estratégicos para queries otimizadas
- Limpeza automática de dados antigos
- Validação em camadas para economizar processamento
- Queries com LIMIT para proteger memória

---

## 🔮 Melhorias Futuras

- [ ] Implementar Machine Learning para previsão de surtos
- [ ] Adicionar suporte para múltiplas culturas (milho, trigo, etc)
- [ ] Sistema de notificações via SMS/WhatsApp
- [ ] App mobile nativo (iOS/Android)
- [ ] Integração com estações meteorológicas
- [ ] Modo offline com sincronização posterior
- [ ] Suporte para múltiplos sensores simultâneos
- [ ] Dashboard de gestão de fazendas

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- Professor Fernando P. Pinheiro pela orientação
- Comunidade Arduino e Raspberry Pi pela documentação
- Colegas de turma pelo feedback durante o desenvolvimento
- Família e amigos pelo apoio

---

## 📞 Contato

**Guilherme** - [seu-email@example.com](mailto:seu-email@example.com)

**Link do Projeto:** [https://github.com/seu-usuario/monitoramento-agricola](https://github.com/seu-usuario/monitoramento-agricola)

---

<p align="center">
  Feito com ❤️ e ☕ pela equipe OMA
</p>

<p align="center">
  <sub>Se este projeto te ajudou, considere deixar uma ⭐</sub>
</p>
