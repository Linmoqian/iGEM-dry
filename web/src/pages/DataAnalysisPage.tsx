import { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ChevronDown, Microscope, ShieldCheck } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { demoReadings, getRiskColor } from '../data/demoReadings';
import { monitoringService } from '../services/monitoringService';
import type { DeviceReading, PredictionPoint, TrendPoint } from '../types/domain';

function downloadCsv(trends: TrendPoint[], predictions: PredictionPoint[], deviceName: string) {
  const rows = [
    ['数据类型', '设备', '时间', '藻毒素(μg/L)', '水温(°C)', 'pH', '95%下界', '95%上界'],
    ...trends.map((item) => ['历史趋势', deviceName, item.time, item.toxinUgL, item.waterTempC, item.ph, '', '']),
    ...predictions.map((item) => [item.isPrediction ? '模型预测' : '历史浓度', deviceName, item.time, item.value, '', '', item.lowerBound, item.upperBound]),
  ];
  const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(',')).join('\r\n');
  const url = URL.createObjectURL(new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `东湖监测数据_${deviceName}_${new Date().toISOString().slice(0, 10)}.csv`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function TrendChart({ data, sensors }: { data: TrendPoint[]; sensors: string }) {
  const showWater = sensors === 'all' || sensors === 'water';
  const showPh = sensors === 'all' || sensors === 'ph';
  return (
    <section className="aqua-panel flex min-h-0 min-w-0 flex-col overflow-hidden px-5 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-[18px] font-black">趋势分析</h2>
        <div className="flex items-center gap-7 text-[13px] font-semibold">
          <span className="flex items-center gap-2 text-[#0878e8]"><i className="h-1 w-6 rounded bg-[#0878e8]" />藻毒素（μg/L）</span>
          {showWater ? <span className="flex items-center gap-2 text-[#14a58a]"><i className="h-1 w-6 rounded bg-[#14a58a]" />水温（°C）</span> : null}
          {showPh ? <span className="flex items-center gap-2 text-[#8058bd]"><i className="h-1 w-6 rounded bg-[#8058bd]" />pH</span> : null}
        </div>
      </div>
      <div className="min-h-0 flex-1 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 22, right: showPh ? 54 : 20, left: -10, bottom: 2 }}>
            <CartesianGrid stroke="#d6e3ed" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#475569' }} interval={1} tickLine={false} axisLine={{ stroke: '#c5d8e6' }} />
            <YAxis yAxisId="toxin" domain={[0, 6]} ticks={[0,1,2,3,4,5,6]} tick={{ fontSize: 11, fill: '#0878e8' }} tickLine={false} axisLine={{ stroke: '#9bc9ee' }} label={{ value: '藻毒素 μg/L', angle: 0, position: 'top', offset: 8, fill: '#0878e8', fontSize: 11 }} />
            {showWater ? <YAxis yAxisId="water" orientation="right" domain={[18, 30]} ticks={[18,21,24,27,30]} tick={{ fontSize: 11, fill: '#14a58a' }} tickLine={false} axisLine={{ stroke: '#8ed9ca' }} /> : null}
            {showPh ? <YAxis yAxisId="ph" orientation="right" domain={[6, 8.5]} ticks={[6,6.5,7,7.5,8,8.5]} tick={{ fontSize: 11, fill: '#8058bd' }} tickLine={false} axisLine={{ stroke: '#bfa8df' }} dx={showWater ? 38 : 0} /> : null}
            <Tooltip formatter={(value: number, name: string) => [value.toFixed(name === 'pH' ? 1 : 2), name]} labelFormatter={(label) => `时间：${label}`} />
            <ReferenceLine yAxisId="toxin" y={5} stroke="#ef232b" strokeDasharray="7 4" label={{ value: '高风险阈值 5.0', fill: '#ef232b', fontSize: 11, position: 'insideTopRight' }} />
            <ReferenceLine yAxisId="toxin" y={1} stroke="#f97316" strokeDasharray="7 4" label={{ value: '警戒阈值 1.0', fill: '#f97316', fontSize: 11, position: 'insideBottomRight' }} />
            <Line isAnimationActive={false} yAxisId="toxin" type="monotone" dataKey="toxinUgL" name="藻毒素 μg/L" stroke="#0878e8" strokeWidth={2.7} dot={{ r: 3.5, fill: '#0878e8', strokeWidth: 0 }} activeDot={{ r: 6 }} />
            {showWater ? <Line isAnimationActive={false} yAxisId="water" type="monotone" dataKey="waterTempC" name="水温 °C" stroke="#14a58a" strokeWidth={2.5} dot={{ r: 3.2, fill: '#14a58a', strokeWidth: 0 }} /> : null}
            {showPh ? <Line isAnimationActive={false} yAxisId="ph" type="monotone" dataKey="ph" name="pH" stroke="#8058bd" strokeWidth={2.5} dot={{ r: 3.2, fill: '#8058bd', strokeWidth: 0 }} /> : null}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function SensorComparison({ readings, selectedId, onSelect }: { readings: DeviceReading[]; selectedId: string; onSelect: (id: string) => void }) {
  return (
    <section className="aqua-panel min-h-0 overflow-auto px-5 py-4">
      <h2 className="text-[18px] font-black">传感器对比</h2>
      <div className="mt-5 flex justify-between text-[13px] text-[#526174]"><b>藻毒素（μg/L）</b><span>最新值</span></div>
      <div className="mt-3 space-y-1">
        {readings.slice(0, 7).map((device) => (
          <button key={device.id} type="button" onClick={() => onSelect(device.id)} className={`flex w-full items-center rounded-[9px] px-2 py-2.5 text-left transition hover:bg-[#f2f9ff] ${selectedId === device.id ? 'bg-[#edf7ff]' : ''}`}>
            <span className="mr-3 h-2.5 w-2.5 rounded-full" style={{ background: getRiskColor(device.toxinUgL) }} />
            <span className="min-w-0 flex-1 truncate text-[14px]">{device.name}</span>
            <b className="text-[22px]" style={{ color: getRiskColor(device.toxinUgL) }}>{device.status === 'offline' ? '--' : device.toxinUgL.toFixed(2)}</b>
          </button>
        ))}
      </div>
    </section>
  );
}

type ForecastChartPoint = PredictionPoint & { history?: number; forecast?: number; bandBase: number; bandSize: number };

function PredictionChart({ data, days, onDaysChange }: { data: PredictionPoint[]; days: number; onDaysChange: (days: number) => void }) {
  const chartData: ForecastChartPoint[] = data.map((point) => ({
    ...point,
    history: point.isPrediction ? undefined : point.value,
    forecast: point.isPrediction ? point.value : undefined,
    bandBase: point.isPrediction ? point.lowerBound : 0,
    bandSize: point.isPrediction ? point.upperBound - point.lowerBound : 0,
  }));
  const firstPrediction = chartData.find((item) => item.isPrediction)?.time;
  return (
    <section className="aqua-panel relative flex min-w-0 flex-col overflow-hidden px-5 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-[18px] font-black">AI 预测 <span className="text-[13px] font-semibold text-[#526174]">（藻毒素浓度）</span></h2>
        <label className="relative">
          <select className="h-9 appearance-none rounded-[8px] border border-[#c6ddf2] bg-white pl-4 pr-9 text-[13px]" value={days} onChange={(event) => onDaysChange(Number(event.target.value))}>
            <option value={3}>预测未来 3 天</option><option value={7}>预测未来 7 天</option><option value={14}>预测未来 14 天</option>
          </select><ChevronDown className="pointer-events-none absolute right-3 top-2.5" size={15} />
        </label>
      </div>
      <div className="mt-1 min-h-0 flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 22, right: 18, left: -10, bottom: 2 }}>
            <CartesianGrid stroke="#d6e3ed" strokeDasharray="3 4" vertical={false} />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#475569' }} tickLine={false} axisLine={{ stroke: '#c5d8e6' }} interval={days > 7 ? 1 : 0} />
            <YAxis domain={[0, 6]} tick={{ fontSize: 11, fill: '#475569' }} tickLine={false} axisLine={false} label={{ value: 'μg/L', angle: 0, position: 'top', fontSize: 11 }} />
            <Tooltip formatter={(value: number, name: string) => [`${value.toFixed(2)} μg/L`, name]} />
            <Legend verticalAlign="top" height={30} wrapperStyle={{ fontSize: 12 }} />
            <Area isAnimationActive={false} type="monotone" dataKey="bandBase" name="区间下界" stackId="confidence" stroke="none" fill="transparent" legendType="none" />
            <Area isAnimationActive={false} type="monotone" dataKey="bandSize" name="95% 置信区间" stackId="confidence" stroke="#78b8f4" strokeDasharray="4 3" fill="#b9dbfa" fillOpacity={.58} />
            <Line isAnimationActive={false} type="monotone" dataKey="history" name="历史数据" stroke="#0878e8" strokeWidth={2.8} connectNulls={false} dot={{ r: 4, fill: '#0878e8', strokeWidth: 0 }} />
            <Line isAnimationActive={false} type="monotone" dataKey="forecast" name="预测值" stroke="#0878e8" strokeWidth={2.8} strokeDasharray="7 5" connectNulls={false} dot={{ r: 3.5, fill: '#0878e8', strokeWidth: 0 }} />
            {firstPrediction ? <ReferenceLine x={firstPrediction} stroke="#89a8bf" strokeDasharray="3 4" /> : null}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <Microscope className="pointer-events-none absolute -bottom-5 -left-3 text-[#8acdf2] opacity-10" size={130} strokeWidth={1.4} />
    </section>
  );
}

function ModelMetrics({ predictions }: { predictions: PredictionPoint[] }) {
  const future = predictions.filter((item) => item.isPrediction);
  const lower = future.length ? Math.min(...future.map((item) => item.lowerBound)) : .45;
  const upper = future.length ? Math.max(...future.map((item) => item.upperBound)) : 3.2;
  const highRisk = future.find((item) => item.upperBound > 5)?.time || '预测期内较低';
  return (
    <aside className="aqua-panel flex flex-col px-5 py-5">
      <h2 className="text-[17px] font-black text-[#0878e8]">模型置信度</h2>
      <strong className="mt-5 text-[37px] text-[#0878e8]">87%</strong>
      <div className="my-5 h-px bg-[#d8e8f3]" />
      <span className="text-[14px]">预测区间（95%）</span>
      <b className="mt-3 text-[20px] text-[#0878e8]">{lower.toFixed(2)} - {upper.toFixed(2)} <small className="text-[12px] text-[#14213d]">μg/L</small></b>
      <div className="my-5 h-px bg-[#d8e8f3]" />
      <span className="text-[14px]">下一高风险时间</span><b className="mt-3 text-[20px]">{highRisk}</b>
      <div className="mt-auto rounded-[10px] bg-[#edf8ff] p-3 text-[12px] leading-5 text-[#526174]"><ShieldCheck className="mb-2 text-[#0878e8]" size={21} />区间由集成模型与校准器生成，正式接入时需同时展示模型版本与 OOD 标记。</div>
    </aside>
  );
}

export default function DataAnalysisPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get('device') || demoReadings[0].id;
  const sensors = searchParams.get('sensors') || 'all';
  const [readings, setReadings] = useState<DeviceReading[]>(demoReadings);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [predictions, setPredictions] = useState<PredictionPoint[]>([]);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [nextReadings, nextTrends, nextPredictions] = await Promise.all([
        monitoringService.getLatestReadings(), monitoringService.getTrends(selectedId), monitoringService.getPredictions(days),
      ]);
      setReadings(nextReadings); setTrends(nextTrends); setPredictions(nextPredictions);
    } finally { setLoading(false); }
  }, [days, selectedId]);

  useEffect(() => { load(); }, [load]);
  const selected = readings.find((item) => item.id === selectedId) || readings[0];
  useEffect(() => {
    const exportHandler = () => downloadCsv(trends, predictions, selected?.name || '全部设备');
    window.addEventListener('igem:export-data', exportHandler);
    return () => window.removeEventListener('igem:export-data', exportHandler);
  }, [predictions, selected?.name, trends]);

  const selectDevice = (id: string) => {
    const next = new URLSearchParams(searchParams); next.set('device', id); setSearchParams(next, { replace: true });
  };
  const maxPrediction = useMemo(() => Math.max(0, ...predictions.filter((item) => item.isPrediction).map((item) => item.upperBound)), [predictions]);

  return (
    <div className={`grid h-[calc(100vh-142px)] min-h-[720px] grid-rows-[360px_1fr] gap-4 transition-opacity ${loading ? 'opacity-70' : ''}`}>
      <div className="grid min-h-0 grid-cols-[1fr_270px] gap-4"><TrendChart data={trends} sensors={sensors} /><SensorComparison readings={readings} selectedId={selectedId} onSelect={selectDevice} /></div>
      <div className="grid min-h-0 grid-cols-[1fr_210px] gap-4"><PredictionChart data={predictions} days={days} onDaysChange={setDays} /><ModelMetrics predictions={predictions} /></div>
      {maxPrediction > 5 ? <div className="pointer-events-none fixed bottom-7 right-7 z-[900] flex items-center gap-2 rounded-full bg-[#fff2f1] px-4 py-2 text-[12px] font-semibold text-[#c92b32] shadow"><AlertTriangle size={16} />预测区间可能触及高风险阈值</div> : null}
    </div>
  );
}
