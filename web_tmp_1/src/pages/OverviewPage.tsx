import { useMemo } from 'react';
import { Wifi, Clock, WifiOff, Droplets, AlertTriangle, ShieldCheck, ChevronRight, AlertTriangle as AlertIcon, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { demoReadings, demoSummary, getRiskLevel, getRiskLabel, getRiskColor, getStatusText, getSignalLabel, demoDeviceHistory } from '../data/demoReadings';
import type { DeviceReading, DeviceHistoryPoint } from '../types/domain';

function KpiCard({ title, value, subtitle, icon, iconBg, iconColor }: {
  title: string; value: string | number; subtitle: string;
  icon: React.ReactNode; iconBg: string; iconColor: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-5 flex flex-col gap-3 flex-1">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[#475569]">{title}</span>
        <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ backgroundColor: iconBg }}>
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-[32px] font-bold" style={{ color: iconColor }}>{value}</span>
        <span className="text-sm text-[#64748B]">{subtitle}</span>
      </div>
      <span className="text-xs text-[#64748B]">{subtitle}</span>
    </div>
  );
}

function SystemStatusPanel() {
  return (
    <div className="bg-white rounded-2xl p-6 flex flex-col gap-4 flex-1">
      <h3 className="text-base font-bold text-[#0F172A]">系统状态</h3>
      <div className="flex flex-col items-center gap-2 py-5">
        <ShieldCheck size={56} className="text-[#22C55E]" />
        <span className="text-[22px] font-bold text-[#22C55E]">运行正常</span>
        <span className="text-xs text-[#64748B]">所有系统功能正常运行</span>
      </div>
      <div className="flex gap-3 justify-center">
        {[
          { label: '数据采集', status: '正常', color: '#22C55E' },
          { label: '数据传输', status: '正常', color: '#22C55E' },
        ].map((item) => (
          <div key={item.label} className="flex flex-col items-center gap-1.5 flex-1">
            <span className="text-xs text-[#475569]">{item.label}</span>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-xs" style={{ color: item.color }}>{item.status}</span>
            </div>
          </div>
        ))}
        <div className="flex flex-col items-center gap-1.5 flex-1">
          <span className="text-xs text-[#475569]">设备在线率</span>
          <span className="text-xl font-bold text-[#0F172A]">
            {Math.round((demoSummary.onlineDevices / demoSummary.totalDevices) * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
}

function AlertSummaryPanel() {
  const alerts = [
    { label: '高风险告警', count: demoReadings.filter(r => getRiskLevel(r.toxinUgL) === 'critical').length, color: '#EF4444', bg: '#EF44441A', icon: AlertTriangle },
    { label: '警戒告警', count: demoReadings.filter(r => getRiskLevel(r.toxinUgL) === 'warning').length, color: '#FF7A00', bg: '#FF7A001A', icon: AlertTriangle },
    { label: '关注告警', count: demoReadings.filter(r => getRiskLevel(r.toxinUgL) === 'watch').length, color: '#EAB308', bg: '#EAB3081A', icon: AlertTriangle },
    { label: '设备离线', count: demoReadings.filter(r => r.status === 'offline').length, color: '#06B6D4', bg: '#06B6D41A', icon: Info },
  ];

  return (
    <div className="bg-white rounded-2xl p-6 flex flex-col gap-3 flex-1">
      <h3 className="text-base font-bold text-[#0F172A]">告警摘要</h3>
      {alerts.map((alert) => (
        <div key={alert.label} className="flex items-center gap-3 h-[52px] px-4 rounded-lg bg-[#F8FAFC]">
          <div className="w-8 h-8 rounded-2xl flex items-center justify-center" style={{ backgroundColor: alert.bg }}>
            <alert.icon size={16} style={{ color: alert.color }} />
          </div>
          <span className="text-sm text-[#0F172A] flex-1">{alert.label}</span>
          <span className="text-lg font-bold" style={{ color: alert.color }}>{alert.count}</span>
          <ChevronRight size={16} className="text-[#64748B]" />
        </div>
      ))}
    </div>
  );
}

function TrendOverview() {
  const chartData = useMemo(() => {
    const firstDevice = demoReadings.find(r => r.status !== 'offline');
    if (!firstDevice) return [];
    const history = demoDeviceHistory[firstDevice.id] ?? [];
    return history.slice(-12).map((p: DeviceHistoryPoint) => ({
      time: p.time.slice(5, 16),
      toxin: p.toxinUgL,
    }));
  }, []);

  const avg = chartData.length > 0 ? chartData.reduce((s, d) => s + d.toxin, 0) / chartData.length : 0;

  return (
    <div className="bg-white rounded-2xl p-6 flex flex-col gap-4 flex-1">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-[#0F172A]">趋势概览（平均藻毒素）</h3>
        <div className="flex items-center gap-2 h-8 px-3 rounded-lg border border-[#E2E8F0] text-xs text-[#0F172A]">
          近7天 <ChevronRight size={14} className="text-[#64748B] rotate-90" />
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 'auto']} tick={{ fontSize: 10, fill: '#64748B' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', fontSize: 12 }}
              formatter={(value: number) => [`${value.toFixed(2)} µg/L`, '藻毒素']}
            />
            <Line type="monotone" dataKey="toxin" stroke="#1A73E8" strokeWidth={3} dot={{ fill: '#FFFFFF', stroke: '#1A73E8', strokeWidth: 2, r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="text-right">
        <span className="text-xs font-bold text-[#1A73E8]">{avg.toFixed(2)}</span>
      </div>
    </div>
  );
}

function LatestReadingsTable() {
  const readings = [...demoReadings].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 5);
  const columns = ['设备名称', '采样时间', '藻毒素 (µg/L)', '电量', '信号强度', '状态', '位置'];

  return (
    <div className="bg-white rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-[#0F172A]">最新采样（近5条）</h3>
        <span className="text-sm text-[#1A73E8] cursor-pointer">查看全部</span>
      </div>
      {/* Header */}
      <div className="flex items-center h-11 bg-[#F8FAFC] rounded-lg px-4 mb-0">
        {columns.map((col, i) => (
          <span key={col} className="text-xs text-[#475569]" style={{ width: i === 0 ? 180 : i === 1 ? 160 : i === 2 ? 120 : i === 3 ? 80 : i === 4 ? 90 : i === 5 ? 100 : 'auto', flexShrink: 0 }}>
            {col}
          </span>
        ))}
      </div>
      {/* Rows */}
      {readings.map((r: DeviceReading) => {
        const risk = getRiskLevel(r.toxinUgL);
        const riskColor = getRiskColor(r.toxinUgL);
        return (
          <div key={r.id} className="flex items-center h-12 border-b border-[#F1F5F9] last:border-0 px-4">
            <div className="flex items-center gap-2" style={{ width: 180, flexShrink: 0 }}>
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: riskColor }} />
              <span className="text-[13px] text-[#0F172A]">{r.name}</span>
            </div>
            <span className="text-[13px] text-[#475569]" style={{ width: 160, flexShrink: 0 }}>{r.updatedAt}</span>
            <span className="text-[13px] font-bold" style={{ color: riskColor, width: 120, flexShrink: 0 }}>{r.toxinUgL.toFixed(2)}</span>
            <span className="text-[13px] text-[#475569]" style={{ width: 80, flexShrink: 0 }}>{r.batteryPercent}%</span>
            <span className="text-[13px] text-[#475569]" style={{ width: 90, flexShrink: 0 }}>{r.signalDbm} dBm</span>
            <div style={{ width: 100, flexShrink: 0 }}>
              <span className="text-[13px]" style={{ color: riskColor }}>{getRiskLabel(r.toxinUgL)}</span>
            </div>
            <span className="text-[13px] text-[#475569]" style={{ flex: 1 }}>{r.locationLabel}</span>
          </div>
        );
      })}
    </div>
  );
}

export default function OverviewPage() {
  return (
    <div className="flex flex-col gap-5">
      {/* KPI Row */}
      <div className="flex gap-5 h-[140px]">
        <KpiCard
          title="在线设备" value={demoSummary.onlineDevices} subtitle={`/ ${demoSummary.totalDevices} 台`}
          icon={<Wifi size={20} color="#22C55E" />} iconBg="#22C55E1A" iconColor="#22C55E"
        />
        <KpiCard
          title="空闲设备" value={demoSummary.idleDevices} subtitle="等待指令中"
          icon={<Clock size={20} color="#F59E0B" />} iconBg="#F59E0B1A" iconColor="#F59E0B"
        />
        <KpiCard
          title="离线设备" value={demoSummary.offlineDevices} subtitle="需人工检查"
          icon={<WifiOff size={20} color="#94A3B8" />} iconBg="#94A3B81A" iconColor="#94A3B8"
        />
        <KpiCard
          title="平均藻毒素" value={demoSummary.averageToxinUgL.toFixed(2)} subtitle="µg/L"
          icon={<Droplets size={20} color="#1A73E8" />} iconBg="#1A73E81A" iconColor="#1A73E8"
        />
        <KpiCard
          title="最高风险" value={demoSummary.maxToxinReading?.toxinUgL.toFixed(2) ?? '--'} subtitle="µg/L"
          icon={<AlertTriangle size={20} color="#EF4444" />} iconBg="#EF44441A" iconColor="#EF4444"
        />
      </div>

      {/* Middle Row */}
      <div className="flex gap-5 h-[360px]">
        <SystemStatusPanel />
        <AlertSummaryPanel />
        <TrendOverview />
      </div>

      {/* Table */}
      <LatestReadingsTable />
    </div>
  );
}
