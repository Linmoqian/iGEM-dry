import type { ReactNode } from 'react';
import { AlertTriangle, Check, ChevronDown, ChevronRight, Clock3, Info, ShieldCheck, Wifi, X } from 'lucide-react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { demoReadings, demoSummary, getRiskColor, getRiskLabel, getRiskLevel } from '../data/demoReadings';
import { materials } from '../data/materials';

function KpiCard({
  title,
  value,
  unit,
  desc,
  color,
  icon,
  iconBg,
}: {
  title: string;
  value: string | number;
  unit: string;
  desc: string;
  color: string;
  icon: ReactNode;
  iconBg: string;
}) {
  return (
    <section className="aqua-panel flex min-w-0 flex-1 items-start justify-between px-7 py-4">
      <div className="flex flex-col gap-2">
        <h3 className="text-[18px] font-bold text-[#111827]">{title}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-[37px] font-black leading-none" style={{ color }}>
            {value}
          </span>
          <span className="text-[17px] font-semibold text-[#0f172a]">{unit}</span>
        </div>
        <p className="text-[16px] leading-6 text-[#1f2937]">{desc}</p>
      </div>
      <div className="flex h-[54px] w-[54px] shrink-0 items-center justify-center rounded-full" style={{ backgroundColor: iconBg }}>
        {icon}
      </div>
    </section>
  );
}

function SystemStatusPanel() {
  return (
    <section className="aqua-panel flex flex-[1.12] flex-col overflow-hidden px-7 py-5">
      <h2 className="text-[21px] font-black">系统状态</h2>
      <div className="flex flex-1 items-center gap-9">
        <div className="flex h-[98px] w-[98px] items-center justify-center rounded-[28px] bg-gradient-to-b from-[#28b86e] to-[#0b8c4a] text-white shadow-[0_10px_24px_rgba(3,133,72,0.25)]">
          <ShieldCheck size={70} strokeWidth={1.6} />
        </div>
        <div>
          <div className="text-[28px] font-black text-[#078b4f]">运行正常</div>
          <p className="mt-2 text-[16px] leading-7 text-[#1f2937]">所有系统功能正常运行</p>
        </div>
      </div>
      <div className="grid h-[82px] grid-cols-3 rounded-[12px] border border-[#c8e3f8] bg-white/72">
        {[
          ['数据采集', '正常'],
          ['数据传输', '正常'],
          ['设备在线率', `${Math.round((demoSummary.onlineDevices / demoSummary.totalDevices) * 100)}%`],
        ].map(([label, value], index) => (
          <div key={label} className={`flex flex-col justify-center gap-2 px-6 ${index > 0 ? 'border-l border-[#d6e8f6]' : ''}`}>
            <span className="text-[15px] text-[#344054]">{label}</span>
            <span className={`flex items-center gap-2 text-[19px] font-black ${index === 2 ? 'text-[#111827]' : 'text-[#078b4f]'}`}>
              {index < 2 ? <span className="h-4 w-4 rounded-full bg-[#078b4f]" /> : null}
              {value}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function AlertSummaryPanel() {
  const rows = [
    { label: '高风险告警', count: demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'critical').length, color: '#ef1919', bg: '#fff0f0', icon: AlertTriangle },
    { label: '警戒告警', count: demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'warning').length, color: '#f97316', bg: '#fff6ec', icon: AlertTriangle },
    { label: '关注告警', count: demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'watch').length, color: '#f59e0b', bg: '#fff9e8', icon: AlertTriangle },
    { label: '设备离线', count: demoSummary.offlineDevices, color: '#0874ed', bg: '#eef7ff', icon: Info },
  ];

  return (
    <section className="aqua-panel flex flex-[1.02] flex-col gap-5 overflow-hidden px-7 py-6">
      <h2 className="text-[21px] font-black">告警摘要</h2>
      <div className="flex flex-col gap-5">
        {rows.map((row) => (
          <button key={row.label} className="flex h-[52px] items-center gap-5 rounded-[12px] px-5 text-left" style={{ background: row.bg }} type="button">
            <row.icon size={27} className="shrink-0" style={{ color: row.color }} />
            <span className="flex-1 text-[18px] font-semibold">{row.label}</span>
            <span className="text-[25px] font-black" style={{ color: row.color }}>
              {row.count}
            </span>
            <ChevronRight size={24} />
          </button>
        ))}
      </div>
    </section>
  );
}

function TrendOverview() {
  const chartData = [
    { time: '05-21', value: 1.5 },
    { time: '05-22', value: 2.6 },
    { time: '05-23', value: 5.2 },
    { time: '05-24', value: 2.6 },
    { time: '05-25', value: 3.3 },
    { time: '05-26', value: 2.1 },
    { time: '05-27', value: 3.3 },
  ];

  return (
    <section className="aqua-panel flex flex-[1.55] flex-col overflow-hidden px-7 py-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-[21px] font-black">
          趋势概览 <span className="text-[16px] font-semibold text-[#344054]">（平均藻毒素）</span>
        </h2>
        <button className="flex h-10 items-center gap-5 rounded-[9px] border border-[#c6ddf2] px-5 text-[16px]" type="button">
          近 7 天 <ChevronDown size={18} />
        </button>
      </div>
      <div className="relative h-[245px]">
        <span className="absolute left-0 top-0 text-[16px] text-[#111827]">μg/L</span>
        <ResponsiveContainer width="100%" height={245}>
          <LineChart data={chartData} margin={{ top: 38, right: 18, left: 6, bottom: 8 }}>
            <CartesianGrid stroke="#cbddec" strokeDasharray="2 4" />
            <XAxis dataKey="time" tick={{ fontSize: 16, fill: '#26334d' }} tickLine={false} axisLine={{ stroke: '#cbddec' }} />
            <YAxis domain={[0.5, 5.5]} ticks={[0.5, 1.5, 2.5, 3.5, 4.5, 5.5]} tick={{ fontSize: 16, fill: '#26334d' }} tickLine={false} axisLine={{ stroke: '#cbddec' }} />
            <Tooltip formatter={(value: number) => [`${value.toFixed(2)} μg/L`, '藻毒素']} />
            <Line type="monotone" dataKey="value" stroke="#0874ed" strokeWidth={3} dot={{ r: 5, fill: '#0874ed', strokeWidth: 0 }} activeDot={{ r: 7 }} />
          </LineChart>
        </ResponsiveContainer>
        <span className="absolute right-2 top-[44%] text-[25px] font-black text-[#0874ed]">2.50</span>
      </div>
    </section>
  );
}

function LatestReadingsTable() {
  const rows = demoReadings.slice(0, 5);
  return (
    <section className="aqua-panel relative h-full px-5 py-4">
      <img className="pointer-events-none absolute -bottom-8 right-2 w-[210px] opacity-70" src={materials.waterAccent} alt="" />
      <div className="relative z-10 mb-3 flex items-center justify-between">
        <h2 className="text-[20px] font-black">最新采样（近 5 条）</h2>
        <button className="text-[17px] font-semibold text-[#0874ed]" type="button">
          查看全部
        </button>
      </div>
      <div className="relative z-10 overflow-hidden rounded-[10px] border border-[#c9e2f7] bg-white/72">
        <div className="grid h-11 grid-cols-[1.5fr_1.35fr_1.15fr_0.85fr_1fr_1fr_1.2fr] items-center px-5 text-[17px] font-semibold text-[#344054]">
          <span>设备名称</span>
          <span>采样时间</span>
          <span>藻毒素（μg/L）</span>
          <span>电量</span>
          <span>信号强度</span>
          <span>状态</span>
          <span>位置</span>
        </div>
        {rows.map((row) => (
          <div key={row.id} className="grid h-[43px] grid-cols-[1.5fr_1.35fr_1.15fr_0.85fr_1fr_1fr_1.2fr] items-center border-t border-[#e3eff8] px-5 text-[16px]">
            <span className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getRiskColor(row.toxinUgL) }} />
              {row.name}
            </span>
            <span>{row.updatedAt}</span>
            <b style={{ color: getRiskColor(row.toxinUgL) }}>{row.toxinUgL.toFixed(2)}</b>
            <span>{row.batteryPercent}%</span>
            <span>{row.signalDbm} dBm</span>
            <span className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getRiskColor(row.toxinUgL) }} />
              {getRiskLabel(row.toxinUgL)}
            </span>
            <span>{row.locationLabel}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function OverviewPage() {
  return (
    <div className="flex h-full flex-col gap-5">
      <div className="grid h-[158px] grid-cols-5 gap-5" style={{ height: 158 }}>
        <KpiCard title="在线设备" value={demoSummary.onlineDevices} unit="/ 14 台" desc="数据正常传输中" color="#078b4f" icon={<Wifi size={39} className="text-[#078b4f]" />} iconBg="#dbf7eb" />
        <KpiCard title="空闲设备" value={demoSummary.idleDevices} unit="/ 14 台" desc="设备待机中" color="#f97316" icon={<Clock3 size={39} className="text-[#f97316]" />} iconBg="#fff1e7" />
        <KpiCard title="离线设备" value={demoSummary.offlineDevices} unit="/ 14 台" desc="设备离线" color="#ef1919" icon={<X size={41} className="text-[#4b5563]" />} iconBg="#eeeeee" />
        <KpiCard title="平均藻毒素" value="2.50" unit="μg/L" desc="较昨日 -0.18 μg/L" color="#0874ed" icon={<Check size={39} className="text-[#0874ed]" />} iconBg="#e4f4ff" />
        <KpiCard title="最高风险" value="6.35" unit="μg/L" desc="藻华预警浮标-06" color="#ef1919" icon={<AlertTriangle size={39} className="text-[#ef1919]" />} iconBg="#fff0f0" />
      </div>

      <div className="grid h-[335px] grid-cols-[1.1fr_1fr_1.55fr] gap-5" style={{ height: 335 }}>
        <SystemStatusPanel />
        <AlertSummaryPanel />
        <TrendOverview />
      </div>

      <div className="min-h-0 flex-1">
        <LatestReadingsTable />
      </div>
    </div>
  );
}
