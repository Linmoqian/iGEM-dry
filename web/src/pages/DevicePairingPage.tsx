import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  DndContext,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import { SortableContext, arrayMove, rectSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Anchor,
  Battery,
  Bluetooth,
  Check,
  ChevronLeft,
  ChevronRight,
  GripVertical,
  Pencil,
  Plus,
  RadioTower,
  RefreshCw,
  Search,
  TestTube2,
  Trash2,
  Wifi,
  X,
} from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { getRiskColor, getStatusText } from '../data/demoReadings';
import { materials } from '../data/materials';
import { deviceService } from '../services/deviceService';
import type { DeviceInput, DeviceReading, DeviceStatus, DiscoveredDevice } from '../types/domain';

const deviceIconSet = [RadioTower, TestTube2, Anchor];

function DeviceVisual({ index, offline }: { index: number; offline: boolean }) {
  const Icon = deviceIconSet[index % deviceIconSet.length];
  return (
    <div className={`relative flex h-[76px] w-[76px] shrink-0 items-center justify-center rounded-[24px] border border-[#b9ddf4] bg-gradient-to-b from-[#f8fdff] to-[#dff3ff] text-[#0b8b74] shadow-[inset_0_-8px_16px_rgba(72,174,222,.1)] ${offline ? 'grayscale opacity-55' : ''}`}>
      <Icon size={43} strokeWidth={1.55} />
      <span className="absolute -bottom-2 h-3 w-12 rounded-[50%] bg-[#85d5f3]/45" />
    </div>
  );
}

function DeviceCard({ device, index, checked, dragDisabled, onChecked, onEdit, onDelete }: {
  device: DeviceReading;
  index: number;
  checked: boolean;
  dragDisabled: boolean;
  onChecked: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: device.id, disabled: dragDisabled });
  const offline = device.status === 'offline';
  const statusColor = device.status === 'online' ? '#078b4f' : device.status === 'idle' ? '#f97316' : '#6b7280';
  return (
    <article
      ref={setNodeRef}
      className={`aqua-panel relative flex h-[228px] min-w-0 flex-col px-4 py-4 transition ${checked ? 'border-[#0878e8] shadow-[0_0_0_1px_#0878e8]' : ''} ${isDragging ? 'z-50 opacity-70 shadow-xl' : ''}`}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      <button className={`absolute right-3 top-3 z-10 flex h-7 w-7 items-center justify-center rounded-full border ${checked ? 'border-[#0878e8] bg-[#0878e8] text-white' : 'border-[#b8d9ee] bg-white text-transparent'}`} type="button" aria-label={checked ? '取消选择' : '选择设备'} onClick={onChecked}><Check size={17} /></button>
      <div className="flex gap-3 pr-8">
        <button className="cursor-grab touch-none active:cursor-grabbing" type="button" aria-label="拖拽调整顺序" disabled={dragDisabled} {...attributes} {...listeners}><DeviceVisual index={index} offline={offline} /></button>
        <div className="min-w-0 pt-1"><h3 className="truncate text-[18px] font-black" title={device.name}>{device.name}</h3><p className="mt-2 flex items-center gap-2 text-[14px] font-semibold" style={{ color: statusColor }}><span className="h-2.5 w-2.5 rounded-full" style={{ background: statusColor }} />{getStatusText(device.status)}</p></div>
      </div>
      <div className="mt-3 flex items-center justify-between border-b border-[#d7e8f4] pb-3">
        <Wifi size={23} className={offline ? 'text-[#87919f]' : 'text-[#078b4f]'} />
        <span className="flex items-center gap-2 text-[14px] font-semibold"><Battery size={24} className={offline ? 'text-[#87919f]' : 'text-[#078b4f]'} />{offline ? '--' : `${device.batteryPercent}%`}</span>
        <div className="flex gap-1">
          <button className="rounded-md p-1.5 text-[#54708a] hover:bg-[#edf7ff] hover:text-[#0878e8]" type="button" aria-label="编辑设备" onClick={onEdit}><Pencil size={16} /></button>
          <button className="rounded-md p-1.5 text-[#8a6470] hover:bg-[#fff0f0] hover:text-[#e22b35]" type="button" aria-label="删除设备" onClick={onDelete}><Trash2 size={16} /></button>
        </div>
      </div>
      <div className="grid flex-1 grid-cols-3 divide-x divide-[#d7e8f4] pt-3">
        {[
          ['藻毒素', offline ? '--' : device.toxinUgL.toFixed(2), 'μg/L', offline ? '#64748b' : getRiskColor(device.toxinUgL)],
          ['水温', offline ? '--' : device.waterTempC.toFixed(1), '°C', '#111827'],
          ['pH', offline ? '--' : device.ph.toFixed(1), '', '#111827'],
        ].map(([label, value, unit, color]) => <div key={label} className="flex min-w-0 flex-col justify-center gap-2 px-3 first:pl-0 last:pr-0"><span className="text-[13px] text-[#526174]">{label}</span><span className="whitespace-nowrap"><b className="text-[20px]" style={{ color }}>{value}</b><small className="ml-1 text-[11px]">{unit}</small></span></div>)}
      </div>
    </article>
  );
}

function RadarScanner({ scanning }: { scanning: boolean }) {
  return (
    <div className={`radar ${scanning ? 'scanning' : ''}`}>
      <i className="ring ring-1" /><i className="ring ring-2" /><i className="ring ring-3" /><i className="radar-axis vertical" /><i className="radar-axis horizontal" />
      <i className="radar-blip blip-1" /><i className="radar-blip blip-2" /><i className="radar-blip blip-3" />
      <div className="radar-center"><Bluetooth size={35} /></div><div className="radar-sweep" />
    </div>
  );
}

function PairingPanel({ onPaired }: { onPaired: () => void }) {
  const [scanning, setScanning] = useState(false);
  const [discovered, setDiscovered] = useState<DiscoveredDevice[]>([]);
  const [pairingId, setPairingId] = useState('');
  const [message, setMessage] = useState('');

  const scan = useCallback(async () => {
    setScanning(true); setMessage('正在扫描附近设备…');
    try { setDiscovered(await deviceService.scan()); setMessage('扫描完成'); }
    finally { setScanning(false); }
  }, []);
  useEffect(() => { scan(); }, [scan]);

  const pair = async (device: DiscoveredDevice) => {
    setPairingId(device.id); setMessage(`正在连接 ${device.name}…`);
    try {
      await deviceService.pair(device);
      setDiscovered((items) => items.map((item) => item.id === device.id ? { ...item, paired: true } : item));
      setMessage(`${device.name} 已连接`); onPaired();
    } catch { setMessage('连接失败，请靠近设备后重试'); }
    finally { setPairingId(''); }
  };

  return (
    <aside className="aqua-panel relative w-[320px] shrink-0 overflow-hidden px-5 py-5">
      <div className="relative z-10">
        <div className="flex items-center justify-between"><div><h2 className="text-[20px] font-black">添加新设备</h2><p className="mt-3 text-[15px] font-semibold">扫描附近设备</p></div><button className="rounded-lg p-2 text-[#0878e8] hover:bg-[#edf7ff]" type="button" aria-label="重新扫描" onClick={scan} disabled={scanning}><RefreshCw size={20} className={scanning ? 'spin' : ''} /></button></div>
        <RadarScanner scanning={scanning} />
        <div className="mt-3 flex items-center justify-between"><b className="text-[16px]">已发现设备（{discovered.length}）</b><span className="text-[11px] text-[#5d7186]">{message}</span></div>
        <div className="mt-3 flex flex-col gap-3">
          {discovered.map((device) => (
            <div key={device.id} className="aqua-panel flex min-h-[76px] items-center justify-between gap-2 px-3 shadow-none">
              <div className="min-w-0"><h3 className="truncate text-[14px] font-semibold">{device.name}</h3><p className="mt-1 text-[12px] text-[#5b6b81]">RSSI {device.signalDbm} dBm · {device.connectionType === 'bluetooth' ? '蓝牙' : 'Wi-Fi'}</p></div>
              <button className={`h-10 shrink-0 rounded-[8px] px-3 text-[13px] font-semibold ${device.paired ? 'bg-[#eaf8f2] text-[#078b4f]' : 'bg-[#0878e8] text-white'}`} type="button" disabled={device.paired || pairingId === device.id} onClick={() => pair(device)}>{device.paired ? '已连接' : pairingId === device.id ? '连接中' : device.connectionType === 'bluetooth' ? '蓝牙配对' : 'WiFi连接'}</button>
            </div>
          ))}
          {!scanning && discovered.length === 0 ? <div className="empty-state min-h-[120px] text-[13px]">未发现可配对设备</div> : null}
        </div>
      </div>
      <img className="pointer-events-none absolute -bottom-6 -right-7 w-[170px] opacity-[.12]" src={materials.mascotScientist} alt="" />
    </aside>
  );
}

function DeviceModal({ device, onClose, onSaved }: { device?: DeviceReading; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(device?.name || '');
  const [location, setLocation] = useState(device?.locationLabel || '东湖待部署点');
  const [connectionType, setConnectionType] = useState<'wifi' | 'bluetooth'>(device?.connectionType === 'bluetooth' ? 'bluetooth' : 'wifi');
  const [saving, setSaving] = useState(false);
  const save = async (event: React.FormEvent) => {
    event.preventDefault(); if (!name.trim()) return;
    setSaving(true);
    try {
      if (device) await deviceService.update(device.id, { name: name.trim(), locationLabel: location.trim(), connectionType });
      else await deviceService.create({ name: name.trim(), locationLabel: location.trim(), connectionType } satisfies DeviceInput);
      onSaved(); onClose();
    } finally { setSaving(false); }
  };
  return (
    <div className="fixed inset-0 z-[2000] grid place-items-center bg-[#12324c]/25 p-5 backdrop-blur-[2px]" role="dialog" aria-modal="true" aria-label={device ? '编辑设备' : '添加设备'}>
      <form className="w-full max-w-[470px] rounded-[18px] border border-[#b9dcf5] bg-white p-6 shadow-2xl" onSubmit={save}>
        <div className="flex items-center justify-between"><h2 className="text-[20px] font-black">{device ? '编辑设备' : '添加新设备'}</h2><button className="rounded-full p-2 hover:bg-[#f1f7fb]" type="button" aria-label="关闭" onClick={onClose}><X size={20} /></button></div>
        <label className="mt-5 block text-[13px] font-semibold">设备名称<input className="mt-2 h-11 w-full rounded-[9px] border border-[#bfd9ec] px-3 font-normal outline-none focus:border-[#0878e8]" value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：湖心浮标-15" autoFocus /></label>
        <label className="mt-4 block text-[13px] font-semibold">部署位置<input className="mt-2 h-11 w-full rounded-[9px] border border-[#bfd9ec] px-3 font-normal outline-none focus:border-[#0878e8]" value={location} onChange={(event) => setLocation(event.target.value)} /></label>
        <label className="mt-4 block text-[13px] font-semibold">连接方式<select className="mt-2 h-11 w-full rounded-[9px] border border-[#bfd9ec] bg-white px-3 font-normal" value={connectionType} onChange={(event) => setConnectionType(event.target.value as 'wifi' | 'bluetooth')}><option value="wifi">Wi-Fi</option><option value="bluetooth">蓝牙</option></select></label>
        <div className="mt-6 flex justify-end gap-3"><button className="secondary-button h-11 px-5" type="button" onClick={onClose}>取消</button><button className="primary-button h-11 px-6" type="submit" disabled={saving || !name.trim()}>{saving ? '保存中…' : '保存设备'}</button></div>
      </form>
    </div>
  );
}

export default function DevicePairingPage() {
  const [searchParams] = useSearchParams();
  const query = (searchParams.get('q') || '').trim().toLowerCase();
  const [devices, setDevices] = useState<DeviceReading[]>([]);
  const [status, setStatus] = useState<'all' | DeviceStatus>('all');
  const [page, setPage] = useState(0);
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set());
  const [editing, setEditing] = useState<DeviceReading | null | undefined>(undefined);
  const [toast, setToast] = useState('');
  const [loading, setLoading] = useState(true);
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }));

  const load = useCallback(async () => {
    setLoading(true);
    try { setDevices(await deviceService.list()); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); window.addEventListener('igem:refresh', load); return () => window.removeEventListener('igem:refresh', load); }, [load]);

  const filtered = useMemo(() => devices.filter((device) => {
    const matchesQuery = !query || device.name.toLowerCase().includes(query) || device.id.toLowerCase().includes(query) || device.locationLabel.toLowerCase().includes(query);
    return matchesQuery && (status === 'all' || device.status === status);
  }), [devices, query, status]);
  const totalPages = Math.max(1, Math.ceil(filtered.length / 6));
  const pageDevices = filtered.slice(page * 6, page * 6 + 6);
  const dragDisabled = Boolean(query) || status !== 'all';
  useEffect(() => setPage(0), [query, status]);
  useEffect(() => { if (page >= totalPages) setPage(totalPages - 1); }, [page, totalPages]);

  const onDragEnd = async ({ active, over }: DragEndEvent) => {
    if (!over || active.id === over.id || dragDisabled) return;
    const oldIndex = devices.findIndex((device) => device.id === active.id);
    const newIndex = devices.findIndex((device) => device.id === over.id);
    const next = arrayMove(devices, oldIndex, newIndex); setDevices(next);
    await deviceService.reorder(next.map((device) => device.id)); setToast('设备顺序已保存');
  };

  const remove = async (device: DeviceReading) => {
    if (!window.confirm(`确认删除“${device.name}”？此操作仅影响当前演示数据。`)) return;
    await deviceService.remove(device.id); setCheckedIds((current) => { const next = new Set(current); next.delete(device.id); return next; }); await load(); setToast('设备已删除');
  };
  const batchAction = async (action: string) => {
    const ids = [...checkedIds]; if (!ids.length || !action) return;
    if (action === 'offline') await Promise.all(ids.map((id) => deviceService.update(id, { status: 'offline' })));
    if (action === 'online') await Promise.all(ids.map((id) => deviceService.update(id, { status: 'online' })));
    if (action === 'delete' && window.confirm(`确认删除选中的 ${ids.length} 台设备？`)) await Promise.all(ids.map((id) => deviceService.remove(id)));
    setCheckedIds(new Set()); await load(); setToast('批量操作已完成');
  };

  useEffect(() => { if (!toast) return; const timer = window.setTimeout(() => setToast(''), 2300); return () => window.clearTimeout(timer); }, [toast]);

  return (
    <div className="flex h-[calc(100vh-142px)] min-h-[720px] gap-4">
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="mb-4 flex h-[48px] shrink-0 items-center gap-3">
          <button className="primary-button flex h-12 items-center gap-2 px-5" type="button" onClick={() => setEditing(null)}><Plus size={22} />添加设备</button>
          <button className="secondary-button flex h-12 items-center gap-2 px-5" type="button" onClick={load}><RefreshCw size={20} className={loading ? 'spin' : ''} />刷新列表</button>
          <label className="relative"><select className="secondary-button h-12 appearance-none pl-4 pr-10" value={status} onChange={(event) => setStatus(event.target.value as 'all' | DeviceStatus)}><option value="all">全部状态</option><option value="online">在线设备</option><option value="idle">待机设备</option><option value="offline">离线设备</option></select><span className="pointer-events-none absolute right-3 top-3.5 text-[12px]">▼</span></label>
          <label className="relative"><select className="secondary-button h-12 appearance-none pl-4 pr-10" defaultValue="" onChange={(event) => { batchAction(event.target.value); event.target.value = ''; }}><option value="">批量操作（{checkedIds.size}）</option><option value="online">设为在线</option><option value="offline">设为离线</option><option value="delete">删除选中</option></select><span className="pointer-events-none absolute right-3 top-3.5 text-[12px]">▼</span></label>
          <div className="ml-auto flex h-12 w-[200px] items-center gap-2 rounded-[10px] border border-[#bfdcf3] bg-white/85 px-4 text-[13px] text-[#71819a]"><Search size={18} />{query ? `筛选：${query}` : '可在顶部搜索设备'}</div>
          <div className="flex h-12 items-center rounded-[10px] border border-[#bfdcf3] bg-white text-[12px]"><button className="h-full px-2 disabled:opacity-30" type="button" aria-label="上一页" disabled={page === 0} onClick={() => setPage((value) => value - 1)}><ChevronLeft size={17} /></button><span className="min-w-[42px] text-center">{page + 1}/{totalPages}</span><button className="h-full px-2 disabled:opacity-30" type="button" aria-label="下一页" disabled={page + 1 >= totalPages} onClick={() => setPage((value) => value + 1)}><ChevronRight size={17} /></button></div>
        </div>

        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
          <SortableContext items={pageDevices.map((device) => device.id)} strategy={rectSortingStrategy}>
            <div className="grid min-h-0 flex-1 grid-cols-3 grid-rows-2 content-start gap-4 overflow-hidden pr-1">
              {pageDevices.map((device) => {
                const index = devices.findIndex((item) => item.id === device.id);
                return <DeviceCard key={device.id} device={device} index={index} checked={checkedIds.has(device.id)} dragDisabled={dragDisabled} onChecked={() => setCheckedIds((current) => { const next = new Set(current); if (next.has(device.id)) next.delete(device.id); else next.add(device.id); return next; })} onEdit={() => setEditing(device)} onDelete={() => remove(device)} />;
              })}
              {!loading && filtered.length === 0 ? <div className="empty-state col-span-3"><div><Search className="mx-auto mb-3" /><p>没有符合条件的设备</p></div></div> : null}
            </div>
          </SortableContext>
        </DndContext>
        <div className="mt-4 flex h-[70px] shrink-0 items-center justify-center gap-3 rounded-[10px] border-2 border-dashed border-[#70baf0] bg-white/45 text-[16px] font-semibold text-[#53657a]"><GripVertical size={24} />{dragDisabled ? '清除搜索与状态筛选后可拖拽排序' : '拖拽设备卡片可调整顺序'}</div>
      </section>
      <PairingPanel onPaired={load} />
      {editing !== undefined ? <DeviceModal device={editing || undefined} onClose={() => setEditing(undefined)} onSaved={() => { load(); setToast(editing ? '设备信息已更新' : '设备已添加'); }} /> : null}
      {toast ? <div className="fixed bottom-7 left-1/2 z-[2100] flex -translate-x-1/2 items-center gap-2 rounded-full bg-[#123b55] px-5 py-2.5 text-[13px] text-white shadow-lg"><Check size={17} />{toast}</div> : null}
    </div>
  );
}
