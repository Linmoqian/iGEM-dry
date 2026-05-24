import type { DeviceReading, DeviceHistoryPoint, TrendPoint } from '@/types/domain';

export function generateTrendData(
  readings: DeviceReading[],
  deviceHistory: Record<string, DeviceHistoryPoint[]>
): TrendPoint[] {
  const days = ['05-20', '05-21', '05-22', '05-23', '05-24', '05-25', '05-26', '05-27'];
  return days.map((date, i) => {
    let toxinSum = 0;
    let maxToxin = 0;
    let tempSum = 0;
    let phSum = 0;
    let hasHighRisk = false;
    let count = 0;

    for (const reading of readings) {
      const history = deviceHistory[reading.id];
      if (!history || history.length === 0) continue;
      const idx = Math.min(i * 3, history.length - 1);
      const point = history[idx];
      toxinSum += point.toxinUgL;
      maxToxin = Math.max(maxToxin, point.toxinUgL);
      tempSum += point.waterTempC;
      phSum += point.ph;
      if (point.toxinUgL > 5) hasHighRisk = true;
      count++;
    }

    return {
      date,
      toxin: count > 0 ? Number((toxinSum / count).toFixed(2)) : 0,
      maxToxin: Number(maxToxin.toFixed(2)),
      temp: count > 0 ? Number((tempSum / count).toFixed(1)) : 0,
      ph: count > 0 ? Number((phSum / count).toFixed(1)) : 0,
      isHighRisk: hasHighRisk,
    };
  });
}
