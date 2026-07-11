import { AlertTriangle, ChevronDown, Info, ShieldCheck } from 'lucide-react';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { demoReadings, getRiskColor } from '../data/demoReadings';
import { generatePredictions } from '../data/mockPredictions';

const trendData = [
  { time: '05-20', toxin: 1.0, temp: 22.0, ph: 7.0 },
  { time: '05-20', toxin: 1.15, temp: 23.2, ph: 7.35 },
  { time: '05-21', toxin: 1.2, temp: 24.5, ph: 7.55 },
  { time: '05-21', toxin: 1.55, temp: 26.7, ph: 7.35 },
  { time: '05-22', toxin: 1.7, temp: 24.8, ph: 7.7 },
  { time: '05-22', toxin: 2.9, temp: 29.0, ph: 8.1 },
  { time: '05-23', toxin: 2.35, temp: 25.5, ph: 7.8 },
  { time: '05-23', toxin: 1.65, temp: 24.8, ph: 7.95 },
  { time: '05-24', toxin: 1.9, temp: 25.0, ph: 7.62 },
  { time: '05-24', toxin: 2.55, temp: 27.8, ph: 7.35 },
  { time: '05-25', toxin: 1.8, temp: 24.9, ph: 7.45 },
  { time: '05-25', toxin: 1.55, temp: 24.5, ph: 7.9 },
  { time: '05-26', toxin: 1.9, temp: 25.4, ph: 8.05 },
  { time: '05-26', toxin: 2.1, temp: 26.0, ph: 7.85 },
  { time: '05-27', toxin: 1.95, temp: 26.1, ph: 7.6 },
];

function Legend({ color, label, dashed = false, block = false }: { color: string; label: string; dashed?: boolean; block?: boolean }) {
  return (
    <span className="flex items-center gap-2 text-[17px] text-[#23334d]">
      <span className={`${block ? 'h-3 w-6' : dashed ? 'h-0 w-7 border-t-[4px] border-dashed' : 'h-[5px] w-7 rounded-full'}`} style={{ backgroundColor: block ? color : undefined, borderColor: dashed ? color : undefined, background: !block && !dashed ? color : undefined }} />
      {label}
    </span>
  );
}

function TrendChart() {
  return (
    <section className="aqua-panel flex min-h-0 flex-1 flex-col px-7 py-6">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[22px] font-black">趋势分析</h2>
        <div className="flex gap-10">
          <Legend color="#0874ed" label="藻毒素（μg/L）" />
          <Legend color="#0aa77d" label="水温（°C）" />
          <Legend color="#824fd1" label="pH" />
        </div>
      </div>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={trendData} margin={{ top: 24, right: 76, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="#cbddec" strokeDasharray="2 4" />
            <XAxis dataKey="time" tick={{ fontSize: 16, fill: '#243149' }} interval={1} tickLine={false} />
            <YAxis yAxisId="toxin" domain={[0, 5]} ticks={[0, 1, 2, 3, 4, 5]} tick={{ fontSize: 16, fill: '#0874ed' }} tickLine={false} />
            <YAxis yAxisId="temp" orientation="right" domain={[18, 30]} ticks={[18, 21, 24, 27, 30]} tick={{ fontSize: 16, fill: '#0aa77d' }} tickLine={false} />
            <YAxis yAxisId="ph" orientation="right" domain={[6, 8.5]} hide />
            <Tooltip />
            <ReferenceLine yAxisId="toxin" y={5} stroke="#ef1919" strokeDasharray="5 5" label={{ value: '高风险阈值 (5.0 μg/L)', fill: '#ef1919', fontSize: 16, position: 'insideTopRight' }} />
            <ReferenceLine yAxisId="toxin" y={1} stroke="#f97316" strokeDasharray="5 5" label={{ value: '警戒阈值 (1.0 μg/L)', fill: '#f97316', fontSize: 16, position: 'insideRight' }} />
            <Line yAxisId="toxin" type="monotone" dataKey="toxin" stroke="#0874ed" strokeWidth={3} dot={{ r: 5, fill: '#0874ed', strokeWidth: 0 }} />
            <Line yAxisId="temp" type="monotone" dataKey="temp" stroke="#0aa77d" strokeWidth={3} dot={{ r: 5, fill: '#0aa77d', strokeWidth: 0 }} />
            <Line yAxisId="ph" type="monotone" dataKey="ph" stroke="#824fd1" strokeWidth={3} dot={{ r: 5, fill: '#824fd1', strokeWidth: 0 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function SensorComparison() {
  const rows = demoReadings.slice(0, 5);
  return (
    <section className="aqua-panel w-[430px] shrink-0 px-7 py-6">
      <h2 className="mb-7 text-[22px] font-black">传感器对比</h2>
      <div className="mb-3 flex justify-between text-[17px] font-semibold">
        <span>藻毒素（μg/L）</span>
        <span>最新值（单位）</span>
      </div>
      <div className="flex flex-col">
        {rows.map((device) => (
          <div key={device.id} className="flex h-[58px] items-center justify-between text-[18px]">
            <span className="flex items-center gap-4">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getRiskColor(device.toxinUgL) }} />
              {device.name}
            </span>
            <b className="text-[30px]" style={{ color: getRiskColor(device.toxinUgL) }}>
              {device.toxinUgL.toFixed(2)}
            </b>
          </div>
        ))}
      </div>
      <button className="mt-4 flex items-center gap-2 text-[18px] font-semibold text-[#0874ed]" type="button">
        查看全部 <ChevronDown className="-rotate-90" size={18} />
      </button>
    </section>
  );
}

function AIPredictionChart() {
  const data = generatePredictions();
  return (
    <section className="aqua-panel flex min-h-0 flex-1 flex-col px-7 py-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[22px] font-black">AI 预测 <span className="text-[18px]">（藻毒素浓度）</span></h2>
        <button className="flex h-10 items-center gap-4 rounded-[8px] border border-[#c6ddf2] px-5 text-[17px]" type="button">
          预测未来 7 天 <ChevronDown size={18} />
        </button>
      </div>
      <div className="mb-2 flex items-center gap-9">
        <span className="text-[17px]">μg/L</span>
        <Legend color="#0874ed" label="历史数据" />
        <Legend color="#0874ed" label="预测值" dashed />
        <Legend color="rgba(8,116,237,.22)" label="置信区间（95%）" block />
      </div>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 6, left: 0 }}>
            <CartesianGrid stroke="#cbddec" strokeDasharray="2 4" />
            <XAxis dataKey="time" tick={{ fontSize: 16, fill: '#243149' }} tickLine={false} />
            <YAxis domain={[0, 6]} ticks={[0, 1, 2, 3, 4, 5, 6]} tick={{ fontSize: 16, fill: '#243149' }} tickLine={false} />
            <Tooltip />
            <Area dataKey="upperBound" fill="rgba(8,116,237,.18)" stroke="none" isAnimationActive={false} />
            <Line type="monotone" dataKey="value" stroke="#0874ed" strokeWidth={3} dot={{ r: 4, fill: '#0874ed', strokeWidth: 0 }} strokeDasharray="0" />
            <ReferenceLine x="05-28" stroke="#9eb7ce" strokeDasharray="4 4" label={{ value: '预测开始', fill: '#0874ed', fontSize: 16, position: 'top' }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function AIMetricsCard() {
  return (
    <section className="aqua-panel w-[430px] shrink-0 px-7 py-8">
      <div className="flex items-center gap-5">
        <div className="flex h-[75px] w-[75px] items-center justify-center rounded-[18px] bg-[#e8f4ff] text-[#0874ed]">
          <ShieldCheck size={54} />
        </div>
        <div>
          <div className="text-[21px] font-black">模型置信度</div>
          <div className="text-[45px] font-black leading-tight text-[#0874ed]">87%</div>
        </div>
      </div>
      <div className="my-7 h-px bg-[#cfe3f4]" />
      <div className="text-[19px] font-semibold">预测区间（95%）</div>
      <div className="mt-5 text-[30px] font-black text-[#0874ed]">0.45 - 3.20 <span className="text-[18px] text-[#12203a]">μg/L</span></div>
      <div className="my-7 h-px bg-[#cfe3f4]" />
      <div className="text-[19px] font-semibold">下一高风险时间</div>
      <div className="mt-4 flex items-center gap-4 text-[28px] font-black">
        5月29日 <AlertTriangle size={28} className="text-[#ef1919]" />
      </div>
      <div className="aqua-panel mt-8 flex gap-4 bg-[#f3f9ff] px-5 py-4 shadow-none">
        <Info size={24} className="mt-1 shrink-0 text-[#0874ed]" />
        <p className="text-[17px] leading-8 text-[#344054]">近期藻毒素浓度呈上升趋势，请持续关注高风险时段。</p>
      </div>
    </section>
  );
}

export default function DataAnalysisPage() {
  return (
    <div className="flex h-full flex-col gap-5">
      <div className="grid h-[410px] shrink-0 grid-cols-[1fr_430px] gap-5">
        <TrendChart />
        <SensorComparison />
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-[1fr_430px] gap-5">
        <AIPredictionChart />
        <AIMetricsCard />
      </div>
    </div>
  );
}
