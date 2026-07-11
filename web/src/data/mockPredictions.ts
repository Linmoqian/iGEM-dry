import type { PredictionPoint } from '../types/domain';

const values = [3.2, 3.45, 4.6, 2.95, 3.5, 3.1, 1.6, 1.5, 2.25, 2.7, 2.6, 3.15, 2.9, 3.85, 3.65];
const labels = ['05-20', '05-21', '05-22', '05-23', '05-24', '05-25', '05-27', '05-28', '05-29', '05-30', '05-31', '06-01', '06-02', '06-03', '06-04'];

export function generatePredictions(): PredictionPoint[] {
  return labels.map((time, index) => {
    const value = values[index];
    const isPrediction = index >= 7;
    return {
      time,
      value,
      upperBound: isPrediction ? +(value + 0.95 + index * 0.03).toFixed(2) : value,
      lowerBound: isPrediction ? Math.max(0.2, +(value - 0.72 - index * 0.02).toFixed(2)) : value,
      isPrediction,
    };
  });
}
