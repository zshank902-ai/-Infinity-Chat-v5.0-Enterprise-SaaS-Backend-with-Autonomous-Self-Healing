"use client";

import dynamic from "next/dynamic";
import { Cpu } from "lucide-react";

// Dynamically import the dashboard with SSR disabled from the components folder
const DynamicDashboard = dynamic(() => import("../components/Dashboard"), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-full bg-[#020617] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Cpu className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-slate-400 text-sm font-mono animate-pulse">Initializing Neural Swarm...</p>
      </div>
    </div>
  )
});

export default function DashboardPage() {
  return <DynamicDashboard />;
}
