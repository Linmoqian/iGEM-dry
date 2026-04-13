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
      case 'online': return 'bg-emerald-400 text-emerald-400';
      case 'offline': return 'bg-rose-500 text-rose-500';
      case 'idle': return 'bg-amber-400 text-amber-400';
      default: return 'bg-slate-500 text-slate-500';
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
    <div className="bg-[#0f172a]/70 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-slate-700/50 max-w-sm hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(34,211,238,0.15)] transition-all duration-300 group">
      <div className="flex justify-between items-start mb-6 border-b border-slate-700/50 pb-4">
        <div>
          <h3 className="text-xl font-bold text-slate-100 tracking-wide">{deviceName}</h3>
          <div className="flex items-center mt-1">
            <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor()} mr-2 shrink-0 animate-pulse shadow-[0_0_8px_currentColor] opacity-90`}></span>
            <span className="text-slate-400 text-sm font-medium">{getStatusText()}</span>
          </div>
        </div>
        <div className="bg-slate-800/80 p-2.5 rounded-xl border border-slate-700 shadow-inner group-hover:border-cyan-500/30 group-hover:text-cyan-400 transition-colors">
          <svg className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 drop-shadow-[0_0_8px_currentColor] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
      </div>

      <div className="space-y-5">
        {/* Location */}
        <div className="flex items-center text-slate-300">
          <div className="w-9 h-9 flex items-center justify-center bg-slate-800/80 border border-slate-700/80 rounded-lg mr-4 shadow-inner">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <p className="text-[11px] text-slate-500 font-bold tracking-widest uppercase mb-0.5">当前拓扑位置</p>
            <p className="text-sm font-semibold tracking-wide text-slate-200">{location}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Battery */}
          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80 shadow-[inset_0_2px_10px_rgba(0,0,0,0.2)] hover:border-slate-600 transition-colors">
            <div className="flex items-center mb-1.5">
              <svg className="w-4 h-4 text-emerald-400 mr-2 drop-shadow-[0_0_6px_rgba(52,211,153,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125H21M4.5 9h12a2.25 2.25 0 012.25 2.25v6.75A2.25 2.25 0 0116.5 20.25h-12A2.25 2.25 0 012.25 18v-6.75A2.25 2.25 0 014.5 9z" />
              </svg>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">储能</span>
            </div>
            <div className="flex items-baseline">
              <span className="text-xl font-black text-slate-100 tracking-tighter">{battery}</span>
              <span className="text-xs text-slate-500 ml-1 font-bold">%</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden shadow-inner">
              <div 
                className={`h-full rounded-full shadow-[0_0_8px_currentColor] ${battery < 20 ? 'bg-rose-500' : 'bg-emerald-400'}`} 
                style={{ width: `${battery}%` }}
              ></div>
            </div>
          </div>

          {/* Temperature */}
          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80 shadow-[inset_0_2px_10px_rgba(0,0,0,0.2)] hover:border-slate-600 transition-colors">
            <div className="flex items-center mb-1.5">
              <svg className="w-4 h-4 text-orange-400 mr-2 drop-shadow-[0_0_6px_rgba(251,146,60,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">核心温度</span>
            </div>
            <div className="flex items-baseline">
              <span className="text-xl font-black text-slate-100 tracking-tighter">{temperature}</span>
              <span className="text-xs text-slate-500 ml-1 font-bold">°C</span>
            </div>
            <div className="flex items-center mt-2.5">
              <span className="text-[10px] text-cyan-400 font-bold bg-cyan-950/50 border border-cyan-800/80 px-2 py-0.5 rounded shadow-[0_0_5px_rgba(34,211,238,0.2)]">核心稳定</span>
            </div>
          </div>
        </div>

        <button className="w-full mt-2 py-3 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-600 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)] rounded-xl font-bold tracking-widest transition-all duration-300 group/btn relative overflow-hidden">
          <span className="relative z-10 transition-colors uppercase text-sm">唤出详细矩阵</span>
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent -translate-x-[100%] group-hover/btn:translate-x-[100%] transition-transform duration-700"></div>
        </button>
      </div>
    </div>
  );
};

export default DeviceStatus;
