import React from 'react';
import {
  ConnectionType,
  DeviceStatus as DeviceStatusValue,
  getRiskColor,
  getRiskLabel,
  getSignalLabel,
  getStatusText,
} from '../lib/demoReadings';

export interface DeviceStatusProps {
  id?: string;
  deviceName: string;
  status: DeviceStatusValue;
  location: string;
  battery: number;
  signalDbm: number;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
  updatedAt: string;
  connectionType?: ConnectionType;
  onDetailsClick?: () => void;
  onConnectClick?: (type: 'bluetooth' | 'wifi') => void;
}

export const DeviceStatus: React.FC<DeviceStatusProps & { dragHandleProps?: React.HTMLAttributes<HTMLDivElement> }> = ({
  deviceName,
  status,
  location,
  battery,
  signalDbm,
  toxinUgL,
  waterTempC,
  ph,
  updatedAt,
  connectionType = 'none',
  onDetailsClick,
  onConnectClick,
  dragHandleProps
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'bg-emerald-400 text-emerald-400';
      case 'offline': return 'bg-rose-500 text-rose-500';
      case 'idle': return 'bg-amber-400 text-amber-400';
      default: return 'bg-slate-500 text-slate-500';
    }
  };

  const riskColor = getRiskColor(toxinUgL);
  const riskLabel = getRiskLabel(toxinUgL);
  const signalLabel = getSignalLabel(signalDbm);

  return (
    <div className="bg-[#0f172a]/70 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-slate-700/50 hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(34,211,238,0.15)] transition-all duration-300 group flex flex-col h-full relative">
      {/* Drag handle */}
      <div 
        className="absolute top-2 left-1/2 -translate-x-1/2 w-8 h-1 bg-slate-700/50 rounded-full cursor-grab active:cursor-grabbing hover:bg-cyan-500/50 transition-colors z-20"
        {...dragHandleProps}
      />

      <div className="flex justify-between items-start mb-6 border-b border-slate-700/50 pb-4 pt-2">
        <div>
          <h3 className="text-xl font-bold text-slate-100 tracking-wide">{deviceName}</h3>
          <div className="flex items-center mt-1">
            <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor()} mr-2 shrink-0 animate-pulse shadow-[0_0_8px_currentColor] opacity-90`}></span>
            <span className="text-slate-400 text-sm font-medium">{getStatusText(status)} · {updatedAt} 更新</span>
          </div>
        </div>
        <div className="flex gap-2">
          {/* Connection Type Indicator */}
          {connectionType === 'bluetooth' && (
            <div className="bg-blue-900/40 p-2 rounded-xl border border-blue-500/30 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.2)]">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7"/></svg>
            </div>
          )}
          {connectionType === 'wifi' && (
            <div className="bg-emerald-900/40 p-2 rounded-xl border border-emerald-500/30 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/></svg>
            </div>
          )}
          
          <div className="bg-slate-800/80 p-2.5 rounded-xl border border-slate-700 shadow-inner group-hover:border-cyan-500/30 group-hover:text-cyan-400 transition-colors">
            <svg className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 drop-shadow-[0_0_8px_currentColor] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="space-y-4 mb-6 flex-1">
        {/* Location */}
        <div className="flex items-center text-slate-300">
          <div className="w-9 h-9 flex items-center justify-center bg-slate-800/80 border border-slate-700/80 rounded-lg mr-4 shadow-inner">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <p className="text-[11px] text-slate-500 font-bold tracking-widest uppercase mb-0.5">水体采样位置</p>
            <p className="text-sm font-semibold tracking-wide text-slate-200">{location}</p>
          </div>
        </div>

        <div className="rounded-xl p-4 border border-slate-800/80 bg-[#050B14]/50 shadow-[inset_0_2px_10px_rgba(0,0,0,0.2)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">藻毒素浓度</span>
            <span
              className="text-[10px] font-black px-2 py-1 rounded border"
              style={{
                color: riskColor,
                borderColor: `${riskColor}66`,
                backgroundColor: `${riskColor}1a`,
              }}
            >
              {riskLabel}
            </span>
          </div>
          <div className="flex items-baseline">
            <span className="text-3xl font-black text-slate-100 tracking-tighter">{toxinUgL.toFixed(2)}</span>
            <span className="text-xs text-slate-500 ml-2 font-bold">µg/L</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden shadow-inner">
            <div
              className="h-full rounded-full shadow-[0_0_10px_currentColor]"
              style={{ width: `${Math.min(100, toxinUgL * 16)}%`, backgroundColor: riskColor, color: riskColor }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80 shadow-[inset_0_2px_10px_rgba(0,0,0,0.2)] hover:border-slate-600 transition-colors">
            <div className="flex items-center mb-1.5">
              <svg className="w-4 h-4 text-emerald-400 mr-2 drop-shadow-[0_0_6px_rgba(52,211,153,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 10.5h.375c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125H21M4.5 9h12a2.25 2.25 0 012.25 2.25v6.75A2.25 2.25 0 0116.5 20.25h-12A2.25 2.25 0 012.25 18v-6.75A2.25 2.25 0 014.5 9z" />
              </svg>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">电量</span>
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

          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80 shadow-[inset_0_2px_10px_rgba(0,0,0,0.2)] hover:border-slate-600 transition-colors">
            <div className="flex items-center mb-1.5">
              <svg className="w-4 h-4 text-cyan-400 mr-2 drop-shadow-[0_0_6px_rgba(34,211,238,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
              </svg>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">信号</span>
            </div>
            <div className="flex items-baseline">
              <span className="text-xl font-black text-slate-100 tracking-tighter">{signalDbm}</span>
              <span className="text-xs text-slate-500 ml-1 font-bold">dBm</span>
            </div>
            <div className="flex items-center mt-2.5">
              <span className="text-[10px] text-cyan-400 font-bold bg-cyan-950/50 border border-cyan-800/80 px-2 py-0.5 rounded shadow-[0_0_5px_rgba(34,211,238,0.2)]">{signalLabel}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">水温</p>
            <p className="text-lg font-black text-slate-100">{waterTempC.toFixed(1)}<span className="text-xs text-slate-500 ml-1">°C</span></p>
          </div>
          <div className="bg-[#050B14]/40 rounded-xl p-3 border border-slate-800/80">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">pH</p>
            <p className="text-lg font-black text-slate-100">{ph.toFixed(1)}</p>
          </div>
        </div>
      </div>

      <div className="mt-auto flex flex-col gap-2">
        {/* Connection Action Buttons */}
        {status === 'offline' && (
          <div className="flex gap-2 w-full mb-2">
            <button 
              onClick={() => onConnectClick?.('bluetooth')}
              className="flex-1 py-2 bg-blue-900/30 hover:bg-blue-800/50 border border-blue-500/30 hover:border-blue-400 text-blue-400 hover:text-blue-300 hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] rounded-lg font-bold tracking-widest transition-all duration-300 flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7"/></svg>
              <span className="text-xs">蓝牙连接</span>
            </button>
            <button 
              onClick={() => onConnectClick?.('wifi')}
              className="flex-1 py-2 bg-emerald-900/30 hover:bg-emerald-800/50 border border-emerald-500/30 hover:border-emerald-400 text-emerald-400 hover:text-emerald-300 hover:shadow-[0_0_15px_rgba(16,185,129,0.3)] rounded-lg font-bold tracking-widest transition-all duration-300 flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/></svg>
              <span className="text-xs">无线连接</span>
            </button>
          </div>
        )}

        <button 
          onClick={onDetailsClick}
          className="w-full py-3 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-600 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)] rounded-xl font-bold tracking-widest transition-all duration-300 group/btn relative overflow-hidden"
        >
          <span className="relative z-10 transition-colors uppercase text-sm">查看采样详情</span>
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent -translate-x-[100%] group-hover/btn:translate-x-[100%] transition-transform duration-700"></div>
        </button>
      </div>
    </div>
  );
};
