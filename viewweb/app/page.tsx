import Link from 'next/link';
import { demoReadings, demoSummary, getRiskLabel } from './lib/demoReadings';

export default function OverviewPage() {
  const maxReading = demoSummary.maxToxinReading;
  const recentReadings = demoReadings.slice(0, 4);

  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-12 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[80px] -z-10 rounded-full"></div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-cyan-300 via-blue-500 to-indigo-600 mb-6 drop-shadow-sm">
          水体藻毒素监测平台
        </h1>
        <p className="text-xl text-slate-400 font-medium max-w-3xl mx-auto leading-relaxed">
          连接嵌入式采样设备，汇总电量、信号强度和藻毒素浓度，并在地图中定位风险热区。
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 w-full max-w-7xl mt-4">
        <div className="bg-[#0f172a]/80 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
          <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-3">在线设备</p>
          <p className="text-4xl font-black text-white">{demoSummary.onlineDevices}<span className="text-sm font-medium text-slate-400 ml-2">/ {demoSummary.totalDevices} 台</span></p>
          <p className="text-sm text-slate-500 mt-4">采样节点正在回传水质数据</p>
        </div>

        <div className="bg-[#0f172a]/80 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
          <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-3">平均藻毒素</p>
          <p className="text-4xl font-black text-cyan-300">{demoSummary.averageToxinUgL.toFixed(2)}<span className="text-sm font-medium text-slate-400 ml-2">µg/L</span></p>
          <p className="text-sm text-slate-500 mt-4">当前演示采样批次均值</p>
        </div>

        <div className="bg-[#0f172a]/80 backdrop-blur-xl rounded-3xl p-8 border border-slate-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.4)]">
          <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-3">最高风险</p>
          <p className="text-4xl font-black text-rose-400">{maxReading.toxinUgL.toFixed(2)}<span className="text-sm font-medium text-slate-400 ml-2">µg/L</span></p>
          <p className="text-sm text-slate-500 mt-4">{maxReading.name} · {getRiskLabel(maxReading.toxinUgL)}</p>
        </div>

        <div className="bg-gradient-to-br from-blue-900 via-[#1e1b4b] to-indigo-950 rounded-3xl p-8 border border-indigo-500/30 shadow-[0_8px_30px_rgb(55,48,163,0.3)] text-white relative overflow-hidden group">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
          <p className="text-xs text-indigo-200 font-bold tracking-widest uppercase mb-3 relative z-10">系统状态</p>
          <p className="text-4xl font-black relative z-10">{demoSummary.lowBatteryDevices + demoSummary.weakSignalDevices === 0 ? '正常' : '需关注'}</p>
          <div className="mt-5 text-sm text-indigo-200 relative z-10">
            低电量 {demoSummary.lowBatteryDevices} 台 · 弱信号 {demoSummary.weakSignalDevices} 台
          </div>
        </div>
      </div>

      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6 mt-8">
        <section className="bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-[0_16px_60px_rgba(0,0,0,0.35)]">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
            <div>
              <h2 className="text-2xl font-black text-slate-100">最新采样</h2>
              <p className="text-sm text-slate-500 mt-2">设备端回传的藻毒素浓度、电量和信号质量</p>
            </div>
            <Link
              href="/map"
              className="self-start md:self-auto px-5 py-3 rounded-lg bg-cyan-500/10 border border-cyan-500/40 text-cyan-300 text-sm font-bold hover:bg-cyan-500/20 transition-colors"
            >
              查看热力图
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentReadings.map((reading) => (
              <div key={reading.id} className="rounded-2xl border border-slate-800 bg-[#050B14]/50 p-5">
                <div className="flex items-center justify-between gap-3 mb-4">
                  <h3 className="font-black text-slate-100 truncate">{reading.name}</h3>
                  <span className="text-xs text-slate-500">{reading.updatedAt}</span>
                </div>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-slate-500 text-xs mb-1">藻毒素</p>
                    <p className="font-black text-cyan-300">{reading.toxinUgL.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">电量</p>
                    <p className="font-black text-slate-200">{reading.batteryPercent}%</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">信号</p>
                    <p className="font-black text-slate-200">{reading.signalDbm}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <aside className="bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-[0_16px_60px_rgba(0,0,0,0.35)]">
          <h2 className="text-2xl font-black text-slate-100 mb-6">风险说明</h2>
          <div className="space-y-5 text-sm text-slate-300">
            <p>当前演示数据以 µg/L 表示藻毒素浓度，热力图会按浓度归一化显示污染强度。</p>
            <p>设备电量低于 20% 或信号低于 -85 dBm 时，会进入维护关注范围。</p>
            <p>第一版使用模拟数据，后续可替换为蓝牙、Wi-Fi 或后端 API 的真实采样流。</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
