import MapDashboard from './MapDashboard';
import { demoLake } from '../lib/demoReadings';

export default function MapPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700 h-full">
      <div className="text-center mb-8 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[60px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-cyan-300 to-indigo-500 mb-3 drop-shadow-sm">
          {demoLake.name}藻毒素热力图
        </h1>
        <p className="text-lg text-slate-400 font-medium">
          {demoLake.description}，展示设备点位、藻毒素浓度和风险热区
        </p>
      </div>

      <MapDashboard />
    </div>
  );
}
