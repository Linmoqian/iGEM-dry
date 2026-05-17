import {
  demoReadings,
  demoSummary,
  getRiskColor,
  getRiskLabel,
  getSignalLabel,
} from '../lib/demoReadings';
import ToxinPredictionModel from '../components/ToxinPredictionModel';

export default function DataPage() {
  const rankedReadings = [...demoReadings].sort((a, b) => b.toxinUgL - a.toxinUgL);
  const average = demoSummary.averageToxinUgL;

  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-8 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-teal-500/20 blur-[60px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500 mb-3 drop-shadow-[0_0_8px_rgba(45,212,191,0.3)]">
          水质数据分析
        </h1>
        <p className="text-lg text-slate-400 font-medium">
          藻毒素浓度、电量和信号质量的采样汇总
        </p>
      </div>

      <div className="w-full max-w-7xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
            <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">平均藻毒素</p>
            <p className="text-3xl font-black text-cyan-300">{average.toFixed(2)}<span className="text-sm text-slate-500 ml-2">µg/L</span></p>
          </div>
          <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
            <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">在线设备</p>
            <p className="text-3xl font-black text-emerald-300">{demoSummary.onlineDevices}<span className="text-sm text-slate-500 ml-2">/ {demoSummary.totalDevices}</span></p>
          </div>
          <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
            <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">低电量</p>
            <p className="text-3xl font-black text-amber-300">{demoSummary.lowBatteryDevices}<span className="text-sm text-slate-500 ml-2">台</span></p>
          </div>
          <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
            <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">弱信号</p>
            <p className="text-3xl font-black text-rose-300">{demoSummary.weakSignalDevices}<span className="text-sm text-slate-500 ml-2">台</span></p>
          </div>
        </div>

        <ToxinPredictionModel />

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
          <section className="bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 shadow-[0_16px_60px_rgba(0,0,0,0.5)] rounded-3xl p-6">
            <div className="flex items-center justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-black text-slate-100">藻毒素浓度排行</h2>
                <p className="text-sm text-slate-500 mt-1">按当前采样浓度从高到低排序</p>
              </div>
              <span className="text-xs text-slate-500 font-bold tracking-widest uppercase">µg/L</span>
            </div>

            <div className="space-y-4">
              {rankedReadings.map((reading) => {
                const color = getRiskColor(reading.toxinUgL);

                return (
                  <div key={reading.id} className="grid grid-cols-[minmax(0,1fr)_88px] gap-4 items-center">
                    <div>
                      <div className="flex items-center justify-between mb-2 gap-3">
                        <span className="text-slate-200 font-bold truncate">{reading.name}</span>
                        <span
                          className="text-[10px] font-black px-2 py-1 rounded border shrink-0"
                          style={{
                            color,
                            borderColor: `${color}66`,
                            backgroundColor: `${color}1a`,
                          }}
                        >
                          {getRiskLabel(reading.toxinUgL)}
                        </span>
                      </div>
                      <div className="h-3 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${Math.min(100, reading.toxinUgL * 16)}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                    <span className="text-right text-lg font-black text-slate-100">{reading.toxinUgL.toFixed(2)}</span>
                  </div>
                );
              })}
            </div>
          </section>

          <aside className="space-y-6">
            <section className="bg-[#0B1221]/80 border border-slate-700/50 rounded-3xl p-6">
              <h2 className="text-xl font-black text-slate-100 mb-5">设备健康</h2>
              <div className="space-y-4">
                {demoReadings.map((reading) => (
                  <div key={reading.id} className="border-b border-slate-800 last:border-b-0 pb-4 last:pb-0">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <span className="text-sm font-bold text-slate-200 truncate">{reading.name}</span>
                      <span className="text-xs text-slate-500">{reading.updatedAt}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
                      <span>电量 {reading.batteryPercent}%</span>
                      <span>信号 {getSignalLabel(reading.signalDbm)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-[#0B1221]/80 border border-slate-700/50 rounded-3xl p-6">
              <h2 className="text-xl font-black text-slate-100 mb-4">判定阈值</h2>
              <div className="space-y-3 text-sm text-slate-300">
                <p><span className="text-emerald-300 font-bold">正常</span>：低于 0.5 µg/L</p>
                <p><span className="text-yellow-300 font-bold">关注</span>：0.5 到 1.0 µg/L</p>
                <p><span className="text-orange-300 font-bold">警戒</span>：1.0 到 5.0 µg/L</p>
                <p><span className="text-rose-300 font-bold">高风险</span>：高于 5.0 µg/L</p>
              </div>
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}
