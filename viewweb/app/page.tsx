export default function OverviewPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-12">
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 drop-shadow-sm">
          系统分析平台
        </h1>
        <p className="text-xl text-slate-500 font-medium max-w-2xl mx-auto leading-relaxed">
          全面掌控设备的运行状态，并实现高级数据可视化与实时地图监控。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-7xl mt-8">
        <div className="bg-white/60 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center text-blue-600 mb-6">
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">活跃设备</h3>
          <p className="text-4xl font-black text-slate-900">24<span className="text-sm font-medium text-slate-500 ml-2">台在线</span></p>
        </div>

        <div className="bg-white/60 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          <div className="w-14 h-14 rounded-2xl bg-teal-100 flex items-center justify-center text-teal-600 mb-6">
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">今日数据分析</h3>
          <p className="text-4xl font-black text-slate-900">12.5k<span className="text-sm font-medium text-slate-500 ml-2">采集点</span></p>
        </div>

        <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-3xl p-8 shadow-[0_8px_30px_rgb(37,99,235,0.25)] text-white relative overflow-hidden">
          <div className="absolute opacity-10 -right-8 -top-8 w-40 h-40 bg-white rounded-full mix-blend-overlay blur-xl"></div>
          <h3 className="text-xl font-bold mb-2">系统健康状态</h3>
          <p className="text-5xl font-black mt-4">98%</p>
          <div className="mt-8 flex items-center text-blue-100 text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse"></span>
            所有核心系统正常运行
          </div>
        </div>
      </div>
    </div>
  );
}
