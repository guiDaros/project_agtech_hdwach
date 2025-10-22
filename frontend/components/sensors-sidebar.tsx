"use client"

import { useEffect, useState } from "react"
import SensorDataCard from "@/components/sensor-data-card"
import { Thermometer, Droplets, Droplet, Sun, Wifi, WifiOff } from "lucide-react"

// Configuração da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api"

export interface SensorReadings {
  temperatura: number | null
  umidadeAr: number | null
  umidadeSolo: number | null
  luminosidade: number | null
  timestamp?: string
}

export default function SensorsSidebar() {
  const [sensorReadings, setSensorReadings] = useState<SensorReadings>({
    temperatura: null,
    umidadeAr: null,
    umidadeSolo: null,
    luminosidade: null,
  })
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<string>("")

  useEffect(() => {
    // Função para buscar dados dos sensores
    const fetchSensorData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/sensors/current?plant=soja`)
        
        if (response.ok) {
          const data = await response.json()
          
          setSensorReadings({
            temperatura: data.temperatura ?? null,
            umidadeAr: data.umidadeAr ?? null,
            umidadeSolo: data.umidadeSolo ?? null,
            luminosidade: data.luminosidade ?? null,
            timestamp: data.timestamp,
          })
          
          setIsConnected(true)
          
          // Atualiza horário da última leitura
          if (data.timestamp) {
            const date = new Date(data.timestamp)
            setLastUpdate(date.toLocaleTimeString('pt-BR'))
          }
        } else {
          setIsConnected(false)
        }
      } catch (error) {
        console.error("Erro ao buscar dados dos sensores:", error)
        setIsConnected(false)
      }
    }

    // Busca inicial
    fetchSensorData()

    // Atualiza a cada 5 segundos
    const interval = setInterval(fetchSensorData, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="sensors-sidebar w-80 border-r bg-sidebar p-6 overflow-y-auto">
      <div className="sensors-sidebar__content space-y-4">
        <div className={`sensors-sidebar__header border-l-4 pl-4 py-3 rounded-r transition-colors ${
          isConnected 
            ? 'border-primary bg-primary/5' 
            : 'border-muted bg-muted/30'
        }`}>
          <div className="flex items-center justify-between mb-1">
            <h2 className="sensors-sidebar__title text-lg font-bold">
              Sensores em Tempo Real
            </h2>
            <div className={`flex items-center gap-1 ${
              isConnected ? 'text-primary' : 'text-muted-foreground'
            }`}>
              {isConnected ? (
                <Wifi className="w-4 h-4" />
              ) : (
                <WifiOff className="w-4 h-4" />
              )}
            </div>
          </div>
          <p className="sensors-sidebar__status text-sm text-muted-foreground">
            {isConnected 
              ? `Última atualização: ${lastUpdate}` 
              : 'Aguardando conexão...'}
          </p>
        </div>

        <div className="sensors-sidebar__cards space-y-3">
          <SensorDataCard
            icon={<Thermometer className="w-5 h-5" />}
            label="Temperatura"
            value={sensorReadings.temperatura}
            unit="°C"
            colorClass="temperatura"
          />

          <SensorDataCard
            icon={<Droplets className="w-5 h-5" />}
            label="Umidade do Ar"
            value={sensorReadings.umidadeAr}
            unit="%"
            colorClass="umidade-ar"
          />

          <SensorDataCard
            icon={<Droplet className="w-5 h-5" />}
            label="Umidade do Solo"
            value={sensorReadings.umidadeSolo}
            unit="ADC"
            colorClass="umidade-solo"
          />

          <SensorDataCard
            icon={<Sun className="w-5 h-5" />}
            label="Luminosidade"
            value={sensorReadings.luminosidade}
            unit="ADC"
            colorClass="luminosidade"
          />
        </div>

        {/* Indicador de conexão */}
        {!isConnected && (
          <div className="sensors-sidebar__alert p-3 rounded-lg bg-yellow-50 border border-yellow-200">
            <p className="text-xs text-yellow-800 font-medium">
              ⚠️ Verifique se o backend está rodando
            </p>
            <p className="text-xs text-yellow-700 mt-1">
              URL: {API_BASE_URL}
            </p>
          </div>
        )}
      </div>
    </aside>
  )
}