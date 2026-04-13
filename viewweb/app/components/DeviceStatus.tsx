import React from 'react';

interface DeviceStatusProps {
  deviceName: string;
  status: 'online' | 'offline' | 'idle';
  location: string;
  battery: number;
  temperature: number;
}

const DeviceStatus: React.FC<DeviceStatusProps> = ({
  deviceName,
  status,
  location,
  battery,
  temperature
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-red-500';
      case 'idle': return 'bg-amber-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'online': return '正在作业';
      case 'offline': return '离线';
      case 'idle': return '空闲';
      default: return '未知';
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-gray-100 max-w-sm">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-800">{deviceName}</h3>
          <div className="flex items-center mt-1">
            <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor()} mr-2 shrink-0 animate-pulse`}></span>
            <span className="text-gray-500 text-sm font-medium">{getStatusText()}</span>
          </div>
        </div>
        <div className="bg-blue-50 p-2 rounded-xl">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
      </div>

      <div className="space-y-4">
        {/* Location */}
        <div className="flex items-center text-gray-600">
          <div className="w-8 h-8 flex items-center justify-center bg-gray-50 rounded-lg mr-3">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <p className="text-xs text-gray-400 font-medium">当前位置</p>
            <p className="text-sm font-semibold">{location}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Battery */}
          <div className="bg-gray-50/50 rounded-xl p-3 border border-gray-100/50">
            <div className="flex items-center mb-1">
              <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125H21M4.5 9h12a2.25 2.25 0 012.25 2.25v6.75A2.25 2.25 0 0116.5 20.25h-12A2.25 2.25 0 012.25 18v-6.75A2.25 2.25 0 014.5 9z" />
              </svg>
              <span className="text-xs text-gray-400 font-medium font-sans">电量</span>
            </div>
            <div className="flex items-baseline">
              <span className="text-lg font-bold text-gray-800">{battery}</span>
              <span className="text-xs text-gray-500 ml-0.5">%</span>
            </div>
            <div className="w-full bg-gray-200 h-1.5 rounded-full mt-2 overflow-hidden">
              <div 
                className={`h-full rounded-full ${battery < 20 ? 'bg-red-500' : 'bg-green-500'}`} 
                style={{ width: `${battery}%` }}
              ></div>
            </div>
          </div>

          {/* Temperature */}
          <div className="bg-gray-50/50 rounded-xl p-3 border border-gray-100/50">
            <div className="flex items-center mb-1">
              <svg className="w-4 h-4 text-orange-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="text-xs text-gray-400 font-medium font-sans">核心温度</span>
            </div>
            <div className="flex items-baseline">
              <span className="text-lg font-bold text-gray-800">{temperature}</span>
              <span className="text-xs text-gray-500 ml-0.5">°C</span>
            </div>
            <div className="flex items-center mt-2">
              <span className="text-[10px] text-gray-400 font-medium bg-gray-100 px-1.5 py-0.5 rounded">正常</span>
            </div>
          </div>
        </div>

        <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white rounded-xl font-bold transition-all duration-200 shadow-md shadow-blue-100 mt-2">
          查看详细视图
        </button>
      </div>
    </div>
  );
};

export default DeviceStatus;
