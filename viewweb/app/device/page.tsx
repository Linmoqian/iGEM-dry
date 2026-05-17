'use client';

import { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { DeviceStatus, DeviceStatusProps } from '../components/DeviceStatus';
import { demoReadings, DeviceReading } from '../lib/demoReadings';

function toDeviceProps(reading: DeviceReading): DeviceStatusProps & { id: string } {
  return {
    id: reading.id,
    deviceName: reading.name,
    status: reading.status,
    location: reading.locationLabel,
    battery: reading.batteryPercent,
    signalDbm: reading.signalDbm,
    toxinUgL: reading.toxinUgL,
    waterTempC: reading.waterTempC,
    ph: reading.ph,
    updatedAt: reading.updatedAt,
    connectionType: reading.connectionType,
  };
}

const SortableDevice = ({ id, ...props }: DeviceStatusProps & { id: string }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 1,
    opacity: isDragging ? 0.8 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="h-full">
      <DeviceStatus
        {...props}
        dragHandleProps={{ ...attributes, ...listeners }}
      />
    </div>
  );
};

export default function DevicePage() {
  const [devices, setDevices] = useState<(DeviceStatusProps & { id: string })[]>(
    demoReadings.map(toDeviceProps)
  );

  const [activeModal, setActiveModal] = useState<{
    show: boolean;
    title: string;
    message: string;
    loading: boolean;
  }>({ show: false, title: '', message: '', loading: false });

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setDevices((items) => {
        const oldIndex = items.findIndex(item => item.id === active.id);
        const newIndex = items.findIndex(item => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const showModal = (title: string, message: string, loading: boolean = false) => {
    setActiveModal({ show: true, title, message, loading });
  };

  const handleConnect = (id: string, type: 'bluetooth' | 'wifi') => {
    showModal(
      `正在建立 ${type === 'bluetooth' ? '蓝牙' : '无线'} 连接`,
      `正在连接设备 [${id}]，请保持采样终端在通讯范围内并等待握手响应...`,
      true
    );

    setTimeout(() => {
      setDevices(current =>
        current.map(dev =>
          dev.id === id
            ? {
                ...dev,
                status: 'idle',
                connectionType: type,
                location: '等待重新定位',
                signalDbm: type === 'wifi' ? -66 : -78,
                updatedAt: '刚刚',
              }
            : dev
        )
      );
      setActiveModal({ show: false, title: '', message: '', loading: false });
    }, 1200);
  };

  const handleDetails = (device: DeviceStatusProps) => {
    showModal(
      '采样详情',
      `设备：${device.deviceName}\n位置：${device.location}\n藻毒素：${device.toxinUgL.toFixed(2)} µg/L\n信号：${device.signalDbm} dBm\n电量：${device.battery}%\n水温：${device.waterTempC.toFixed(1)} °C\npH：${device.ph.toFixed(1)}`,
      false
    );
  };

  const handleAddDevice = () => {
    showModal('搜索采样终端', '正在广播配对请求，请确保新设备处于配对状态。', true);

    setTimeout(() => {
      const newId = `aq-${Date.now()}`;
      const newDevice: DeviceStatusProps & { id: string } = {
        id: newId,
        deviceName: `临时采样点-${Math.floor(Math.random() * 1000)}`,
        status: 'offline',
        location: '等待 GPS 定位',
        battery: 100,
        signalDbm: -92,
        toxinUgL: Number((Math.random() * 1.2).toFixed(2)),
        waterTempC: 24.0,
        ph: 7.2,
        updatedAt: '未同步',
        connectionType: 'none',
      };
      setDevices(prev => [...prev, newDevice]);
      setActiveModal({ show: false, title: '', message: '', loading: false });
    }, 1200);
  };

  return (
    <div className="flex flex-col items-center py-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      {activeModal.show && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#050714]/80 backdrop-blur-md animate-in fade-in duration-200 px-4">
          <div className="bg-[#0f172a] border border-cyan-500/50 rounded-2xl p-8 max-w-md w-full shadow-[0_0_40px_rgba(34,211,238,0.15)] flex flex-col items-center text-center">
            {activeModal.loading ? (
              <div className="w-12 h-12 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin mb-6 shadow-[0_0_15px_currentColor]"></div>
            ) : (
              <svg className="w-12 h-12 mb-6 text-emerald-400 drop-shadow-[0_0_8px_currentColor]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            )}
            <h3 className="text-xl font-bold text-slate-100 mb-3 tracking-wider">{activeModal.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed whitespace-pre-wrap">{activeModal.message}</p>
            <button
              onClick={() => setActiveModal({ show: false, title: '', message: '', loading: false })}
              className="mt-8 px-8 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 rounded-lg text-sm font-bold tracking-widest transition-all"
            >
              {activeModal.loading ? '中断连接' : '确认'}
            </button>
          </div>
        </div>
      )}

      <div className="text-center mb-12 relative pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-blue-500/20 blur-[80px] -z-10 rounded-full"></div>
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-500 mb-3 drop-shadow-[0_0_8px_rgba(34,211,238,0.3)]">
          采样设备连接与监控
        </h1>
        <p className="text-lg text-slate-400 font-medium max-w-3xl mx-auto">
          管理水体采样终端，跟踪电量、信号强度、藻毒素浓度和最新采样状态。
        </p>
      </div>

      <div className="w-full max-w-7xl">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={devices.map(d => d.id)}
            strategy={rectSortingStrategy}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
              {devices.map(device => (
                <SortableDevice
                  key={device.id}
                  {...device}
                  onConnectClick={(type) => handleConnect(device.id, type)}
                  onDetailsClick={() => handleDetails(device)}
                />
              ))}

              <div
                onClick={handleAddDevice}
                className="bg-[#0f172a]/50 backdrop-blur border border-dashed border-slate-700/80 rounded-2xl p-6 flex flex-col items-center justify-center text-slate-500 hover:text-cyan-400 hover:bg-[#0f172a]/80 hover:border-cyan-500/50 hover:shadow-[0_0_20px_rgba(34,211,238,0.15)] transition-all cursor-pointer min-h-[360px] h-full group"
              >
                <div className="w-16 h-16 rounded-full bg-slate-800/50 group-hover:bg-cyan-500/10 flex items-center justify-center mb-4 transition-colors">
                  <svg className="w-8 h-8 group-hover:scale-110 transition-transform duration-300 drop-shadow-md" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <span className="font-bold tracking-[0.2em] text-sm uppercase">接入新采样终端</span>
              </div>
            </div>
          </SortableContext>
        </DndContext>
      </div>
    </div>
  );
}
