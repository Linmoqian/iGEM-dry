'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from 'recharts';
import { getRiskColor, getRiskLabel } from '../lib/demoReadings';

// This is a placeholder model for predicting toxin concentration
// To be replaced with actual ML mathematical model
export default function ToxinPredictionModel() {
  const predictionData = useMemo(() => {
    const data = [];
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    // Past 7 days data
    for (let i = -7; i <= 0; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() + i);
      
      // Simulate historical data with some noise
      const baseValue = 0.5 + Math.sin((i + 7) * 0.5) * 0.3;
      const noise = (Math.random() - 0.5) * 0.2;
      
      data.push({
        date: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
        value: Math.max(0, baseValue + noise),
        isPrediction: false,
      });
    }

    // Future 7 days prediction
    let lastValue = data[data.length - 1].value;
    for (let i = 1; i <= 7; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() + i);
      
      // Simulate an upcoming spike (bloom)
      const trend = i > 3 ? 0.4 : 0.1; 
      lastValue = lastValue + trend + (Math.random() - 0.5) * 0.15;

      data.push({
        date: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
        value: Math.max(0, lastValue),
        isPrediction: true,
        // Confidence intervals for the prediction
        upperBound: Number((lastValue + i * 0.2).toFixed(2)),
        lowerBound: Number(Math.max(0, lastValue - i * 0.2).toFixed(2)),
      });
    }
    return data;
  }, []);

  const riskThreshold = 2.0;

  return (
    <section className="bg-[#0B1221]/70 backdrop-blur-2xl border border-slate-700/50 shadow-[0_16px_60px_rgba(0,0,0,0.5)] rounded-3xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-black text-slate-100 flex items-center gap-2">
            AI 毒素爆发预测模型 <span className="px-2 py-0.5 rounded text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30">占位版</span>
          </h2>
          <p className="text-sm text-slate-500 mt-1">基于历史检测数据的未来七天浓度演变趋势（示例模型）</p>
        </div>
      </div>

      <div className="h-[300px] w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={predictionData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPrediction" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false} 
              dy={10}
            />
            <YAxis 
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false} 
              dx={-10}
              tickFormatter={(value) => `${value.toFixed(1)}`}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
              itemStyle={{ color: '#e2e8f0' }}
              labelStyle={{ color: '#94a3b8', marginBottom: '8px' }}
              formatter={(value: number, name: string) => {
                if (name === 'upperBound' || name === 'lowerBound') {
                  return [`${value.toFixed(2)} µg/L`, name === 'upperBound' ? '置信区间上界' : '置信区间下界'];
                }
                return [`${value.toFixed(2)} µg/L`, name === 'value' ? '预测浓度' : name];
              }}
            />
            
            <ReferenceLine 
              y={riskThreshold} 
              stroke="#ef4444" 
              strokeDasharray="3 3" 
              label={{ position: 'top', value: '危险阈值', fill: '#ef4444', fontSize: 12 }} 
            />

            {/* Confidence interval area for prediction */}
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="#8b5cf6"
              fillOpacity={0.1}
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#0f172a"
              fillOpacity={1}
            />

            {/* Historical line */}
            <Area
              type="monotone"
              dataKey={(d) => (!d.isPrediction ? d.value : null)}
              stroke="#06b6d4"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorValue)"
              isAnimationActive={false}
            />
            
            {/* Future prediction line */}
            <Area
              type="monotone"
              dataKey={(d) => (d.isPrediction || predictionData.indexOf(d) === 7 ? d.value : null)}
              stroke="#8b5cf6"
              strokeWidth={3}
              strokeDasharray="5 5"
              fillOpacity={1}
              fill="url(#colorPrediction)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 text-purple-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
          </div>
          <div>
            <h3 className="font-bold text-slate-200">爆发预警</h3>
            <p className="text-sm text-slate-400 mt-1">
              根据假设模型预测，藻毒素浓度可能在 <strong className="text-purple-300">未来 4-5 天内</strong> 出现显著上升并逼近危险阈值。该预测基于光照、温度和当前历史生长曲线。
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}