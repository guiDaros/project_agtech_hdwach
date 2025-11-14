"use client"

import { Card } from "@/components/ui/card"
import { BarChart3, LineChartIcon, Activity, Sun } from "lucide-react"

export default function ChartsMainArea() {
  return (
    <main className="charts-main-area flex-1 p-6 overflow-y-auto bg-muted/30">
      <div className="charts-main-area__container max-w-7xl mx-auto space-y-6">
        <Card className="system-status-card p-6 border-l-4 border-primary bg-primary/5">
          <div className="system-status-card__content flex items-start gap-4">
            <div className="system-status-card__icon p-3 rounded-lg bg-primary/10">
              <Activity className="w-7 h-7 text-primary" />
            </div>
            <div className="system-status-card__text">
              <h3 className="system-status-card__title text-xl font-bold mb-1 text-primary">
                Sistema Pronto para Monitoramento
              </h3>
              <p className="system-status-card__description text-sm text-muted-foreground">
                Conecte o backend para visualizar análises de risco de pragas em tempo real.
              </p>
            </div>
          </div>
        </Card>

        <Card className="pest-probability-chart p-6 border-2 border-dashed">
          <div className="pest-probability-chart__header flex items-center gap-3 mb-4">
            <div className="pest-probability-chart__icon p-2 rounded-lg bg-primary/10">
              <BarChart3 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="pest-probability-chart__title text-lg font-bold">Probabilidade de Pragas</h3>
          </div>
          <div className="pest-probability-chart__placeholder h-[300px] flex items-center justify-center">
            <div className="text-center space-y-3">
              <div className="w-16 h-16 mx-auto rounded-lg bg-muted flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground font-medium">Aguardando dados do backend</p>
              <p className="text-sm text-muted-foreground">O gráfico será exibido aqui</p>
            </div>
          </div>
        </Card>

        <div className="sensor-charts-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="temperature-chart p-6 border-2 border-dashed border-red-200 bg-red-50/50">
            <div className="temperature-chart__header flex items-center gap-3 mb-4">
              <div className="temperature-chart__icon p-2 rounded-lg bg-red-100">
                <LineChartIcon className="w-5 h-5 text-red-600" />
              </div>
              <h3 className="temperature-chart__title text-lg font-bold text-red-600">Temperatura (24h)</h3>
            </div>
            <div className="temperature-chart__placeholder h-[250px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 mx-auto rounded-lg bg-red-100 flex items-center justify-center">
                  <LineChartIcon className="w-6 h-6 text-red-600" />
                </div>
                <p className="text-sm text-muted-foreground">Gráfico será exibido aqui</p>
              </div>
            </div>
          </Card>

          <Card className="air-humidity-chart p-6 border-2 border-dashed border-blue-200 bg-blue-50/50">
            <div className="air-humidity-chart__header flex items-center gap-3 mb-4">
              <div className="air-humidity-chart__icon p-2 rounded-lg bg-blue-100">
                <Activity className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="air-humidity-chart__title text-lg font-bold text-blue-600">Umidade do Ar (24h)</h3>
            </div>
            <div className="air-humidity-chart__placeholder h-[250px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 mx-auto rounded-lg bg-blue-100 flex items-center justify-center">
                  <Activity className="w-6 h-6 text-blue-600" />
                </div>
                <p className="text-sm text-muted-foreground">Gráfico será exibido aqui</p>
              </div>
            </div>
          </Card>

          <Card className="soil-humidity-chart p-6 border-2 border-dashed border-cyan-200 bg-cyan-50/50">
            <div className="soil-humidity-chart__header flex items-center gap-3 mb-4">
              <div className="soil-humidity-chart__icon p-2 rounded-lg bg-cyan-100">
                <LineChartIcon className="w-5 h-5 text-cyan-600" />
              </div>
              <h3 className="soil-humidity-chart__title text-lg font-bold text-cyan-600">Umidade do Solo (24h)</h3>
            </div>
            <div className="soil-humidity-chart__placeholder h-[250px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 mx-auto rounded-lg bg-cyan-100 flex items-center justify-center">
                  <LineChartIcon className="w-6 h-6 text-cyan-600" />
                </div>
                <p className="text-sm text-muted-foreground">Gráfico será exibido aqui</p>
              </div>
            </div>
          </Card>

          <Card className="luminosity-chart p-6 border-2 border-dashed border-orange-200 bg-orange-50/50">
            <div className="luminosity-chart__header flex items-center gap-3 mb-4">
              <div className="luminosity-chart__icon p-2 rounded-lg bg-orange-100">
                <Sun className="w-5 h-5 text-orange-600" />
              </div>
              <h3 className="luminosity-chart__title text-lg font-bold text-orange-600">Luminosidade (24h)</h3>
            </div>
            <div className="luminosity-chart__placeholder h-[250px] flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 mx-auto rounded-lg bg-orange-100 flex items-center justify-center">
                  <Sun className="w-6 h-6 text-orange-600" />
                </div>
                <p className="text-sm text-muted-foreground">Gráfico será exibido aqui</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}
