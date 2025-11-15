"use client";

import { Card } from "@/components/ui/card";
import {
  BarChart3,
  LineChartIcon,
  Activity,
  Sun,
  type LucideIcon,
} from "lucide-react";

import { useState, useEffect } from "react";
import {
  fetchHistoricalData,
  fetchPestRisk,
  type HistoricalData,
  type PestRisk,
} from "@/lib/api";

// --- 1. IMPORTAMOS OS COMPONENTES NOVOS ---
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  // Adicionados para o gráfico de linha:
  LineChart,
  Line,
} from "recharts";

// --- 2. ADICIONAMOS AS CORES DE 'STROKE' (TRAÇO) ---
const chartThemes = {
  red: {
    border: "border-red-200",
    bg: "bg-red-50/50",
    iconBg: "bg-red-100",
    text: "text-red-600",
    stroke: "#ef4444", // Cor do traço (hex de text-red-600)
  },
  blue: {
    border: "border-blue-200",
    bg: "bg-blue-50/50",
    iconBg: "bg-blue-100",
    text: "text-blue-600",
    stroke: "#2563eb", // Cor do traço (hex de text-blue-600)
  },
  cyan: {
    border: "border-cyan-200",
    bg: "bg-cyan-50/50",
    iconBg: "bg-cyan-100",
    text: "text-cyan-600",
    stroke: "#0891b2", // Cor do traço (hex de text-cyan-600)
  },
  orange: {
    border: "border-orange-200",
    bg: "bg-orange-50/50",
    iconBg: "bg-orange-100",
    text: "text-orange-600",
    stroke: "#ea580c", // Cor do traço (hex de text-orange-600)
  },
};

// Interface (sem mudanças)
interface SensorChartProps {
  title: string;
  Icon: LucideIcon;
  theme: keyof typeof chartThemes;
  isLoading: boolean;
  data: HistoricalData[];
  dataKey: keyof HistoricalData;
}

// ---
// 3. MUDANÇA PRINCIPAL: 'SensorChartPlaceholder' AGORA É UM GRÁFICO REAL
// ---
function SensorChartPlaceholder({
  title,
  Icon,
  theme,
  isLoading,
  data,
  dataKey,
}: SensorChartProps) {
  const colors = chartThemes[theme];
  const hasData = !isLoading && data.length > 0;

  // Função para formatar o timestamp (ex: "2025-11-15T01:30:00Z" -> "01:30")
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      // Formata para HH:MM
      return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    } catch (e) {
      return timestamp; // Retorna o original se falhar
    }
  };

  return (
    <Card
      className={`p-6 border-2 border-dashed ${colors.border} ${colors.bg}`}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg ${colors.iconBg}`}>
          <Icon className={`w-5 h-5 ${colors.text}`} />
        </div>
        <h3 className={`text-lg font-bold ${colors.text}`}>{title}</h3>
      </div>

      {/* Miolo (AGORA COM GRÁFICO DE LINHA) */}
      <div className="h-[250px] flex items-center justify-center">
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Carregando gráfico...</p>
        ) : hasData ? (
          // === AQUI ENTRA O GRÁFICO DE LINHA ===
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data} // Passa o array de histórico
              margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTimestamp} // Formata o eixo X (ex: "01:30")
                fontSize={12}
                tickMargin={5}
              />
              <YAxis 
                fontSize={12} 
                tickMargin={5}
                // Define a faixa de exibição com uma margem (ex: 5-35)
                domain={['dataMin - 5', 'dataMax + 5']} 
              />
              <Tooltip 
                labelFormatter={formatTimestamp} // Formata o label do tooltip
                // Formata o valor (ex: "25.1 Temperatura")
                formatter={(value: number, name) => [value.toFixed(1), title.split(' ')[0]]}
              />
              <Line 
                type="monotone" 
                dataKey={dataKey} // A CHAVE (ex: "temperatura")
                stroke={colors.stroke} // A COR (ex: vermelho)
                strokeWidth={2}
                dot={false} // Remove os pontos da linha
                activeDot={{ r: 6 }} // Ponto maior no hover
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          // Placeholder (se não tiver dados)
          <div className="text-center space-y-2">
            <div
              className={`w-12 h-12 mx-auto rounded-lg ${colors.iconBg} flex items-center justify-center`}
            >
              <Icon className={`w-6 h-6 ${colors.text}`} />
            </div>
            <p className="text-sm text-muted-foreground">
              Nenhum dado histórico
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}

// --- Componente Principal ---
export default function ChartsMainArea() {
  const [history, setHistory] = useState<HistoricalData[]>([]);
  const [risk, setRisk] = useState<PestRisk[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log("ChartsMainArea montou. Buscando dados dos gráficos...");

    async function loadChartData() {
      try {
        setIsLoading(true);
        const [historyData, riskData] = await Promise.all([
          fetchHistoricalData(24),
          fetchPestRisk(),
        ]);

        // 4. INVERTEMOS OS DADOS PARA O GRÁFICO (Antigo -> Novo)
        setHistory(historyData.reverse());
        setRisk(riskData);
        console.log("Dados dos gráficos recebidos!", { historyData, riskData });
      } catch (error) {
        console.error("Erro ao carregar dados dos gráficos:", error);
      } finally {
        setIsLoading(false);
      }
    }

    loadChartData();
  }, []);

  return (
    <main className="flex-1 p-6 overflow-y-auto bg-muted/30">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Card 1: Status (sem mudança) */}
        <Card className="p-6 border-l-4 border-primary bg-primary/5">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <Activity className="w-7 h-7 text-primary" />
            </div>
            <div>
              <h3 className="text-xl font-bold mb-1 text-primary">
                Sistema Pronto para Monitoramento
              </h3>
              <p className="text-sm text-muted-foreground">
                Dados sendo carregados. Sensores e gráficos aparecerão abaixo.
              </p>
            </div>
          </div>
        </Card>

        {/* Card 2: Risco de Pragas (sem mudança) */}
        <Card className="p-6 border-2 border-dashed">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <BarChart3 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg font-bold">Probabilidade de Pragas</h3>
          </div>
          <div className="h-[300px] flex items-center justify-center">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">
                Carregando riscos...
              </p>
            ) : risk.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={risk} 
                  layout="vertical" 
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} /> 
                  <XAxis
                    type="number"
                    domain={[0, 100]} 
                    tickFormatter={(value) => `${value}%`} 
                    ticks={[
                      0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70,
                      75, 80, 85, 90, 95, 100,
                    ]}
                  />
                  <YAxis
                    type="category"
                    dataKey="praga" 
                    width={100} 
                  />
                  <Tooltip
                    formatter={(value: number) => `${value.toFixed(1)}%`} 
                    cursor={{ fill: "rgba(0,0,0,0.05)" }} 
                  />
                  <Bar
                    dataKey="risco"
                    fill="#8884d8" 
                    label={{
                      position: "right",
                      formatter: (value: number) => `${value.toFixed(1)}%`,
                    }} 
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              // Placeholder
              <div className="text-center space-y-3">
                <div className="w-16 h-16 mx-auto rounded-lg bg-muted flex items-center justify-center">
                  <BarChart3 className="w-8 h-8 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground font-medium">
                  Nenhum risco detectado
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Grid dos Sensores (sem mudança, agora funciona) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SensorChartPlaceholder
            title="Temperatura (24h)"
            Icon={LineChartIcon}
            theme="red"
            isLoading={isLoading}
            data={history}
            dataKey="temperatura"
          />
          <SensorChartPlaceholder
            title="Umidade do Ar (24h)"
            Icon={Activity}
            theme="blue"
            isLoading={isLoading}
            data={history}
            dataKey="umidadeAr" 
          />
          <SensorChartPlaceholder
            title="Umidade do Solo (24h)"
            Icon={LineChartIcon}
            theme="cyan"
            isLoading={isLoading}
            data={history}
            dataKey="umidadeSolo" 
          />
          <SensorChartPlaceholder
            title="Luminosidade (24h)"
            Icon={Sun}
            theme="orange"
            isLoading={isLoading}
            data={history}
            dataKey="luminosidade"
          />
        </div>
      </div>
    </main>
  );
}