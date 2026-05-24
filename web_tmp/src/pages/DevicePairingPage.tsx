import { useState, useCallback } from 'react';
import { demoReadings } from '@/data/demoReadings';
import DeviceToolbar from '@/components/device/DeviceToolbar';
import DeviceCardGrid from '@/components/device/DeviceCardGrid';
import DeviceSortDropZone from '@/components/device/DeviceSortDropZone';
import PairingPanel from '@/components/device/PairingPanel';
import DeviceFormModal from '@/components/device/DeviceFormModal';
import type { DeviceItem, DeviceModalState, DiscoveredDevice } from '@/types/domain';

function toItem(r: typeof demoReadings[number]): DeviceItem {
  return { id: r.id, deviceName: r.name, status: r.status, location: r.locationLabel, battery: r.batteryPercent, signalDbm: r.signalDbm, toxinUgL: r.toxinUgL, waterTempC: r.waterTempC, ph: r.ph, updatedAt: r.updatedAt, connectionType: r.connectionType };
}

const DISC: DiscoveredDevice[] = [
  { name: 'WaterProbe-7F2A', rssi: -48, type: 'bluetooth' },
  { name: 'Buoy-3C91', rssi: -62, type: 'wifi' },
];

export default function DevicePairingPage() {
  const [devices, setDevices] = useState<DeviceItem[]>(demoReadings.map(toItem));
  const [modal, setModal] = useState<DeviceModalState>({ type: 'none' });
  const [editForm, setEditForm] = useState<Partial<DeviceItem>>({});
  const [scanning, setScanning] = useState(false);
  const [scanned, setScanned] = useState(false);

  const close = () => setModal({ type: 'none' });

  const handleConnect = useCallback((id: string, type: 'bluetooth' | 'wifi') => {
    setModal({ type: 'connecting', title: `正在建立 ${type === 'bluetooth' ? '蓝牙' : '无线'} 连接`, message: '正在连接设备，请保持采样终端在通讯范围内...', loading: true });
    setTimeout(() => { setDevices((p) => p.map((d) => d.id === id ? { ...d, status: 'idle' as const, connectionType: type, signalDbm: type === 'wifi' ? -66 : -78, updatedAt: '刚刚' } : d)); close(); }, 1200);
  }, []);

  const handleDisconnect = useCallback((id: string) => {
    setDevices((p) => p.map((d) => d.id === id ? { ...d, status: 'offline' as const, connectionType: 'none' as const } : d));
  }, []);

  const handleDetails = useCallback((d: DeviceItem) => setModal({ type: 'details', device: d }), []);
  const handleEdit = useCallback((d: DeviceItem) => { setEditForm({ ...d }); setModal({ type: 'edit', device: d }); }, []);
  const handleDelete = useCallback((d: DeviceItem) => setModal({ type: 'delete', device: d }), []);

  const handleSave = useCallback(() => {
    if (!modal.device) return;
    setDevices((p) => p.map((d) => d.id === modal.device!.id ? { ...d, ...editForm } : d)); close();
  }, [modal.device, editForm]);

  const handleConfirmDelete = useCallback(() => {
    if (!modal.device) return;
    setDevices((p) => p.filter((d) => d.id !== modal.device!.id)); close();
  }, [modal.device]);

  const handleScan = useCallback(() => { setScanning(true); setScanned(false); setTimeout(() => { setScanning(false); setScanned(true); }, 2000); }, []);

  const handlePair = useCallback((disc: DiscoveredDevice) => {
    setModal({ type: 'adding', title: `正在配对 ${disc.name}`, message: '正在建立连接并添加设备...', loading: true });
    setTimeout(() => {
      setDevices((p) => [...p, { id: `aq-${Date.now()}`, deviceName: disc.name, status: 'idle', location: '等待 GPS 定位', battery: 100, signalDbm: disc.rssi, toxinUgL: Number((Math.random() * 1.2).toFixed(2)), waterTempC: 24.0, ph: 7.2, updatedAt: '刚刚', connectionType: disc.type }]);
      close();
    }, 1000);
  }, []);

  return (
    <div className="flex flex-col">
      <DeviceToolbar onAdd={() => { setScanning(false); setScanned(false); }} onRefresh={() => setDevices(demoReadings.map(toItem))} />
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-5 items-start">
        <div>
          {devices.length > 0 ? (
            <>
              <DeviceCardGrid devices={devices} onDragEnd={setDevices} onConnect={handleConnect} onDisconnect={handleDisconnect} onDetails={handleDetails} onEdit={handleEdit} onDelete={handleDelete} />
              <DeviceSortDropZone />
            </>
          ) : (
            <div className="flex items-center justify-center h-52 rounded-2xl border-2 border-dashed border-[rgba(45,124,255,0.08)] bg-[rgba(45,124,255,0.02)]">
              <span className="text-[var(--color-muted)] text-sm">暂无配对设备</span>
            </div>
          )}
        </div>
        <PairingPanel isScanning={scanning} scanDone={scanned} discoveredDevices={scanned ? DISC : []} onStartScan={handleScan} onPair={handlePair} />
      </div>
      <DeviceFormModal modal={modal} editForm={editForm} onClose={close} onSave={handleSave} onDelete={handleConfirmDelete} onChange={(f, v) => setEditForm((p) => ({ ...p, [f]: v }))} />
    </div>
  );
}
