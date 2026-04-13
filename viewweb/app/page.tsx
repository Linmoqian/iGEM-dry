export default function OverviewPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-12 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[80px] -z-10 rounded-full"></div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-cyan-300 via-blue-500 to-indigo-600 mb-6 drop-shadow-sm">
          系统分析平台
        </h1>
        <p className="text-xl text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
          全面掌控设备的运行状态，并实现高级数据可视化与实时地图监控。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-7xl mt-8">
        <div className="bg-[#0f172a]/80 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.4)] hover:border-cyan-500/40 hover:shadow-[0_0_30px_rgba(34,211,238,0.15)] transition-all group overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center text-cyan-400 mb-6 border border-blue-500/30">
            <svg className="w-7 h-7 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-200 mb-2">活跃设备</h3>
          <p className="text-4xl font-black text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">24<span className="text-sm font-medium text-slate-400 ml-2">台在线</span></p>
        </div>

        <div className="bg-[#0f172a]/80 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.4)] hover:border-teal-500/40 hover:shadow-[0_0_30px_rgba(20,184,166,0.15)] transition-all group overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="w-14 h-14 rounded-2xl bg-teal-500/20 flex items-center justify-center text-teal-400 mb-6 border border-teal-500/30">
            <svg className="w-7 h-7 drop-shadow-[0_0_8px_rgba(20,184,166,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-200 mb-2">今日数据分析</h3>
          <p className="text-4xl font-black text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">12.5k<span className="text-sm font-medium text-slate-400 ml-2">采集点</span></p>
        </div>

        <div className="bg-gradient-to-br from-blue-900 via-[#1e1b4b] to-indigo-950 rounded-3xl p-8 border border-indigo-500/30 shadow-[0_8px_30px_rgb(55,48,163,0.3)] text-white relative overflow-hidden group">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
          <div className="absolute delay-75 duration-1000 opacity-30 -right-8 -top-8 w-40 h-40 bg-indigo-400 rounded-full mix-blend-overlay blur-3xl group-hover:scale-150"></div>
          <h3 className="text-xl font-bold mb-2">系统健康状态</h3>
          <p className="text-5xl font-black mt-4 drop-shadow-[0_0_12px_rgba(129,140,248,0.6)]">98%</p>
          <div className="mt-8 flex items-center text-indigo-200 text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-cyan-400 mr-2 animate-pulse shadow-[0_0_8px_rgba(34,211,238,1)]"></span>
            所有核心系统正常运行
          </div>
        </div>
      </div>
    </div>
  );
}
