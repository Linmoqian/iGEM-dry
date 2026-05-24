import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import AquaPanel from '@/components/common/AquaPanel';

export default function ToxinPredictionPanel() {
  const predictionData = useMemo(() => {
    const data: { date: string; historical: number | null; predicted: number | null; upperBound: number | null; lowerBound: number | null }[] = [];
    const now = new Date(); now.setHours(0, 0, 0, 0);
    for (let i = -7; i <= 0; i++) {
      const date = new Date(now); date.setDate(date.getDate() + i);
      const value = Math.max(0, 0.5 + Math.sin((i + 7) * 0.5) * 0.3 + (Math.random() - 0.5) * 0.2);
      data.push({ date: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }), historical: value, predicted: null, upperBound: null, lowerBound: null });
    }
    let last = data[data.length - 1].historical ?? 0.5;
    for (let i = 1; i <= 7; i++) {
      const date = new Date(now); date.setDate(date.getDate() + i);
      last = last + (i > 3 ? 0.4 : 0.1) + (Math.random() - 0.5) * 0.15;
      data.push({ date: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }), historical: null, predicted: Number(Math.max(0, last).toFixed(2)), upperBound: Number((last + i * 0.2).toFixed(2)), lowerBound: Number(Math.max(0, last - i * 0.2).toFixed(2)) });
    }
    return data;
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-5">
      <AquaPanel title="AI 预测（藻毒素浓度）" subtitle="基于历史检测数据的未来浓度演变趋势"
        action={<span className="text-[11px] px-3 py-1 rounded-full bg-[rgba(45,124,255,0.08)] text-[#2d7cff] font-semibold">预测未来 7 天</span>}>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={predictionData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="ph" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2d7cff" stopOpacity={0.18} /><stop offset="95%" stopColor="#2d7cff" stopOpacity={0} /></linearGradient>
                <linearGradient id="pf" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2d7cff" stopOpacity={0.08} /><stop offset="95%" stopColor="#2d7cff" stopOpacity={0} /></linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(45,124,255,0.08)" vertical={false} />
              <XAxis dataKey="date" fontSize={11} tickLine={false} axisLine={false} stroke="#6b8094" />
              <YAxis fontSize={11} tickLine={false} axisLine={false} stroke="#6b8094" />
              <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #dbeaf7', borderRadius: 16, fontSize: 12 }} />
              <ReferenceLine y={5.0} stroke="#ff3b30" strokeDasharray="4 4" />
              <Area type="monotone" dataKey="lowerBound" stroke="none" fill="rgba(45,124,255,0.06)" />
              <Area type="monotone" dataKey="upperBound" stroke="none" fill="rgba(45,124,255,0.06)" />
              <Area type="monotone" dataKey="historical" stroke="#2d7cff" strokeWidth={2.5} fill="url(#ph)" name="历史数据" />
              <Area type="monotone" dataKey="predicted" stroke="#2d7cff" strokeWidth={2.5} strokeDasharray="6 4" fill="url(#pf)" name="预测值" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </AquaPanel>

      <div className="flex flex-col gap-5">
        <AquaPanel className="flex flex-col gap-4">
          <div><p className="text-[36px] font-extrabold text-[#2d7cff] tracking-[-0.02em]">87%</p><p className="text-[11px] text-[var(--color-muted)] mt-1">模型置信度</p></div>
          <div className="border-t border-[var(--color-border)] pt-4"><p className="text-[11px] text-[var(--color-muted)]">预测区间（95%）</p><p className="text-[16px] font-bold text-[var(--color-text)] mt-0.5">0.45 - 3.20 μg/L</p></div>
          <div className="border-t border-[var(--color-border)] pt-4"><p className="text-[11px] text-[var(--color-muted)]">下一高风险时间</p><p className="text-[16px] font-bold text-[#ff3b30] mt-0.5">5月29日</p></div>
        </AquaPanel>
        <div className="aqua-panel p-5" style={{ backgroundColor: 'rgba(255,59,48,0.04)', borderColor: 'rgba(255,59,48,0.2)' }}>
          <div className="flex items-start gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff3b30" strokeWidth="2"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>
            <div><h3 className="text-[13px] font-bold text-[#ff3b30]">爆发预警</h3><p className="text-[11px] text-[var(--color-muted)] mt-1">浓度可能在 4-5 天内出现显著上升并逼近危险阈值</p></div>
          </div>
        </div>
      </div>
    </div>
  );
}
