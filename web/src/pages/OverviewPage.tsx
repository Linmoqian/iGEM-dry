import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  AlertTriangle,
  Check,
  ChevronDown,
  ChevronRight,
  Clock3,
  Info,
  ShieldCheck,
  Wifi,
  X,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { demoReadings, demoSummary, getRiskColor, getRiskLabel, getRiskLevel } from '../data/demoReadings';
import { materials } from '../data/materials';
import { monitoringService } from '../services/monitoringService';
import type { DemoSummary, DeviceReading } from '../types/domain';

function KpiCard({ title, value, unit, desc, color, icon, iconBg }: {
  title: string;
  value: string | number;
  unit: string;
  desc: string;
  color: string;
  icon: ReactNode;
  iconBg: string;
}) {
  return (
    <section className="aqua-panel flex min-w-0 items-start justify-between px-5 py-4">
      <div className="min-w-0">
        <h3 className="text-[16px] font-bold text-[#151d2d]">{title}</h3>
        <div className="mt-2 flex items-baseline gap-2 whitespace-nowrap">
          <span className="text-[34px] font-black leading-none" style={{ color }}>{value}</span>
          <span className="text-[14px] font-semibold">{unit}</span>
        </div>
        <p className="mt-2 truncate text-[14px] text-[#344054]" title={desc}>{desc}</p>
      </div>
      <div className="ml-2 flex h-[46px] w-[46px] shrink-0 items-center justify-center rounded-full" style={{ backgroundColor: iconBg }}>
        {icon}
      </div>
    </section>
  );
}

function SystemStatusPanel({ summary }: { summary: DemoSummary }) {
  const onlineRate = Math.round((summary.onlineDevices / Math.max(summary.totalDevices, 1)) * 100);
  return (
    <section className="aqua-panel flex min-w-0 flex-col px-6 py-5">
      <h2 className="text-[18px] font-black">系统状态</h2>
      <div className="flex min-h-0 flex-1 items-center gap-7">
        <div className="flex h-[88px] w-[88px] shrink-0 items-center justify-center rounded-[26px] bg-gradient-to-b from-[#28b86e] to-[#087e46] text-white shadow-[0_10px_24px_rgba(3,133,72,.25)]">
          <ShieldCheck size={62} strokeWidth={1.7} />
        </div>
        <div>
          <div className="text-[25px] font-black text-[#078b4f]">运行正常</div>
          <p className="mt-1 text-[14px] leading-6 text-[#344054]">数据采集、传输及告警服务均正常</p>
        </div>
      </div>
      <div className="grid h-[72px] grid-cols-3 rounded-[11px] border border-[#c8e3f8] bg-white/70">
        {[['数据采集', '正常'], ['数据传输', '正常'], ['设备在线率', `${onlineRate}%`]].map(([label, value], index) => (
          <div key={label} className={`flex flex-col justify-center gap-2 px-4 ${index ? 'border-l border-[#d6e8f6]' : ''}`}>
            <span className="text-[13px] text-[#516176]">{label}</span>
            <span className={`flex items-center gap-2 text-[17px] font-black ${index === 2 ? 'text-[#111827]' : 'text-[#078b4f]'}`}>
              {index < 2 ? <span className="h-3 w-3 rounded-full bg-[#078b4f]" /> : null}{value}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function AlertSummaryPanel({ readings, summary }: { readings: DeviceReading[]; summary: DemoSummary }) {
  const navigate = useNavigate();
  const rows = [
    { label: '高风险告警', count: readings.filter((r) => getRiskLevel(r.toxinUgL) === 'critical').length, risk: 'critical', color: '#ef232b', bg: '#fff0f0' },
    { label: '警戒告警', count: readings.filter((r) => getRiskLevel(r.toxinUgL) === 'warning').length, risk: 'warning', color: '#f97316', bg: '#fff6ec' },
    { label: '关注告警', count: readings.filter((r) => getRiskLevel(r.toxinUgL) === 'watch').length, risk: 'watch', color: '#f5a300', bg: '#fff9e8' },
    { label: '设备离线', count: summary.offlineDevices, risk: 'offline', color: '#0878e8', bg: '#eef7ff' },
  ];
  return (
    <section className="aqua-panel flex min-w-0 flex-col px-6 py-5">
      <h2 className="text-[18px] font-black">告警摘要</h2>
      <div className="mt-4 flex flex-1 flex-col justify-between gap-2">
        {rows.map((row, index) => (
          <button key={row.label} className="flex min-h-[44px] items-center gap-4 rounded-[10px] px-4 text-left transition hover:-translate-y-px hover:shadow-sm" style={{ background: row.bg }} type="button" onClick={() => navigate(`/map?risk=${row.risk}`)}>
            {index === 3 ? <Info size={22} style={{ color: row.color }} /> : <AlertTriangle size={22} style={{ color: row.color }} />}
            <span className="flex-1 text-[15px] font-semibold">{row.label}</span>
            <span className="text-[21px] font-black" style={{ color: row.color }}>{row.count}</span>
            <ChevronRight size={20} />
          </button>
        ))}
      </div>
    </section>
  );
}

const weekData = [
  { time: '05-21', value: 1.5 }, { time: '05-22', value: 2.1 }, { time: '05-23', value: 4.35 },
  { time: '05-24', value: 2.2 }, { time: '05-25', value: 2.75 }, { time: '05-26', value: 1.8 }, { time: '05-27', value: 2.5 },
];

function createTrend(days: number) {
  if (days === 7) return weekData;
  return Array.from({ length: days }, (_, index) => {
    const date = new Date(2025, 4, 28 - days + index);
    const base = 2.05 + Math.sin(index * .82) * .65 + (index % 9 === 5 ? 1.2 : 0);
    return { time: `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`, value: +Math.max(.5, base).toFixed(2) };
  });
}

function TrendOverview() {
  const [days, setDays] = useState(7);
  const chartData = useMemo(() => createTrend(days), [days]);
  return (
    <section className="aqua-panel flex min-w-0 flex-col px-5 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-[18px] font-black">趋势概览 <span className="text-[14px] font-semibold text-[#526174]">（平均藻毒素）</span></h2>
        <label className="relative">
          <select className="h-9 appearance-none rounded-[8px] border border-[#c6ddf2] bg-white pl-4 pr-9 text-[14px]" value={days} onChange={(event) => setDays(Number(event.target.value))}>
            <option value={7}>近 7 天</option><option value={14}>近 14 天</option><option value={30}>近 30 天</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-2.5" size={16} />
        </label>
      </div>
      <div className="min-h-0 flex-1 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 14, left: -14, bottom: 0 }}>
            <defs>
              <linearGradient id="overview-line-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#50a8f2" stopOpacity=".25"/><stop offset="1" stopColor="#50a8f2" stopOpacity="0"/></linearGradient>
            </defs>
            <CartesianGrid stroke="#d4e3ef" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="time" tick={{ fontSize: 12, fill: '#526174' }} tickLine={false} axisLine={{ stroke: '#caddea' }} interval={days === 30 ? 4 : days === 14 ? 1 : 0} />
            <YAxis domain={[0, 5]} tick={{ fontSize: 12, fill: '#526174' }} tickLine={false} axisLine={false} />
            <Tooltip formatter={(value: number) => [`${value.toFixed(2)} μg/L`, '平均藻毒素']} />
            <Line isAnimationActive={false} type="monotone" dataKey="value" stroke="#0878e8" strokeWidth={3} dot={days <= 14 ? { r: 4, fill: '#0878e8', strokeWidth: 0 } : false} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function LatestReadingsTable({ readings }: { readings: DeviceReading[] }) {
  const [showAll, setShowAll] = useState(false);
  const navigate = useNavigate();
  const rows = showAll ? readings : readings.slice(0, 5);
  return (
    <section className="aqua-panel relative min-h-[255px] overflow-hidden px-4 py-3">
      <img className="pointer-events-none absolute -bottom-14 right-0 w-[230px] opacity-10" src={materials.waterAccent} alt="" />
      <div className="relative z-10 mb-2 flex items-center justify-between">
        <h2 className="text-[17px] font-black">最新采样（{showAll ? `全部 ${readings.length} 条` : '近 5 条'}）</h2>
        <button className="text-[14px] font-semibold text-[#0878e8]" type="button" onClick={() => setShowAll((value) => !value)}>{showAll ? '收起' : '查看全部'}</button>
      </div>
      <div className="relative z-10 min-w-[900px] overflow-hidden rounded-[9px] border border-[#c9e2f7] bg-white/80">
        <div className="grid h-9 grid-cols-[1.5fr_1.35fr_1fr_.75fr_.9fr_.9fr_1.2fr] items-center bg-[#f5faff] px-4 text-[13px] font-semibold text-[#43536a]">
          <span>设备名称</span><span>采样时间</span><span>藻毒素（μg/L）</span><span>电量</span><span>信号强度</span><span>状态</span><span>位置</span>
        </div>
        {rows.map((row) => (
          <button key={row.id} className="grid h-9 w-full grid-cols-[1.5fr_1.35fr_1fr_.75fr_.9fr_.9fr_1.2fr] items-center border-t border-[#e3eff8] px-4 text-left text-[13px] transition hover:bg-[#f2f9ff]" type="button" onClick={() => navigate(`/map?device=${row.id}`)}>
            <span className="flex min-w-0 items-center gap-2"><span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: getRiskColor(row.toxinUgL) }} /><span className="truncate">{row.name}</span></span>
            <span>{row.updatedAt}</span><b style={{ color: getRiskColor(row.toxinUgL) }}>{row.status === 'offline' ? '--' : row.toxinUgL.toFixed(2)}</b>
            <span>{row.batteryPercent}%</span><span>{row.signalDbm} dBm</span>
            <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: getRiskColor(row.toxinUgL) }} />{getRiskLabel(row.toxinUgL)}</span>
            <span className="truncate">{row.locationLabel}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export default function OverviewPage() {
  const [readings, setReadings] = useState<DeviceReading[]>(demoReadings);
  const [summary, setSummary] = useState<DemoSummary>(demoSummary);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [nextReadings, nextSummary] = await Promise.all([monitoringService.getLatestReadings(), monitoringService.getDashboardSummary()]);
      setReadings(nextReadings); setSummary(nextSummary);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    load();
    window.addEventListener('igem:refresh', load);
    return () => window.removeEventListener('igem:refresh', load);
  }, [load]);

  const max = summary.maxToxinReading;
  return (
    <div className={`flex min-h-full flex-col gap-4 transition-opacity ${loading ? 'opacity-75' : ''}`}>
      <div className="grid min-h-[132px] grid-cols-5 gap-4">
        <KpiCard title="在线设备" value={summary.onlineDevices} unit={`/ ${summary.totalDevices} 台`} desc="数据正常传输中" color="#078b4f" icon={<Wifi size={33} className="text-[#078b4f]" />} iconBg="#dbf7eb" />
        <KpiCard title="空闲设备" value={summary.idleDevices} unit={`/ ${summary.totalDevices} 台`} desc="设备待机中" color="#f97316" icon={<Clock3 size={33} className="text-[#f97316]" />} iconBg="#fff1e7" />
        <KpiCard title="离线设备" value={summary.offlineDevices} unit={`/ ${summary.totalDevices} 台`} desc="等待重新连接" color="#b5473c" icon={<X size={34} className="text-[#526174]" />} iconBg="#eeeeee" />
        <KpiCard title="平均藻毒素" value={summary.averageToxinUgL.toFixed(2)} unit="μg/L" desc="综合在线监测点" color="#0878e8" icon={<Check size={33} className="text-[#0878e8]" />} iconBg="#e4f4ff" />
        <KpiCard title="最高风险" value={max?.toxinUgL.toFixed(2) || '--'} unit="μg/L" desc={max?.name || '暂无数据'} color="#ef232b" icon={<AlertTriangle size={33} className="text-[#ef232b]" />} iconBg="#fff0f0" />
      </div>
      <div className="grid min-h-[302px] grid-cols-[1.02fr_.94fr_1.48fr] gap-4">
        <SystemStatusPanel summary={summary} /><AlertSummaryPanel readings={readings} summary={summary} /><TrendOverview />
      </div>
      <LatestReadingsTable readings={readings} />
    </div>
  );
}
