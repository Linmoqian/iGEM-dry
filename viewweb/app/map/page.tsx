export default function MapPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700 h-full">
      <div className="text-center mb-8 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[60px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-cyan-300 to-indigo-500 mb-3 drop-shadow-sm">
          地理空间监视网
        </h1>
        <p className="text-lg text-slate-400 font-medium">
          实时位置追踪与多节点高精监控
        </p>
      </div>

      <div className="w-full max-w-7xl flex-1 min-h-[600px] bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 shadow-[0_16px_60px_rgba(0,0,0,0.5)] rounded-3xl p-4 flex flex-col relative overflow-hidden group hover:border-cyan-500/30 transition-colors">
        <div className="absolute inset-0 m-4 rounded-2xl bg-[#050714] overflow-hidden border border-slate-800">
          {/* Tech Radar/Map Pattern */}
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 bg-[radial-gradient(ellipse_at_center,rgba(14,165,233,0.1)_0%,transparent_70%),linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:100%_100%,32px_32px,32px_32px] relative overflow-hidden">
            <div className="absolute w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[80px]" />
            {/* Animated Radar Sweep Placeholder */}
            <div className="absolute w-[400px] h-[400px] border border-cyan-500/10 rounded-full"></div>
            <div className="absolute w-[250px] h-[250px] border border-teal-500/20 rounded-full"></div>
            <div className="absolute w-[100px] h-[100px] border border-indigo-500/30 rounded-full"></div>
            
            <svg className="w-16 h-16 mb-4 text-cyan-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.6)] relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span className="text-lg font-medium tracking-widest text-cyan-50/70 relative z-10 uppercase transition-opacity animate-pulse">地图服务阵列加载中...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
