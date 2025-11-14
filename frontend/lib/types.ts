// Tipos centralizados para facilitar manutenção

export type PlantType = "soja" | "milho"

export interface SensorReading {
  id: string
  temperatura: number
  umidadeAr: number
  umidadeSolo: number
  luminosidade: number
  timestamp: Date
  plantType: PlantType
}

export interface PestAlert {
  id: string
  praga: string
  risco: number
  status: "baixo" | "médio" | "alto"
  descricao?: string
  recomendacoes?: string[]
  plantType: PlantType
}

export interface ChartDataPoint {
  hora: string
  temperatura?: number
  umidadeAr?: number
  umidadeSolo?: number
  luminosidade?: number
}

export interface WeatherForecast {
  temperatura: number
  velocidadeVento: number
  condicao: "ensolarado" | "nublado" | "chuva"
  precipitacao?: number
  localizacao: string
  timestamp: Date
}
