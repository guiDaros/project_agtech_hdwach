export interface SensorData {
  temperatura: number;
  umidadeAr: number;
  umidadeSolo: number;
  luminosidade: number;
  timestamp: string;
}

export interface PestRisk {
  praga: string;
  risco: number;
  status: "baixo" | "médio" | "alto";
}

export interface HistoricalData {
  timestamp: string; 
  temperatura: number;
  umidadeAr: number;
  umidadeSolo: number;
  luminosidade: number;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api";

export async function fetchSensorData(): Promise<SensorData> {
  try {
    const response = await fetch(`${API_BASE_URL}/latest`);
    if (!response.ok) throw new Error("Erro ao buscar dados dos sensores");
    const data = await response.json();

    if (data.success) {
      return data.tempo_real.dados_brutos;
    } else {
      throw new Error(data.message || "Erro ao buscar dados");
    }
  } catch (error) {
    console.error("Erro na API (fetchSensorData):", error); 
    return {
      temperatura: 28.5,
      umidadeAr: 65,
      umidadeSolo: 42,
      luminosidade: 78,
      timestamp: new Date().toISOString(),
    };
  }
}

export async function fetchHistoricalData(
  hours = 24
): Promise<HistoricalData[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/historical/${hours}`);
    if (!response.ok) throw new Error("Erro ao buscar dados históricos");
    const data = await response.json();

    if (data.success) {
      return data.historico;
    } else {
      return [];
    }
  } catch (error) {
    console.error("Erro na API (fetchHistoricalData):", error);
    return [];
  }
}

export async function fetchPestRisk(): Promise<PestRisk[]> {
  try {
    // MUDANÇA: Chamando a nova rota /api/analysis/risk
    const response = await fetch(`${API_BASE_URL}/analysis/risk`);
    
    if (!response.ok) throw new Error("Erro ao buscar risco de pragas");
    
    const data = await response.json();

    if (data.success && data.risks) {
      return data.risks;
    } else {
      return [];
    }
  } catch (error) {
    console.error("Erro na API (fetchPestRisk):", error);
    return [];
  }
}