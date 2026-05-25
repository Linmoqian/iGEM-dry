import { useState } from 'react';
import {
  Plus, RefreshCw, ChevronDown, GripVertical,
  LifeBuoy, Thermometer, Scan, Wifi, Bluetooth, Check, X,
} from 'lucide-react';
import {
  DndContext, closestCenter, PointerSensor, KeyboardSensor,
  useSensor, useSensors, DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext, useSortable, rectSortingStrategy,
  sortableKeyboardCoordinates, arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { demoReadings, getRiskColor, getStatusText } from '../data/demoReadings';
import type { DeviceReading } from '../types/domain';

/* ───── device icon rotation ───── */
const deviceIcons = [LifeBuoy, Thermometer, Scan, LifeBuoy, Thermometer, Scan];

/* ───── Modal ───── */
function Modal({
  title, message, loading, onClose,
}: {
  title: string; message: string; loading: boolean; onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl p-8 w-[380px] flex flex-col items-center gap-4 shadow-xl">
        {loading ? (
          <div className="w-12 h-12 border-4 border-[#E6F0FA] border-t-[#1A73E8] rounded-full animate-spin" />
        ) : (
          <div className="w-12 h-12 rounded-full bg-[#22C55E1A] flex items-center justify-center">
            <Check size={24} className="text-[#22C55E]" />
          </div>
        )}
        <h3 className="text-lg font-bold text-[#0F172A]">{title}</h3>
        <p className="text-sm text-[#64748B] text-center whitespace-pre-wrap leading-relaxed">{message}</p>
        <button
          onClick={onClose}
          className="h-10 px-8 rounded-lg border border-[#E2E8F0] text-sm font-bold text-[#0F172A] mt-2 hover:bg-[#F8FAFC] transition-colors"
        >
          {loading ? '中断连接' : '确认'}
        </button>
      </div>
    </div>
  );
}

/* ───── Radar Scanner ───── */
function RadarScanner() {
  return (
    <div className="h-[260px] flex items-center justify-center relative">
      {/* Concentric ellipses — matching pen positions */}
      <div className="absolute w-[200px] h-[200px] rounded-full border border-[#E0F2FE]" style={{ top: 30, left: 110 }} />
      <div className="absolute w-[150px] h-[150px] rounded-full border border-[#E0F2FE]" style={{ top: 55, left: 135 }} />
      <div className="absolute w-[100px] h-[100px] rounded-full border border-[#E0F2FE]" style={{ top: 80, left: 160 }} />
      <div className="absolute w-[50px] h-[50px] rounded-full border border-[#E0F2FE]" style={{ top: 105, left: 185 }} />
      {/* Center button */}
      <div
        className="absolute w-16 h-16 rounded-full bg-[#1A73E8] flex items-center justify-center animate-pulse"
        style={{ top: 98, left: 178 }}
      >
        <Bluetooth size={32} className="text-white" />
      </div>
    </div>
  );
}

/* ───── Device Card ───── */
function DeviceCard({
  device,
  iconIndex,
  isSelected,
  onSelect,
  onConnectClick,
  onDetailsClick,
}: {
  device: DeviceReading;
  iconIndex: number;
  isSelected: boolean;
  onSelect: () => void;
  onConnectClick: (type: 'bluetooth' | 'wifi') => void;
  onDetailsClick: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: device.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };
  const borderColor = isSelected ? '#3B82F6' : '#E2E8F0';
  const IconComp = deviceIcons[iconIndex % deviceIcons.length] ?? LifeBuoy;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white rounded-xl flex flex-col flex-1 cursor-pointer hover:shadow-md transition-shadow"
      onClick={onSelect}
      onKeyDown={(e) => { if (e.key === 'Enter') onSelect(); }}
      role="button"
      tabIndex={0}
    >
      <div className="p-4 flex flex-col gap-3 flex-1" style={{ border: `1px solid ${borderColor}`, borderRadius: 12 }}>
        {/* Top Row */}
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className="w-[50px] h-[50px] rounded-[25px] bg-[#E6F0FA] flex items-center justify-center flex-shrink-0">
            <IconComp size={24} className="text-[#1A73E8]" />
          </div>

          {/* Info */}
          <div className="flex flex-col gap-1.5 flex-1 justify-center">
            <span className="text-[15px] font-bold text-[#0F172A]">{device.name}</span>
            {/* Status Row */}
            <div className="flex items-center gap-1.5">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  backgroundColor:
                    device.status === 'online' ? '#22C55E' : device.status === 'idle' ? '#F59E0B' : '#94A3B8',
                }}
              />
              <span className="text-xs text-[#64748B]">{getStatusText(device.status)}</span>
            </div>
            {/* Icons Row */}
            <div className="flex items-center gap-2">
              {device.connectionType === 'wifi' && <Wifi size={14} className="text-[#64748B]" />}
              {device.connectionType === 'bluetooth' && <Bluetooth size={14} className="text-[#64748B]" />}
              <span className="text-xs text-[#64748B]">
                {device.connectionType === 'wifi' ? 'WiFi' : device.connectionType === 'bluetooth' ? '蓝牙' : '无连接'}
              </span>
            </div>
          </div>

          {/* Drag Handle + Select Check */}
          <div className="flex items-center gap-1 flex-shrink-0">
            {isSelected && (
              <div className="w-[22px] h-[22px] rounded-[11px] bg-[#3B82F6] flex items-center justify-center">
                <Check size={14} className="text-white" />
              </div>
            )}
            <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing p-1" onClick={(e) => e.stopPropagation()}>
              <GripVertical size={16} className="text-[#94A3B8]" />
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="h-px bg-[#F1F5F9]" />

        {/* Bottom Row — metrics */}
        <div className="flex justify-between">
          {[
            {
              label: '藻毒素',
              value: device.status === 'offline' ? '-- µg/L' : `${device.toxinUgL.toFixed(2)} µg/L`,
              color: device.status === 'offline' ? '#64748B' : getRiskColor(device.toxinUgL),
            },
            {
              label: '水温',
              value: device.status === 'offline' ? '-- ℃' : `${device.waterTempC.toFixed(1)} ℃`,
              color: '#0F172A',
            },
            {
              label: 'pH',
              value: device.status === 'offline' ? '--' : device.ph.toFixed(1),
              color: '#0F172A',
            },
          ].map((m) => (
            <div key={m.label} className="flex flex-col gap-1 flex-1">
              <span className="text-xs text-[#64748B]">{m.label}</span>
              <span className="text-[15px] font-bold" style={{ color: m.color }}>{m.value}</span>
            </div>
          ))}
        </div>

        {/* Connect buttons — offline devices */}
        {device.status === 'offline' && (
          <div className="flex gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); onConnectClick('bluetooth'); }}
              className="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg bg-[#E6F0FA] border border-[#1A73E8]/30 text-[#1A73E8] text-xs font-bold hover:bg-[#D0E5FA] transition-colors"
            >
              <Bluetooth size={14} />
              蓝牙连接
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onConnectClick('wifi'); }}
              className="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg bg-white border border-[#E2E8F0] text-[#0F172A] text-xs font-bold hover:bg-[#F8FAFC] transition-colors"
            >
              <Wifi size={14} />
              无线连接
            </button>
          </div>
        )}

        {/* Details button — only for connected devices */}
        {device.status !== 'offline' && (
          <button
            onClick={(e) => { e.stopPropagation(); onDetailsClick(); }}
            className="w-full h-10 rounded-lg bg-white border border-[#E2E8F0] text-sm font-medium text-[#0F172A] hover:bg-[#F8FAFC] hover:border-[#1A73E8]/30 transition-colors"
          >
            查看采样详情
          </button>
        )}
      </div>
    </div>
  );
}

/* ───── Page ───── */
export default function DevicePairingPage() {
  const [devices, setDevices] = useState<DeviceReading[]>(() => [...demoReadings]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [modal, setModal] = useState<{ show: boolean; title: string; message: string; loading: boolean }>({
    show: false, title: '', message: '', loading: false,
  });

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setDevices((items) => {
        const oldIndex = items.findIndex((d) => d.id === active.id);
        const newIndex = items.findIndex((d) => d.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  }

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  function handleConnect(device: DeviceReading, type: 'bluetooth' | 'wifi') {
    setModal({
      show: true,
      title: `正在建立 ${type === 'bluetooth' ? '蓝牙' : '无线'} 连接`,
      message: `正在连接设备 [${device.name}]，请保持采样终端在通讯范围内并等待握手响应...`,
      loading: true,
    });
    setTimeout(() => {
      setDevices((prev) =>
        prev.map((d) =>
          d.id === device.id
            ? { ...d, status: 'idle' as const, connectionType: type, signalDbm: type === 'wifi' ? -66 : -78, updatedAt: new Date().toISOString().replace('T', ' ').slice(0, 16) }
            : d,
        ),
      );
      setModal({ show: false, title: '', message: '', loading: false });
    }, 1200);
  }

  function handleDetails(device: DeviceReading) {
    setModal({
      show: true,
      title: '采样详情',
      message: [
        `设备：${device.name}`,
        `位置：${device.locationLabel}`,
        `藻毒素：${device.toxinUgL.toFixed(2)} µg/L`,
        `信号：${device.signalDbm} dBm`,
        `电量：${device.batteryPercent}%`,
        `水温：${device.waterTempC.toFixed(1)} °C`,
        `pH：${device.ph.toFixed(1)}`,
        `最后更新：${device.updatedAt}`,
      ].join('\n'),
      loading: false,
    });
  }

  function handleAddDevice() {
    setModal({ show: true, title: '搜索采样终端', message: '正在广播配对请求，请确保新设备处于配对状态。', loading: true });
    setTimeout(() => {
      const newDevice: DeviceReading = {
        id: `aq-${Date.now()}`,
        name: `临时采样点-${Math.floor(Math.random() * 1000)}`,
        status: 'offline',
        connectionType: 'none',
        locationLabel: '等待 GPS 定位',
        lat: 30.56 + Math.random() * 0.02,
        lng: 114.37 + Math.random() * 0.02,
        batteryPercent: 100,
        signalDbm: -92,
        toxinUgL: +((Math.random() * 1.2).toFixed(2)),
        waterTempC: 24.0,
        ph: 7.2,
        updatedAt: '未同步',
      };
      setDevices((prev) => [...prev, newDevice]);
      setModal({ show: false, title: '', message: '', loading: false });
    }, 1200);
  }

  return (
    <div className="flex gap-5 h-full">
      {/* ── Left Panel ── */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        {/* Action Row */}
        <div className="flex items-center gap-3 h-10 flex-shrink-0">
          <button
            onClick={handleAddDevice}
            className="flex items-center gap-1.5 h-10 px-5 rounded-lg bg-[#1A73E8] text-white text-sm font-bold hover:bg-[#1557B0] transition-colors"
          >
            <Plus size={16} />
            添加设备
          </button>
          <button className="flex items-center gap-1.5 h-10 px-5 rounded-lg bg-white border border-[#E2E8F0] text-sm text-[#0F172A] hover:bg-[#F8FAFC] transition-colors">
            <RefreshCw size={16} />
            刷新列表
          </button>
          <button className="flex items-center gap-1 h-10 px-5 rounded-lg bg-white border border-[#E2E8F0] text-sm text-[#0F172A] hover:bg-[#F8FAFC] transition-colors">
            批量操作 <ChevronDown size={16} />
          </button>
          <div className="flex-1" />
        </div>

        {/* Card Grid — scrollable */}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={devices.map((d) => d.id)} strategy={rectSortingStrategy}>
            <div className="flex-1 overflow-y-auto flex flex-col gap-4">
              {Array.from({ length: Math.ceil(devices.length / 3) }).map((_, rowIdx) => (
                <div key={rowIdx} className="flex gap-4" style={{ minHeight: 220 }}>
                  {devices.slice(rowIdx * 3, rowIdx * 3 + 3).map((device, i) => (
                    <DeviceCard
                      key={device.id}
                      device={device}
                      iconIndex={rowIdx * 3 + i}
                      isSelected={selectedIds.has(device.id)}
                      onSelect={() => toggleSelect(device.id)}
                      onConnectClick={(type) => handleConnect(device, type)}
                      onDetailsClick={() => handleDetails(device)}
                    />
                  ))}
                </div>
              ))}
            </div>
          </SortableContext>
        </DndContext>

        {/* Drop Zone */}
        <div className="flex items-center justify-center gap-2 h-[72px] rounded-xl bg-[#F0F7FF] border-2 border-dashed border-[#93C5FD] text-sm text-[#475569] font-medium flex-shrink-0">
          <GripVertical size={20} className="text-[#475569]" />
          拖拽设备卡片可调整顺序
        </div>
      </div>

      {/* ── Right Panel ── */}
      <div className="w-[420px] bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 flex-shrink-0 overflow-y-auto">
        <h2 className="text-lg font-bold text-[#0F172A]">添加新设备</h2>
        <p className="text-sm text-[#475569]">扫描附近设备</p>

        <RadarScanner />

        <h4 className="text-sm font-semibold text-[#0F172A]">已发现设备 (2)</h4>

        {/* Discovered Device 1 */}
        <div className="flex items-center justify-between p-3 rounded-[10px] border border-[#E2E8F0]">
          <div className="flex flex-col gap-1">
            <span className="text-sm font-bold text-[#0F172A]">WaterProbe-7F2A</span>
            <span className="text-xs text-[#64748B]">RSSI -48 dBm</span>
          </div>
          <button className="flex items-center justify-center rounded-md bg-[#1A73E8] text-white text-xs font-bold hover:bg-[#1557B0] transition-colors" style={{ padding: '6px 14px' }}>
            蓝牙配对
          </button>
        </div>

        {/* Discovered Device 2 */}
        <div className="flex items-center justify-between p-3 rounded-[10px] border border-[#E2E8F0]">
          <div className="flex flex-col gap-1">
            <span className="text-sm font-bold text-[#0F172A]">Buoy-3C91</span>
            <span className="text-xs text-[#64748B]">RSSI -62 dBm</span>
          </div>
          <button className="flex items-center justify-center rounded-md bg-white border border-[#1A73E8] text-[#1A73E8] text-xs font-bold hover:bg-[#F0F7FF] transition-colors" style={{ padding: '6px 14px' }}>
            WiFi连接
          </button>
        </div>

        {/* Decoration placeholder */}
        <div className="flex-1 min-h-[80px]" />
        <div className="flex gap-2">
          <div className="flex-1 h-[100px] border border-dashed border-[#E2E8F0] rounded-lg flex items-center justify-center text-[10px] text-[#64748B]">
            [海藻装饰]
          </div>
          <div className="flex-1 h-[100px] border border-dashed border-[#E2E8F0] rounded-lg flex items-center justify-center text-[10px] text-[#64748B]">
            [研究员吉祥物]
          </div>
        </div>
      </div>

      {/* ── Modal ── */}
      {modal.show && (
        <Modal
          title={modal.title}
          message={modal.message}
          loading={modal.loading}
          onClose={() => setModal({ show: false, title: '', message: '', loading: false })}
        />
      )}
    </div>
  );
}
