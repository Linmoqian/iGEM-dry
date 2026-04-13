export default function DataPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-8 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-teal-500/20 blur-[60px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500 mb-3 drop-shadow-[0_0_8px_rgba(45,212,191,0.3)]">
          高级数据中枢
        </h1>
        <p className="text-lg text-slate-400 font-medium">
          实时传感器趋势预测与深度拓扑分析
        </p>
      </div>

      <div className="w-full max-w-7xl bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 shadow-[0_16px_60px_rgba(0,0,0,0.5)] hover:border-teal-500/30 transition-colors rounded-3xl p-8 flex flex-col relative overflow-hidden min-h-[600px]">
        {/* Decorative elements */}
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-teal-500/10 blur-3xl rounded-full"></div>
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-blue-500/10 blur-3xl rounded-full"></div>

        {/* Placeholder UI Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full flex-1 relative z-10">
          {/* Sidebar Filters */}
          <div className="col-span-1 border-r border-slate-700/60 pr-6 hidden lg:block">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-6 flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-2 shadow-[0_0_8px_rgba(34,211,238,0.8)]"></span>
              数据流筛选
            </h3>
            <div className="space-y-4">
              {['环境温度测序', '核心处理能效图', '湿度频段探测', '化学生化指标'].map(i => (
                <div key={i} className="flex items-center text-slate-400 font-medium hover:text-cyan-400 cursor-pointer group transition-colors">
                  <div className="w-4 h-4 rounded border border-slate-600 mr-3 flex-shrink-0 group-hover:border-cyan-500/50 group-hover:shadow-[0_0_8px_rgba(34,211,238,0.2)] bg-slate-800/50" />
                  {i}
                </div>
              ))}
            </div>
          </div>
          
          {/* Main Chart Area */}
          <div className="col-span-3 flex flex-col items-center justify-center text-slate-500">
            <svg className="w-20 h-20 mb-6 text-slate-700 drop-shadow-md" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            <span className="font-medium tracking-widest text-lg text-slate-500 uppercase">构建预测模型图表组件中...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
