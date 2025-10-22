"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { BarChart3, LineChartIcon, Activity, Sun, AlertCircle, CheckCircle2 } from "lucide-react"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

// Configuração da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api"

interface SensorData {
  temperatura: number
  umidadeAr: number
  umidadeSolo: number
  luminosidade: number
  timestamp: string
}

interface HistoricalData {
  hora: string
  temperatura: number
  umidadeAr: number
  umidadeSolo: number
  luminosidade: number
}

interface PestRisk {
  praga: string
  risco: number
  status: "baixo" | "médio" | "alto"
}

export default function ChartsMainArea() {
  const [sensorData, setSensorData] = useState<SensorData | null>(null)
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([])
  const [pestRisk, setPestRisk] = useState<PestRisk[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [plant] = useState<"soja" | "milho">("soja") // Pode ser dinâmico depois

  // Busca dados da API
  const fetchData = async () => {
    try {
      setError(null)

      // Busca dados atuais
      const currentResponse = await fetch(`${API_BASE_URL}/sensors/current?plant=${plant}`)
      if (currentResponse.ok) {
        const currentData = await currentResponse.json()
        setSensorData(currentData)
      }

      // Busca histórico (últimas 24h)
      const historicalResponse = await fetch(`${API_BASE_URL}/sensors/historical?plant=${plant}&hours=24`)
      if (historicalResponse.ok) {
        const historical = await historicalResponse.json()
        setHistoricalData(historical)
      }

      // Busca risco de pragas
      const pestResponse = await fetch(`${API_BASE_URL}/pests/risk?plant=${plant}`)
      if (pestResponse.ok) {
        const pests = await pestResponse.json()
        setPestRisk(pests)
      }

      setIsLoading(false)
    } catch (err) {
      console.error("Erro ao buscar dados:", err)
      setError("Erro ao conectar com o backend. Verifique se está rodando.")
      setIsLoading(false)
    }
  }

  // Busca dados ao montar e a cada 10 segundos
  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000) // Atualiza a cada 10s
    return () => clearInterval(interval)
  }, [plant])

  // Função para cor baseada no status
  const getStatusColor = (status: string) => {
    switch (status) {
      case "alto":
        return "text-red-600 bg-red-100"
      case "médio":
        return "text-yellow-600 bg-yellow-100"
      default:
        return "text-green-600 bg-green-100"
    }
  }

  // Função para cor da barra de risco
  const getBarColor = (status: string) => {
    switch (status) {
      case "alto":
        return "#dc2626"
      case "médio":
        return "#d97706"
      default:
        return "#16a34a"
    }
  }

  if (isLoading) {
    return (
      <main className="charts-main-area flex-1 p-6 overflow-y-auto bg-muted/30">
        <div className="flex items-center justify-center h-full">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-lg font-medium">Carregando dados...</p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="charts-main-area flex-1 p-6 overflow-y-auto bg-muted/30">
      <div className="charts-main-area__container max-w-7xl mx-auto space-y-6">
        {/* Status Card */}
        <Card className={`system-status-card p-6 border-l-4 ${error ? 'border-red-500 bg-red-50' : 'border-primary bg-primary/5'}`}>
          <div className="system-status-card__content flex items-start gap-4">
            <div className={`system-status-card__icon p-3 rounded-lg ${error ? 'bg-red-100' : 'bg-primary/10'}`}>
              {error ? (
                <AlertCircle className="w-7 h-7 text-red-600" />
              ) : (
                <CheckCircle2 className="w-7 h-7 text-primary" />
              )}
            </div>
            <div className="system-status-card__text">
              <h3 className={`system-status-card__title text-xl font-bold mb-1 ${error ? 'text-red-600' : 'text-primary'}`}>
                {error ? "Erro de Conexão" : "Sistema Conectado"}
              </h3>
              <p className="system-status-card__description text-sm text-muted-foreground">
                {error || `Monitorando ${plant} em tempo real. Última atualização: ${sensorData ? new Date(sensorData.timestamp).toLocaleTimeString('pt-BR') : '--:--'}`}
              </p>
            </div>
          </div>
        </Card>

        {/* Gráfico de Probabilidade de Pragas */}
        <Card className="pest-probability-chart p-6">
          <div className="pest-probability-chart__header flex items-center gap-3 mb-4">
            <div className="pest-probability-chart__icon p-2 rounded-lg bg-primary/10">
              <BarChart3 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="pest-probability-chart__title text-lg font-bold">Probabilidade de Pragas - {plant.charAt(0).toUpperCase() + plant.slice(1)}</h3>
          </div>
          <div className="pest-probability-chart__content h-[300px]">
            {pestRisk.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pestRisk} layout="vertical" margin={{ left: 120, right: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis type="category" dataKey="praga" width={110} />
                  <Tooltip 
                    formatter={(value: number) => [`${value}%`, 'Risco']}
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                  />
                  <Bar dataKey="risco" fill="#8884d8" radius={[0, 8, 8, 0]}>
                    {pestRisk.map((entry, index) => (
                      <Bar key={`bar-${index}`} fill={getBarColor(entry.status)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center">
                <p className="text-muted-foreground">Nenhum dado de risco disponível</p>
              </div>
            )}
          </div>
          {/* Status tags */}
          <div className="mt-4 flex flex-wrap gap-2">
            {pestRisk.map((pest, index) => (
              <span key={index} className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(pest.status)}`}>
                {pest.praga}: {pest.risco}% ({pest.status})
              </span>
            ))}
          </div>
        </Card>

        {/* Grid de Gráficos de Sensores */}
        <div className="sensor-charts-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Temperatura */}
          <Card className="temperature-chart p-6 border-2 border-red-200 bg-red-50/50">
            <div className="temperature-chart__header flex items-center gap-3 mb-4">
              <div className="temperature-chart__icon p-2 rounded-lg bg-red-100">
                <LineChartIcon className="w-5 h-5 text-red-600" />
              </div>
              <h3 className="temperature-chart__title text-lg font-bold text-red-600">
                Temperatura (24h) - Atual: {sensorData?.temperatura.toFixed(1) || '--'}°C
              </h3>
            </div>
            <div className="temperature-chart__content h-[250px]">
              {historicalData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="hora" tick={{ fontSize: 12 }} />
                    <YAxis domain={['auto', 'auto']} />
                    <Tooltip 
                      formatter={(value: number) => [`${value.toFixed(1)}°C`, 'Temperatura']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #fecaca' }}
                    />
                    <Line type="monotone" dataKey="temperatura" stroke="#dc2626" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-sm text-muted-foreground">Sem dados históricos</p>
                </div>
              )}
            </div>
          </Card>

          {/* Umidade do Ar */}
          <Card className="air-humidity-chart p-6 border-2 border-blue-200 bg-blue-50/50">
            <div className="air-humidity-chart__header flex items-center gap-3 mb-4">
              <div className="air-humidity-chart__icon p-2 rounded-lg bg-blue-100">
                <Activity className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="air-humidity-chart__title text-lg font-bold text-blue-600">
                Umidade do Ar (24h) - Atual: {sensorData?.umidadeAr.toFixed(1) || '--'}%
              </h3>
            </div>
            <div className="air-humidity-chart__content h-[250px]">
              {historicalData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="hora" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip 
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Umidade']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #bfdbfe' }}
                    />
                    <Line type="monotone" dataKey="umidadeAr" stroke="#2563eb" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-sm text-muted-foreground">Sem dados históricos</p>
                </div>
              )}
            </div>
          </Card>

          {/* Umidade do Solo */}
          <Card className="soil-humidity-chart p-6 border-2 border-cyan-200 bg-cyan-50/50">
            <div className="soil-humidity-chart__header flex items-center gap-3 mb-4">
              <div className="soil-humidity-chart__icon p-2 rounded-lg bg-cyan-100">
                <LineChartIcon className="w-5 h-5 text-cyan-600" />
              </div>
              <h3 className="soil-humidity-chart__title text-lg font-bold text-cyan-600">
                Umidade do Solo (24h) - Atual: {sensorData?.umidadeSolo.toFixed(0) || '--'} ADC
              </h3>
            </div>
            <div className="soil-humidity-chart__content h-[250px]">
              {historicalData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="hora" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 1023]} />
                    <Tooltip 
                      formatter={(value: number) => [`${value.toFixed(0)}`, 'Solo']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #a5f3fc' }}
                    />
                    <Line type="monotone" dataKey="umidadeSolo" stroke="#0891b2" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-sm text-muted-foreground">Sem dados históricos</p>
                </div>
              )}
            </div>
          </Card>

          {/* Luminosidade */}
          <Card className="luminosity-chart p-6 border-2 border-orange-200 bg-orange-50/50">
            <div className="luminosity-chart__header flex items-center gap-3 mb-4">
              <div className="luminosity-chart__icon p-2 rounded-lg bg-orange-100">
                <Sun className="w-5 h-5 text-orange-600" />
              </div>
              <h3 className="luminosity-chart__title text-lg font-bold text-orange-600">
                Luminosidade (24h) - Atual: {sensorData?.luminosidade.toFixed(0) || '--'} ADC
              </h3>
            </div>
            <div className="luminosity-chart__content h-[250px]">
              {historicalData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="hora" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 1023]} />
                    <Tooltip 
                      formatter={(value: number) => [`${value.toFixed(0)}`, 'Luminosidade']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #fed7aa' }}
                    />
                    <Line type="monotone" dataKey="luminosidade" stroke="#ea580c" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-sm text-muted-foreground">Sem dados históricos</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}