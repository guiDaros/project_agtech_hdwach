// Arquivo preparado para integração futura com backend

export interface SensorData {
  temperatura: number
  umidadeAr: number
  umidadeSolo: number
  luminosidade: number
  timestamp: string
}

export interface PestRisk {
  praga: string
  risco: number
  status: "baixo" | "médio" | "alto"
}

export interface HistoricalData {
  hora: string
  temperatura: number
  umidadeAr: number
  umidadeSolo: number
  luminosidade: number
}

// Configuração da URL da API - substituir pela URL real
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://0.0.0.0:5000/api"

/**
 * Busca dados atuais dos sensores
 * @param plant - Tipo de planta (soja ou milho)
 */
export async function fetchSensorData(plant: "soja" | "milho"): Promise<SensorData> {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/current?plant=${plant}`)
    if (!response.ok) throw new Error("Erro ao buscar dados dos sensores")
    return await response.json()
  } catch (error) {
    console.error("Erro na API:", error)
    // Retorna dados mock em caso de erro
    return {
      temperatura: 28.5,
      umidadeAr: 65,
      umidadeSolo: 42,
      luminosidade: 78,
      timestamp: new Date().toISOString(),
    }
  }
}

/**
 * Busca dados históricos dos sensores
 * @param plant - Tipo de planta (soja ou milho)
 * @param hours - Número de horas de histórico (padrão: 24)
 */
export async function fetchHistoricalData(plant: "soja" | "milho", hours = 24): Promise<HistoricalData[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/sensors/historical?plant=${plant}&hours=${hours}`)
    if (!response.ok) throw new Error("Erro ao buscar dados históricos")
    return await response.json()
  } catch (error) {
    console.error("Erro na API:", error)
    return []
  }
}

/**
 * Busca probabilidade de pragas
 * @param plant - Tipo de planta (soja ou milho)
 */
export async function fetchPestRisk(plant: "soja" | "milho"): Promise<PestRisk[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/pests/risk?plant=${plant}`)
    if (!response.ok) throw new Error("Erro ao buscar risco de pragas")
    return await response.json()
  } catch (error) {
    console.error("Erro na API:", error)
    return []
  }
}
