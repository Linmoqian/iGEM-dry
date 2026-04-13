import DeviceStatus from '../components/DeviceStatus';

export default function DevicePage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-12 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[80px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-500 mb-3 drop-shadow-sm">
          装备配对与监控阵列
        </h1>
        <p className="text-lg text-slate-400 font-medium">
          实时管理实验室内连接的硬件模块与传感器状态
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-6xl">
        <DeviceStatus 
          deviceName="核心处理模块-01" 
          status="online" 
          location="实验室 A-204" 
          battery={85} 
          temperature={32.4} 
        />
        
        <DeviceStatus 
          deviceName="分布式传感器-02" 
          status="idle" 
          location="走廊 3 楼 B1" 
          battery={42} 
          temperature={28.1} 
        />

        <DeviceStatus 
          deviceName="离线终端-03" 
          status="offline" 
          location="储藏室" 
          battery={12} 
          temperature={24.5} 
        />
        
        {/* Placeholder for adding more devices */}
        <div className="bg-[#0f172a]/50 backdrop-blur border border-dashed border-slate-600/50 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-400 hover:text-cyan-400 hover:bg-[#0f172a]/80 hover:border-cyan-500/50 hover:shadow-[0_0_20px_rgba(34,211,238,0.1)] transition-all cursor-pointer min-h-[300px] group">
          <svg className="w-12 h-12 mb-4 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4v16m8-8H4" />
          </svg>
          <span className="font-semibold tracking-wider text-sm">部署新设备</span>
        </div>
      </div>
    </div>
  );
}

