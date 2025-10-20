"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sprout } from "lucide-react"

interface MonitoringHeaderProps {
  selectedPlant: "soja" | "milho"
  onPlantChange: (plant: "soja" | "milho") => void
}

export default function MonitoringHeader({ selectedPlant, onPlantChange }: MonitoringHeaderProps) {
  return (
    <header className="monitoring-header border-b bg-card shadow-sm">
      <div className="monitoring-header__container flex items-center justify-between px-6 py-4">
        <div className="monitoring-header__branding flex items-center gap-3">
          <div className="monitoring-header__icon flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
            <Sprout className="w-7 h-7 text-primary" />
          </div>
          <h1 className="monitoring-header__title text-xl font-bold text-balance">
            Sistema de Monitoramento Inteligente de Risco de Pragas
          </h1>
        </div>

        <div className="monitoring-header__controls flex items-center gap-3">
          <span className="plant-selector__label text-sm font-medium text-muted-foreground">Cultura:</span>
          <Select value={selectedPlant} onValueChange={(value) => onPlantChange(value as "soja" | "milho")}>
            <SelectTrigger className="plant-selector__trigger w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="soja">Soja</SelectItem>
              <SelectItem value="milho">Milho</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </header>
  )
}
