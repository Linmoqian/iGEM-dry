'use client';

import { useMemo, useState } from 'react';
import {
  DeviceHistoryPoint,
  demoReadings,
  demoLake,
  demoSummary,
  getDeviceHistory,
  getRiskColor,
  getRiskLabel,
  getSignalLabel,
} from '../lib/demoReadings';
import MapClientLoader from './MapClientLoader';

interface MetricChartProps {
  title: string;
  unit: string;
  color: string;
  points: DeviceHistoryPoint[];
  valueKey: keyof Pick<DeviceHistoryPoint, 'toxinUgL' | 'waterTempC' | 'ph' | 'batteryPercent' | 'signalDbm'>;
  thresholds?: { value: number; label: string; color: string }[];
}

function buildPath(values: number[], min: number, max: number, width: number, height: number): string {
  if (values.length === 0) return '';
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(' ');
}

function MetricChart({ title, unit, color, points, valueKey, thresholds = [] }: MetricChartProps) {
  const values = points.map((point) => Number(point[valueKey]));
  const rawMin = Math.min(...values, ...thresholds.map((threshold) => threshold.value));
  const rawMax = Math.max(...values, ...thresholds.map((threshold) => threshold.value));
  const padding = Math.max((rawMax - rawMin) * 0.16, valueKey === 'ph' ? 0.2 : 0.4);
  const min = rawMin - padding;
  const max = rawMax + padding;
  const width = 520;
  const height = 160;
  const path = buildPath(values, min, max, width, height);
  const latest = values[values.length - 1];
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  const peak = Math.max(...values);

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#050B14]/55 p-4">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h3 className="font-black text-slate-100">{title}</h3>
          <p className="text-xs text-slate-500 mt-1">过去 24 小时</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-black" style={{ color }}>
            {latest.toFixed(valueKey === 'batteryPercent' || valueKey === 'signalDbm' ? 0 : 2)}
            <span className="text-xs text-slate-500 ml-1">{unit}</span>
          </p>
          <p className="text-xs text-slate-500">当前值</p>
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-44 overflow-visible">
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line
            key={ratio}
            x1="0"
            x2={width}
            y1={height * ratio}
            y2={height * ratio}
            stroke="#1e293b"
            strokeWidth="1"
          />
        ))}

        {thresholds.map((threshold) => {
          const y = height - ((threshold.value - min) / (max - min || 1)) * height;
          return (
            <g key={threshold.label}>
              <line
                x1="0"
                x2={width}
                y1={y}
                y2={y}
                stroke={threshold.color}
                strokeDasharray="6 7"
                strokeWidth="1.5"
                opacity="0.85"
              />
              <text x={width - 4} y={Math.max(12, y - 5)} fill={threshold.color} fontSize="12" textAnchor="end">
                {threshold.label}
              </text>
            </g>
          );
        })}

        <path d={path} fill="none" stroke="rgba(15,23,42,0.9)" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
        <path d={path} fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />

        {values.map((value, index) => {
          if (index % 4 !== 0 && index !== values.length - 1) return null;
          const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
          const y = height - ((value - min) / (max - min || 1)) * height;
          return <circle key={`${points[index].time}-${value}`} cx={x} cy={y} r="4" fill={color} stroke="#020617" strokeWidth="2" />;
        })}
      </svg>

      <div className="grid grid-cols-3 gap-3 text-xs text-slate-400 mt-3">
        <span>峰值 <strong className="text-slate-100">{peak.toFixed(2)} {unit}</strong></span>
        <span>均值 <strong className="text-slate-100">{average.toFixed(2)} {unit}</strong></span>
        <span>范围 <strong className="text-slate-100">{points[0]?.time} - {points[points.length - 1]?.time}</strong></span>
      </div>
    </div>
  );
}

export default function MapDashboard() {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
  const selectedReading = useMemo(
    () => demoReadings.find((reading) => reading.id === selectedDeviceId) ?? null,
    [selectedDeviceId]
  );
  const history = selectedReading ? getDeviceHistory(selectedReading.id) : [];
  const maxReading = demoSummary.maxToxinReading;

  return (
    <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6 items-start">
      <div className="h-[640px] bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 shadow-[0_16px_60px_rgba(0,0,0,0.5)] rounded-3xl p-4 relative overflow-hidden hover:border-cyan-500/30 transition-colors">
        <div className="absolute inset-0 m-4 rounded-2xl overflow-hidden border border-slate-800">
          <MapClientLoader
            readings={demoReadings}
            selectedDeviceId={selectedDeviceId}
            onSelectDevice={setSelectedDeviceId}
          />
        </div>
      </div>

      <aside className="space-y-4">
        {selectedReading ? (
          <>
            <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)]">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">历史采样</p>
                  <h2 className="text-xl font-black text-slate-100">{selectedReading.name}</h2>
                  <p className="text-sm text-slate-400 mt-1">{selectedReading.locationLabel}</p>
                </div>
                <button
                  onClick={() => setSelectedDeviceId(null)}
                  className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-bold text-slate-300 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
                >
                  返回总览
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-[#050B14]/60 border border-slate-800 p-3">
                  <p className="text-xs text-slate-500 mb-1">当前浓度</p>
                  <p className="font-black" style={{ color: getRiskColor(selectedReading.toxinUgL) }}>
                    {selectedReading.toxinUgL.toFixed(2)} µg/L
                  </p>
                </div>
                <div className="rounded-xl bg-[#050B14]/60 border border-slate-800 p-3">
                  <p className="text-xs text-slate-500 mb-1">风险等级</p>
                  <p className="font-black text-slate-100">{getRiskLabel(selectedReading.toxinUgL)}</p>
                </div>
                <div className="rounded-xl bg-[#050B14]/60 border border-slate-800 p-3">
                  <p className="text-xs text-slate-500 mb-1">电量</p>
                  <p className="font-black text-slate-100">{selectedReading.batteryPercent}%</p>
                </div>
                <div className="rounded-xl bg-[#050B14]/60 border border-slate-800 p-3">
                  <p className="text-xs text-slate-500 mb-1">信号</p>
                  <p className="font-black text-slate-100">{selectedReading.signalDbm} dBm · {getSignalLabel(selectedReading.signalDbm)}</p>
                </div>
              </div>
            </div>

            <MetricChart
              title="藻毒素浓度变化"
              unit="µg/L"
              color={getRiskColor(selectedReading.toxinUgL)}
              points={history}
              valueKey="toxinUgL"
              thresholds={[
                { value: 1, label: '警戒 1.0', color: '#fb923c' },
                { value: 5, label: '高风险 5.0', color: '#f43f5e' },
              ]}
            />

            <div className="grid grid-cols-1 gap-4">
              <MetricChart title="水温变化" unit="°C" color="#38bdf8" points={history} valueKey="waterTempC" />
              <MetricChart title="pH 变化" unit="" color="#a78bfa" points={history} valueKey="ph" />
            </div>
          </>
        ) : (
          <>
            <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5 shadow-[0_12px_40px_rgba(0,0,0,0.35)]">
              <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">演示水域</p>
              <h2 className="text-xl font-black text-slate-100 mb-1">{demoLake.name}</h2>
              <p className="text-sm text-slate-400 mb-4">{demoLake.description}</p>
              <p className="text-xs text-slate-500 mb-5">绿色区域为陆地，蓝色圆形为湖泊，采样点用于展示设备监测分布。</p>
              <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-2">最高风险点</p>
              <h2 className="text-xl font-black text-slate-100 mb-1">{maxReading.name}</h2>
              <p className="text-sm text-slate-400 mb-4">{maxReading.locationLabel}</p>
              <p className="text-4xl font-black text-rose-400">{maxReading.toxinUgL.toFixed(2)}<span className="text-sm text-slate-500 ml-2">µg/L</span></p>
              <p className="mt-2 text-sm text-rose-300">{getRiskLabel(maxReading.toxinUgL)}</p>
            </div>

            <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
              <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-4">图例</p>
              <div className="space-y-3 text-sm text-slate-300">
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><i className="w-3 h-3 rounded-full bg-emerald-400"></i>正常</span><span>&lt; 0.5</span></div>
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><i className="w-3 h-3 rounded-full bg-yellow-400"></i>关注</span><span>0.5-1.0</span></div>
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><i className="w-3 h-3 rounded-full bg-orange-400"></i>警戒</span><span>1.0-5.0</span></div>
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><i className="w-3 h-3 rounded-full bg-rose-500"></i>高风险</span><span>&gt; 5.0</span></div>
              </div>
              <p className="text-xs text-slate-500 mt-4">单位：µg/L</p>
            </div>

            <div className="bg-[#0B1221]/80 border border-slate-700/50 rounded-2xl p-5">
              <p className="text-xs text-slate-500 font-bold tracking-widest uppercase mb-4">采样节点</p>
              <div className="space-y-3">
                {demoReadings.map((reading) => (
                  <button
                    key={reading.id}
                    type="button"
                    onClick={() => setSelectedDeviceId(reading.id)}
                    className="w-full flex items-center justify-between gap-3 text-sm text-left hover:text-cyan-300 transition-colors"
                  >
                    <span className="text-slate-300 truncate">{reading.name}</span>
                    <span className="font-bold text-cyan-300 shrink-0">{reading.toxinUgL.toFixed(2)}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
