export function formatToxin(value: number): string {
  return `${value.toFixed(2)} μg/L`;
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatDbm(value: number): string {
  return `${value} dBm`;
}

export function formatTemp(value: number): string {
  return `${value.toFixed(1)} °C`;
}

export function formatPh(value: number): string {
  return value.toFixed(1);
}
