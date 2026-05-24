import { useState } from 'react';
import { Plus, RefreshCw, ChevronDown, GripVertical, LifeBuoy, Thermometer, Scan, Wifi, Bluetooth, Check, X } from 'lucide-react';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { SortableContext, useSortable, rectSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { arrayMove } from '@dnd-kit/sortable';
import { demoReadings, getRiskColor, getStatusText } from '../data/demoReadings';
import type { DeviceReading } from '../types/domain';

const iconMap: Record<string, React.ReactNode> = {
  LifeBuoy: <LifeBuoy size={24} className="text-[#1A73E8]" />,
  Thermometer: <Thermometer size={24} className="text-[#1A73E8]" />,
  Scan: <Scan size={24} className="text-[#1A73E8]" />,
};

const deviceIcons = ['LifeBuoy', 'Thermometer', 'Scan', 'LifeBuoy', 'Thermometer', 'Scan'];

function DeviceCard({ device, index }: { device: DeviceReading; index: number }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: device.id });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-white rounded-xl border border-[#E2E8F0] p-4 flex flex-col gap-3 flex-1"
    >
      {/* Top Row */}
      <div className="flex items-start gap-3">
        <div className="w-[50px] h-[50px] rounded-[25px] bg-[#E6F0FA] flex items-center justify-center flex-shrink-0">
          {iconMap[deviceIcons[index % deviceIcons.length]] ?? <LifeBuoy size={24} className="text-[#1A73E8]" />}
        </div>
        <div className="flex flex-col gap-1.5 flex-1">
          <span className="text-[15px] font-bold text-[#0F172A]">{device.name}</span>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: device.status === 'online' ? '#22C55E' : device.status === 'idle' ? '#F59E0B' : '#94A3B8' }} />
            <span className="text-xs text-[#64748B]">{getStatusText(device.status)}</span>
          </div>
          <div className="flex items-center gap-2">
            {device.connectionType === 'wifi' && <Wifi size={14} className="text-[#64748B]" />}
            {device.connectionType === 'bluetooth' && <Bluetooth size={14} className="text-[#64748B]" />}
            <span className="text-xs text-[#64748B]">{device.connectionType === 'wifi' ? 'WiFi' : device.connectionType === 'bluetooth' ? '蓝牙' : '无连接'}</span>
          </div>
        </div>
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing p-1">
          <GripVertical size={16} className="text-[#94A3B8]" />
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-[#F1F5F9]" />

      {/* Bottom Row */}
      <div className="flex justify-between">
        {[
          { label: '藻毒素', value: device.status === 'offline' ? '-- µg/L' : `${device.toxinUgL.toFixed(2)} µg/L`, color: device.status === 'offline' ? '#64748B' : getRiskColor(device.toxinUgL) },
          { label: '水温', value: device.status === 'offline' ? '-- ℃' : `${device.waterTempC.toFixed(1)} ℃`, color: '#0F172A' },
          { label: 'pH', value: device.status === 'offline' ? '--' : device.ph.toFixed(1), color: '#0F172A' },
        ].map((m) => (
          <div key={m.label} className="flex flex-col gap-1 flex-1">
            <span className="text-xs text-[#64748B]">{m.label}</span>
            <span className="text-[15px] font-bold" style={{ color: m.color }}>{m.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RadarScanner() {
  return (
    <div className="h-[260px] flex items-center justify-center relative">
      <div className="relative w-[200px] h-[200px]">
        <div className="absolute inset-0 rounded-full border border-[#E0F2FE]" />
        <div className="absolute inset-[25px] rounded-full border border-[#E0F2FE]" />
        <div className="absolute inset-[50px] rounded-full border border-[#E0F2FE]" />
        <div className="absolute inset-[75px] rounded-full border border-[#E0F2FE]" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-[#1A73E8] flex items-center justify-center animate-pulse">
            <Bluetooth size={32} className="text-white" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DevicePairingPage() {
  const [devices, setDevices] = useState<DeviceReading[]>(() => [...demoReadings]);
  const [showModal, setShowModal] = useState(false);
  const [modalState, setModalState] = useState<'loading' | 'done' | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
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

  function handleAddDevice() {
    setShowModal(true);
    setModalState('loading');
    setTimeout(() => {
      setModalState('done');
      const newDevice: DeviceReading = {
        id: `aq-${Date.now()}`,
        name: `新设备-${devices.length + 1}`,
        status: 'idle',
        connectionType: 'bluetooth',
        locationLabel: '待定位',
        lat: 30.56 + Math.random() * 0.02,
        lng: 114.37 + Math.random() * 0.02,
        batteryPercent: 100,
        signalDbm: -50,
        toxinUgL: 0,
        waterTempC: 25.0,
        ph: 7.0,
        updatedAt: new Date().toISOString().replace('T', ' ').slice(0, 16),
      };
      setTimeout(() => {
        setDevices((prev) => [...prev, newDevice]);
        setShowModal(false);
        setModalState(null);
      }, 800);
    }, 1200);
  }

  return (
    <div className="flex gap-5 h-full">
      {/* Left Panel */}
      <div className="flex-1 flex flex-col gap-4">
        {/* Actions */}
        <div className="flex items-center gap-3 h-10">
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

        {/* Device Grid */}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={devices.map(d => d.id)} strategy={rectSortingStrategy}>
            <div className="flex-1 flex flex-col gap-4 overflow-y-auto">
              <div className="flex gap-4" style={{ minHeight: 220 }}>
                {devices.slice(0, 3).map((device, i) => (
                  <DeviceCard key={device.id} device={device} index={i} />
                ))}
              </div>
              <div className="flex gap-4" style={{ minHeight: 220 }}>
                {devices.slice(3, 6).map((device, i) => (
                  <DeviceCard key={device.id} device={device} index={i + 3} />
                ))}
              </div>
            </div>
          </SortableContext>
        </DndContext>

        {/* Drop Zone Hint */}
        <div className="flex items-center justify-center gap-2 h-[72px] rounded-xl bg-[#F0F7FF] border-2 border-dashed border-[#93C5FD] text-sm text-[#475569] font-medium flex-shrink-0">
          <GripVertical size={20} className="text-[#475569]" />
          拖拽设备卡片可调整顺序
        </div>
      </div>

      {/* Right Panel - Pairing */}
      <div className="w-[420px] bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 flex-shrink-0">
        <h2 className="text-lg font-bold text-[#0F172A]">添加新设备</h2>
        <p className="text-sm text-[#475569]">扫描附近设备</p>
        <RadarScanner />
        <h4 className="text-sm font-semibold text-[#0F172A]">已发现设备 (2)</h4>
        {/* Discovered devices */}
        <div className="flex items-center justify-between p-3 rounded-[10px] border border-[#E2E8F0]">
          <div className="flex flex-col gap-1">
            <span className="text-sm font-bold text-[#0F172A]">WaterProbe-7F2A</span>
            <span className="text-xs text-[#64748B]">RSSI -48 dBm</span>
          </div>
          <button className="flex items-center justify-center h-7 px-3 rounded-md bg-[#1A73E8] text-white text-xs font-bold hover:bg-[#1557B0] transition-colors">
            蓝牙配对
          </button>
        </div>
        <div className="flex items-center justify-between p-3 rounded-[10px] border border-[#E2E8F0]">
          <div className="flex flex-col gap-1">
            <span className="text-sm font-bold text-[#0F172A]">Buoy-3C91</span>
            <span className="text-xs text-[#64748B]">RSSI -62 dBm</span>
          </div>
          <button className="flex items-center justify-center h-7 px-3 rounded-md bg-white border border-[#1A73E8] text-[#1A73E8] text-xs font-bold hover:bg-[#F0F7FF] transition-colors">
            WiFi连接
          </button>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-8 w-[380px] flex flex-col items-center gap-4 shadow-xl">
            {modalState === 'loading' ? (
              <>
                <div className="w-12 h-12 border-4 border-[#E6F0FA] border-t-[#1A73E8] rounded-full animate-spin" />
                <h3 className="text-lg font-bold text-[#0F172A]">正在扫描附近设备...</h3>
                <p className="text-sm text-[#64748B] text-center">请确保设备已开启蓝牙或WiFi功能</p>
                <button
                  onClick={() => { setShowModal(false); setModalState(null); }}
                  className="h-10 px-6 rounded-lg border border-[#E2E8F0] text-sm text-[#0F172A] mt-2"
                >
                  取消
                </button>
              </>
            ) : (
              <>
                <div className="w-12 h-12 rounded-full bg-[#22C55E1A] flex items-center justify-center">
                  <Check size={24} className="text-[#22C55E]" />
                </div>
                <h3 className="text-lg font-bold text-[#0F172A]">发现新设备</h3>
                <p className="text-sm text-[#64748B] text-center">已成功添加设备到监测列表</p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
