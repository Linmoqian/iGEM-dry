import { useState } from 'react';
import AppSelect from '@/components/common/AppSelect';
import AppButton from '@/components/common/AppButton';
import type { FilterState } from '@/types/domain';

interface P { onFilterChange?: (s: FilterState) => void; }

export default function DataFilterBar({ onFilterChange }: P) {
  const [filter, setFilter] = useState<FilterState>({ dateRange: '2025-05-20 ~ 2025-05-27', device: 'all', metric: 'all' });

  const update = (key: keyof FilterState, value: string) => {
    const next = { ...filter, [key]: value };
    setFilter(next);
    onFilterChange?.(next);
  };

  return (
    <div className="aqua-panel px-5 py-3 flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-2">
        <label className="text-[11px] font-semibold text-[var(--color-muted)]">时间范围</label>
        <input type="text" readOnly value={filter.dateRange}
          className="text-[13px] py-2 px-3 rounded-[14px] border border-[var(--color-border)] bg-white text-[var(--color-text)] outline-none w-[190px]" />
      </div>
      <AppSelect label="设备" value={filter.device}
        options={[{ value: 'all', label: '全部设备' }, { value: 'online', label: '在线' }, { value: 'idle', label: '待机' }, { value: 'offline', label: '离线' }]}
        onChange={(v) => update('device', v)} />
      <AppSelect label="传感器" value={filter.metric}
        options={[{ value: 'all', label: '藻毒素+水温+pH' }, { value: 'toxin', label: '藻毒素' }, { value: 'temp', label: '水温' }, { value: 'ph', label: 'pH' }]}
        onChange={(v) => update('metric', v)} />
      <div className="flex-1" />
      <AppButton variant="secondary" onClick={() => alert('导出功能将在后端接入后启用')}
        icon={<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>}>
        导出数据
      </AppButton>
    </div>
  );
}
