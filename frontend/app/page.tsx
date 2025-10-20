"use client"

import { useState } from "react"
import MonitoringHeader from "@/components/monitoring-header"
import SensorsSidebar from "@/components/sensors-sidebar"
import ChartsMainArea from "@/components/charts-main-area"

export default function Home() {
  const [selectedPlant, setSelectedPlant] = useState<"soja" | "milho">("soja")

  return (
    <div className="agro-monitoring-system min-h-screen flex flex-col">
      <MonitoringHeader selectedPlant={selectedPlant} onPlantChange={setSelectedPlant} />

      <div className="agro-monitoring-layout flex flex-1 overflow-hidden">
        <SensorsSidebar />
        <ChartsMainArea />
      </div>
    </div>
  )
}
