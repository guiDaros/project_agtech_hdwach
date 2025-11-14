"use client"

import { useEffect, useState } from "react"
import SensorDataCard from "@/components/sensor-data-card"
import WeatherForecast from "@/components/weather-forecast"
import { Thermometer, Droplets, Droplet, Sun } from "lucide-react"

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

  useEffect(() => {
    // TODO: Conectar com API do backend para receber dados dos sensores
    // Exemplo de implementação futura:
    // const fetchSensorData = async () => {
    //   const response = await fetch('/api/sensors')
    //   const data = await response.json()
    //   setSensorReadings(data)
    // }
    // fetchSensorData()
    // const interval = setInterval(fetchSensorData, 5000) // Atualizar a cada 5 segundos
    // return () => clearInterval(interval)
  }, [])

  return (
    <aside className="sensors-sidebar w-80 border-r bg-sidebar p-6 overflow-y-auto">
      <div className="sensors-sidebar__content space-y-4">
        <WeatherForecast />

        <div className="sensors-sidebar__header border-l-4 border-primary pl-4 bg-primary/5 py-3 rounded-r">
          <h2 className="sensors-sidebar__title text-lg font-bold mb-1">Sensores em Tempo Real</h2>
          <p className="sensors-sidebar__status text-sm text-muted-foreground">Aguardando dados dos sensores</p>
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
            unit="%"
            colorClass="umidade-solo"
          />

          <SensorDataCard
            icon={<Sun className="w-5 h-5" />}
            label="Luminosidade"
            value={sensorReadings.luminosidade}
            unit="%"
            colorClass="luminosidade"
          />
        </div>
      </div>
    </aside>
  )
}
