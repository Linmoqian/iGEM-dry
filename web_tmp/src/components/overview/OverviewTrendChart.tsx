import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';
import AquaPanel from '@/components/common/AquaPanel';
import type { TrendPoint } from '@/types/domain';

interface P { data: TrendPoint[]; currentValue: number; deviceName: string; }

export default function OverviewTrendChart({ data, currentValue, deviceName }: P) {
  return (
    <AquaPanel title="趋势概览" subtitle={`${deviceName} 藻毒素浓度`}
      action={<span className="text-[11px] px-3 py-1 rounded-full bg-[rgba(45,124,255,0.08)] text-[#2d7cff] font-semibold">近 7 天</span>}>
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-[28px] font-extrabold text-[#2d7cff] tracking-[-0.02em]">{currentValue.toFixed(2)}</span>
        <span className="text-[12px] text-[var(--color-muted)]">μg/L</span>
      </div>
      <div style={{ height: 160 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="ovGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2d7cff" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#2d7cff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,124,255,0.08)" vertical={false} />
            <XAxis dataKey="date" fontSize={10} tickLine={false} axisLine={false} stroke="#6b8094" />
            <YAxis fontSize={10} tickLine={false} axisLine={false} stroke="#6b8094" />
            <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #dbeaf7', borderRadius: 16, fontSize: 12 }} />
            <ReferenceLine y={1.0} stroke="#ff8a00" strokeDasharray="5 5" strokeWidth={1} />
            <ReferenceLine y={5.0} stroke="#ff3b30" strokeDasharray="5 5" strokeWidth={1} />
            <Area type="monotone" dataKey="toxin" stroke="#2d7cff" strokeWidth={2} fill="url(#ovGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </AquaPanel>
  );
}
