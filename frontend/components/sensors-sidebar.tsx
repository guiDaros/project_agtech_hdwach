"use client"

import { fetchSensorData } from "@/lib/api" 
import { SensorData } from "@/lib/api"
import { useEffect, useState } from "react"
import SensorDataCard from "@/components/sensor-data-card"
import WeatherForecast from "@/components/weather-forecast"
import { Thermometer, Droplets, Droplet, Sun, Waves } from "lucide-react"

export default function SensorsSidebar() {
  const [data, setData] = useState<SensorData | null>(null)
  const [isLoading, setIsLoading] = useState(true) 

  useEffect(() => {
    console.log("Sidebar montou. Buscando dados da API...")

    async function loadSensorData() {
      try {
        setIsLoading(true)
        const apiData = await fetchSensorData() 
        setData(apiData)
        console.log("Dados recebidos!", apiData)
      } catch (error) {
        console.error("Erro ao buscar dados no sidebar:", error)
        setData(null) 
      } finally {
        setIsLoading(false)
      }
    }

    loadSensorData()
  }, []) 

  return (
    <aside className="sensors-sidebar w-80 p-4 border-r overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4">Sensores Atuais</h2>
      
      {isLoading && <p className="text-muted-foreground">Carregando sensores...</p>}
      
      <div className="space-y-4">
        <SensorDataCard
          icon={<Thermometer size={20} />}
          label="Temperatura"
          value={data ? data.temperatura : null}
          unit="°C"
          colorClass="temperatura"
        />
        <SensorDataCard
          icon={<Droplet size={20} />}
          label="Umidade do Ar"
          value={data ? data.umidadeAr : null}
          unit="%"
          colorClass="umidade-ar"
        />
        <SensorDataCard
          icon={<Waves size={20} />}
          label="Umidade do Solo"
          value={data ? data.umidadeSolo : null}
          unit="%"
          colorClass="umidade-solo"
        />
        <SensorDataCard
          icon={<Sun size={20} />}
          label="Luminosidade"
          value={data ? data.luminosidade : null}
          unit="lux"
          colorClass="luminosidade"
        />
      </div>
    </aside>
  )
}