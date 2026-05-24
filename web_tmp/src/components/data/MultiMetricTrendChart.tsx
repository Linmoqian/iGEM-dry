import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';
import AquaPanel from '@/components/common/AquaPanel';
import type { TrendPoint } from '@/types/domain';

interface P { trendData: TrendPoint[]; }

export default function MultiMetricTrendChart({ trendData }: P) {
  const hasRisk = trendData.some((d) => d.isHighRisk);
  const riskCount = trendData.filter((d) => d.isHighRisk).length;

  if (!trendData.length) {
    return <AquaPanel title="趋势分析" subtitle="藻毒素、水温、pH 综合趋势图"><div className="h-[340px] flex items-center justify-center border-2 border-dashed border-[rgba(45,124,255,0.08)] rounded-2xl"><span className="text-[var(--color-muted)] text-sm">暂无趋势数据</span></div></AquaPanel>;
  }

  return (
    <AquaPanel title="趋势分析" subtitle="藻毒素、水温、pH 综合趋势图">
      <div style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trendData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,124,255,0.08)" vertical={false} />
            <XAxis dataKey="date" fontSize={11} tickLine={false} axisLine={false} stroke="#6b8094" />
            <YAxis yAxisId="left" fontSize={11} tickLine={false} axisLine={false} stroke="#6b8094" />
            <YAxis yAxisId="right" orientation="right" fontSize={11} tickLine={false} axisLine={false} hide />
            <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #dbeaf7', borderRadius: 16, fontSize: 12 }} />
            <Legend iconType="line" wrapperStyle={{ fontSize: 12, fontWeight: 600 }} />
            <ReferenceLine y={1.0} yAxisId="left" stroke="#ff8a00" strokeDasharray="5 5" label={{ value: '警戒 1.0', fill: '#ff8a00', fontSize: 10 }} />
            <ReferenceLine y={5.0} yAxisId="left" stroke="#ff3b30" strokeDasharray="5 5" label={{ value: '高风险 5.0', fill: '#ff3b30', fontSize: 10 }} />
            <Line yAxisId="left" type="monotone" dataKey="toxin" stroke="#2d7cff" strokeWidth={2.5} name="藻毒素" dot={false} />
            <Line yAxisId="left" type="monotone" dataKey="maxToxin" stroke="#ff3b30" strokeWidth={1.5} strokeDasharray="6 4" name="最大浓度" dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="temp" stroke="#1db954" strokeWidth={1.5} name="水温" dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="ph" stroke="#a78bfa" strokeWidth={1.5} name="pH" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {hasRisk && (
        <div className="flex items-center gap-1.5 mt-3 text-[11px] text-[#ff3b30] font-semibold">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>
          检测到 {riskCount} 个异常高值日期
        </div>
      )}
    </AquaPanel>
  );
}
