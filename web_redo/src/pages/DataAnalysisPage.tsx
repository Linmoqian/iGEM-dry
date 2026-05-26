import { useMemo } from 'react';
import { ChevronDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, ComposedChart, ReferenceLine } from 'recharts';
import { demoReadings, getRiskColor, demoDeviceHistory } from '../data/demoReadings';
import { generatePredictions } from '../data/mockPredictions';
import type { DeviceHistoryPoint, DeviceReading } from '../types/domain';

function TrendChart() {
  const device = demoReadings.find(r => r.status !== 'offline');
  const history = device ? (demoDeviceHistory[device.id] ?? []) : [];

  const data = history.map((p: DeviceHistoryPoint) => ({
    time: p.time.slice(5, 16),
    toxin: p.toxinUgL,
    temp: p.waterTempC,
    ph: p.ph,
  }));

  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 flex-1" style={{ height: 440 }}>
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-[#0F172A]">趋势分析</h3>
        <div className="flex items-center gap-5">
          {[
            { color: '#1A73E8', label: '藻毒素 (µg/L)' },
            { color: '#10B981', label: '水温 (°C)' },
            { color: '#8B5CF6', label: 'pH' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <div className="w-3 h-[3px]" style={{ backgroundColor: item.color }} />
              <span className="text-[11px] text-[#475569]">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 5, right: 110, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748B' }} interval={3} />
            <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#64748B' }} domain={[0, 5]} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#10B981' }} domain={[18, 30]} />
            <YAxis yAxisId="ph" orientation="right" tick={{ fontSize: 10, fill: '#8B5CF6' }} domain={[6, 8.5]} hide />
            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', fontSize: 12 }} />
            <ReferenceLine yAxisId="left" y={5} stroke="#EF4444" strokeDasharray="4 4" label={{ value: '高风险阈值 (5.0 µg/L)', fill: '#EF4444', fontSize: 10, position: 'insideRight', dy: 10 }} />
            <ReferenceLine yAxisId="left" y={1} stroke="#FF7A00" strokeDasharray="4 4" label={{ value: '警戒阈值 (1.0 µg/L)', fill: '#FF7A00', fontSize: 10, position: 'insideRight', dy: -8 }} />
            <Line yAxisId="left" type="monotone" dataKey="toxin" stroke="#1A73E8" strokeWidth={2} dot={{ fill: '#FFFFFF', stroke: '#1A73E8', strokeWidth: 1.5, r: 3 }} />
            <Line yAxisId="right" type="monotone" dataKey="temp" stroke="#10B981" strokeWidth={2} dot={{ fill: '#FFFFFF', stroke: '#10B981', strokeWidth: 1.5, r: 3 }} />
            <Line yAxisId="ph" type="monotone" dataKey="ph" stroke="#8B5CF6" strokeWidth={2} dot={{ fill: '#FFFFFF', stroke: '#8B5CF6', strokeWidth: 1.5, r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function SensorComparison() {
  const sorted = [...demoReadings]
    .filter(r => r.status !== 'offline')
    .sort((a, b) => b.toxinUgL - a.toxinUgL)
    .slice(0, 5);

  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 flex-shrink-0" style={{ height: 440, width: 400 }}>
      <h3 className="text-base font-bold text-[#0F172A]">传感器对比</h3>
      <div className="flex justify-between text-xs text-[#64748B]">
        <span>藻毒素 (µg/L)</span>
        <span>最新值 (单位)</span>
      </div>
      {sorted.map((device: DeviceReading) => (
        <div key={device.id} className="flex items-center justify-between" style={{ padding: '12px 0' }}>
          <div className="flex items-center gap-2.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getRiskColor(device.toxinUgL) }} />
            <span className="text-sm text-[#475569]">{device.name}</span>
          </div>
          <span className="text-lg font-bold" style={{ color: getRiskColor(device.toxinUgL) }}>
            {device.toxinUgL.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
}

function AIPredictionCard() {
  const predictions = useMemo(() => generatePredictions(), []);

  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 flex-1" style={{ height: 460 }}>
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-[#0F172A]">AI 预测（藻毒素浓度）</h3>
        <div className="flex items-center gap-1.5 h-8 px-3 rounded-lg border border-[#E2E8F0] text-xs text-[#475569]">
          预测未来 7 天 <ChevronDown size={14} className="text-[#64748B]" />
        </div>
      </div>
      {/* Legend */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-[3px]" style={{ backgroundColor: '#1A73E8' }} />
          <span className="text-[11px] text-[#475569]">历史数据</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-0 border-t-2 border-dashed border-[#1A73E8]" />
          <span className="text-[11px] text-[#475569]">预测值</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-2" style={{ backgroundColor: '#1A73E81F' }} />
          <span className="text-[11px] text-[#475569]">置信区间 (95%)</span>
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={predictions}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#64748B' }} interval={1} />
            <YAxis tick={{ fontSize: 10, fill: '#64748B' }} domain={[0, 6]} />
            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', fontSize: 12 }} />
            <Area dataKey="upperBound" stroke="none" fill="#1A73E81F" />
            <Area dataKey="lowerBound" stroke="none" fill="#FFFFFF" />
            {/* Historical solid line */}
            <Line
              dataKey="value"
              stroke="#1A73E8"
              strokeWidth={2}
              dot={false}
              connectNulls
              activeDot={{ fill: '#1A73E8', r: 3 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function AIMetricsCard() {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col flex-shrink-0" style={{ height: 460, width: 400, gap: 20 }}>
      <div className="flex flex-col" style={{ height: 50 }}>
        <span className="text-sm text-[#64748B]">模型置信度</span>
        <span className="text-[38px] font-extrabold text-[#1A73E8] leading-none">87%</span>
      </div>
      <div className="h-px bg-[#F1F5F9]" />
      <div className="flex flex-col gap-1">
        <span className="text-sm text-[#64748B]">预测区间 (95%)</span>
        <div style={{ height: 30, width: 100 }} />
        <div className="flex items-baseline gap-1">
          <span className="text-[20px] font-bold text-[#0F172A]">0.45 - 3.20</span>
          <span className="text-sm text-[#475569]">µg/L</span>
        </div>
      </div>
      <div className="h-px bg-[#F1F5F9]" />
      <div className="flex flex-col gap-1">
        <span className="text-sm text-[#64748B]">下一高风险时间</span>
        <span className="text-[20px] font-bold text-[#0F172A]">5月29日</span>
      </div>
    </div>
  );
}

export default function DataAnalysisPage() {
  return (
    <div className="flex flex-col gap-5">
      {/* Top Row */}
      <div className="flex gap-5" style={{ height: 440 }}>
        <TrendChart />
        <SensorComparison />
      </div>

      {/* Bottom Row */}
      <div className="flex gap-5" style={{ height: 460 }}>
        <AIPredictionCard />
        <AIMetricsCard />
      </div>
    </div>
  );
}
