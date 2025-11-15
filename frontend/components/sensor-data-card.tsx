import { Card } from "@/components/ui/card"
import type { ReactNode } from "react"

interface SensorDataCardProps {
  icon: ReactNode
  label: string
  value: number | null | undefined
  unit: string
  colorClass: "temperatura" | "umidade-ar" | "umidade-solo" | "luminosidade"
}

const sensorColorConfig = {
  temperatura: {
    text: "text-red-600",
    bg: "bg-red-50",
    border: "border-red-200",
  },
  "umidade-ar": {
    text: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-200",
  },
  "umidade-solo": {
    text: "text-cyan-600",
    bg: "bg-cyan-50",
    border: "border-cyan-200",
  },
  luminosidade: {
    text: "text-orange-600",
    bg: "bg-orange-50",
    border: "border-orange-200",
  },
}

export default function SensorDataCard({ icon, label, value, unit, colorClass }: SensorDataCardProps) {
  const colors = sensorColorConfig[colorClass]

  return (
    <Card className={`sensor-data-card p-4 border-l-4 ${colors.border} hover:shadow-md transition-shadow`}>
      <div className="sensor-data-card__content flex items-start justify-between">
        <div className="sensor-data-card__info flex-1">
          <div className="sensor-data-card__header flex items-center gap-2 mb-3">
            <div className={`sensor-data-card__icon ${colors.bg} ${colors.text} p-2 rounded-lg`}>{icon}</div>
            <span className="sensor-data-card__label text-sm font-semibold text-foreground">{label}</span>
          </div>
          <div className="sensor-data-card__value flex items-baseline gap-1">

            {typeof value === 'number' ? (
              <>
                <span className={`sensor-data-card__number text-3xl font-bold ${colors.text}`}>{value.toFixed(1)}</span>
                <span className="sensor-data-card__unit text-lg font-medium text-muted-foreground">{unit}</span>
              </>
            ) : (
              <span className="sensor-data-card__placeholder text-2xl font-bold text-muted-foreground">--</span>
            )}

          </div>
        </div>
      </div>
    </Card>
  )
}