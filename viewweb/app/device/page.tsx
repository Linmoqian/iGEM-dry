import DeviceStatus from '../components/DeviceStatus';

export default function DevicePage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center py-32 px-16 bg-gray-50/50 min-h-screen">
      <h1 className="text-4xl font-semibold tracking-tight text-black mb-8">
        设备详情
      </h1>
      
      <div className="flex gap-8 flex-wrap justify-center">
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
      </div>

      <div className="mt-12 text-center">
        <p className="mt-4 text-lg text-neutral-500">设备连接与配对管理</p>
      </div>
    </main>
  );
}

