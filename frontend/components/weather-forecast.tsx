"use client"

import { useEffect, useState } from "react"
import { Sun, Cloud, CloudRain, Wind } from "lucide-react" 
import { Card } from "@/components/ui/card"


export interface WeatherData {
  temperatura: number | null
  condicao: string | null 
  condicaoIcone: string | null 
  localizacao?: string
}

export default function WeatherForecast() {
  const [weatherData, setWeatherData] = useState<WeatherData>({
    temperatura: null,
    condicao: null,
    condicaoIcone: null,
    localizacao: "Carregando...",
  })

  const getWeatherIcon = () => {
    switch (weatherData.condicaoIcone) {
      case "Clear":
        return <Sun className="w-5 h-5 text-yellow-500" />
      case "Clouds":
        return <Cloud className="w-5 h-5 text-gray-500" />
      case "Rain":
      case "Drizzle":
      case "Thunderstorm":
        return <CloudRain className="w-5 h-5 text-blue-500" />
      default:
        return <Cloud className="w-5 h-5 text-primary" /> 
    }
  }

  useEffect(() => {

    const APIKey = "bf4551dbab91c24f36ac352027d6ac23"
    const cidade = "Passo Fundo"
    const link = `https://api.openweathermap.org/data/2.5/weather?q=${cidade}&appid=${APIKey}&lang=pt_br&units=metric`

    const fetchWeatherData = async () => {
      try {
        const response = await fetch(link)
        if (!response.ok) {
          throw new Error("Falha ao buscar dados do tempo")
        }
        const data = await response.json()

        setWeatherData({
          temperatura: Math.round(data.main.temp), 
          condicao: data.weather[0].description, 
          condicaoIcone: data.weather[0].main,
          localizacao: data.name, 
        })
      } catch (error) {
        console.error("Erro ao buscar dados do tempo:", error)
        setWeatherData({
          temperatura: null,
          condicao: "Erro ao carregar",
          condicaoIcone: "Error",
          localizacao: "Falha na API",
        })
      }
    }

    fetchWeatherData()

  }, [])

  return (
    <Card className="weather-forecast p-4 bg-card border-primary/20">
      <div className="weather-forecast__header mb-3">
        <div className="flex items-center gap-2 mb-1">
          {getWeatherIcon()}
          <h3 className="weather-forecast__title text-base font-semibold">
            Tempo Agora
          </h3>
        </div>
        <p className="weather-forecast__status text-xs text-muted-foreground">
          {weatherData.localizacao}
        </p>
      </div>

      <div className="weather-forecast__data grid grid-cols-1 gap-2">
        <div className="weather-forecast__item flex flex-col items-center justify-center p-2 bg-background rounded border">
          <div className="w-4 h-4 rounded-full bg-orange-500 mb-1" />
          <span className="text-xs text-muted-foreground">Temp.</span>
          <span className="text-sm font-bold">
            {weatherData.temperatura !== null
              ? `${weatherData.temperatura}°C`
              : "--"}
          </span>
        </div>

      </div>

      {weatherData.condicao && (
        <div className="weather-forecast__condition mt-3 text-center">
          <span className="text-sm text-muted-foreground capitalize">
            {weatherData.condicao}
          </span>
        </div>
      )}
    </Card>
  )
}