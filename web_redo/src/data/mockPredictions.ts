import type { PredictionPoint } from '../types/domain';

export function generatePredictions(): PredictionPoint[] {
  const points: PredictionPoint[] = [];
  const now = new Date('2025-05-27T10:00:00');
  const historicalDays = 7;
  const predictionDays = 7;
  const totalDays = historicalDays + predictionDays;

  for (let d = 0; d < totalDays; d++) {
    const t = new Date(now.getTime() - (historicalDays - d) * 86400000);
    const m = (t.getMonth() + 1).toString().padStart(2, '0');
    const day = t.getDate().toString().padStart(2, '0');
    const dateStr = `${m}-${day}`;
    const isPrediction = d >= historicalDays;

    const trend = isPrediction ? 1.5 + (d - historicalDays) * 0.35 : 1.2 + Math.sin(d / historicalDays * Math.PI) * 0.8;
    const noise = (Math.sin(d * 1.7) * 0.3 + Math.cos(d * 2.3) * 0.25) * (isPrediction ? 1.5 : 1);
    const value = +Math.max(0.1, trend + noise).toFixed(2);

    points.push({
      time: dateStr,
      value,
      upperBound: +Math.min(8, value + 0.6 + Math.random() * 0.4).toFixed(2),
      lowerBound: +Math.max(0, value - 0.4 - Math.random() * 0.3).toFixed(2),
      isPrediction,
    });
  }

  return points;
}
