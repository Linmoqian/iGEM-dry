export default function DataPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-3 drop-shadow-sm">
          数据分析
        </h1>
        <p className="text-lg text-slate-500 font-medium">
          实时传感器趋势与深度分析报告
        </p>
      </div>

      <div className="w-full max-w-7xl bg-white/70 backdrop-blur-2xl border border-white/50 shadow-[0_16px_60px_rgba(0,0,0,0.06)] rounded-3xl p-8 flex flex-col relative overflow-hidden min-h-[600px]">
        {/* Placeholder UI Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full flex-1">
          {/* Sidebar Filters */}
          <div className="col-span-1 border-r border-slate-200/60 pr-6 hidden lg:block">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-6">数据筛选</h3>
            <div className="space-y-4">
              {['环境温度', '核心处理能效', '湿度探测', '化学指标测定'].map(i => (
                <div key={i} className="flex items-center text-slate-600 font-medium hover:text-blue-600 cursor-pointer">
                  <div className="w-4 h-4 rounded border border-slate-300 mr-3 flex-shrink-0" />
                  {i}
                </div>
              ))}
            </div>
          </div>
          
          {/* Main Chart Area */}
          <div className="col-span-3 flex flex-col items-center justify-center text-slate-400">
            <svg className="w-20 h-20 mb-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            <span className="font-semibold text-xl text-slate-300">构建图表组件中...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
