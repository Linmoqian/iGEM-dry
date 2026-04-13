export default function MapPage() {
  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700 h-full">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-3 drop-shadow-sm">
          地图监视
        </h1>
        <p className="text-lg text-slate-500 font-medium">
          实时位置追踪与多节点监控
        </p>
      </div>

      <div className="w-full max-w-7xl flex-1 min-h-[600px] bg-white/70 backdrop-blur-2xl border border-white/50 shadow-[0_16px_60px_rgba(0,0,0,0.06)] rounded-3xl p-4 flex flex-col relative overflow-hidden">
        <div className="absolute inset-0 m-4 rounded-2xl bg-slate-100 overflow-hidden border border-slate-200/50">
          {/* Placeholder Map Pattern */}
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:24px_24px] relative">
            <div className="absolute w-64 h-64 bg-blue-100/50 rounded-full blur-[80px]" />
            <svg className="w-16 h-16 mb-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span className="text-lg font-medium">地图服务加载中...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
