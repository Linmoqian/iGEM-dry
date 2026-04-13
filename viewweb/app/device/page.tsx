import DeviceStatus from '../components/DeviceStatus';

export default function DevicePage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-3 drop-shadow-sm">
          设备配对与监控
        </h1>
        <p className="text-lg text-slate-500 font-medium">
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
        <div className="bg-white/40 backdrop-blur border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-400 hover:text-blue-500 hover:bg-white/60 hover:border-blue-300 transition-all cursor-pointer min-h-[300px]">
          <svg className="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="font-semibold tracking-wide">添加新设备</span>
        </div>
      </div>
    </div>
  );
}

