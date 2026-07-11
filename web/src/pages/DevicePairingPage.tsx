import { useState } from 'react';
import { Battery, Bluetooth, Check, ChevronDown, GripVertical, Plus, RefreshCw, Search, ShieldCheck, Wifi } from 'lucide-react';
import { demoReadings, getRiskColor, getStatusText } from '../data/demoReadings';
import { materials } from '../data/materials';
import type { DeviceReading } from '../types/domain';

const deviceImages = [
  materials.deviceBuoy,
  materials.deviceProbe,
  materials.deviceAnchor,
  materials.deviceBuoy,
  materials.deviceTube,
  materials.deviceOld,
];

function ToolbarButton({
  children,
  active = false,
}: {
  children: React.ReactNode;
  active?: boolean;
}) {
  return (
    <button
      className={`flex h-[54px] items-center gap-3 rounded-[10px] px-7 text-[18px] font-semibold ${active ? 'bg-[#0874ed] text-white' : 'border border-[#bfdcf3] bg-white/86 text-[#12203a]'}`}
      type="button"
    >
      {children}
    </button>
  );
}

function DeviceCard({
  device,
  index,
  selected,
  onSelect,
}: {
  device: DeviceReading;
  index: number;
  selected: boolean;
  onSelect: () => void;
}) {
  const offline = device.status === 'offline';
  const statusColor = device.status === 'online' ? '#078b4f' : device.status === 'idle' ? '#f97316' : '#6b7280';

  return (
    <button
      className={`aqua-panel relative flex h-[230px] flex-col px-6 py-5 text-left transition ${selected ? 'border-[#0874ed] shadow-[0_0_0_1px_#0874ed]' : ''} ${offline ? 'grayscale' : ''}`}
      type="button"
      onClick={onSelect}
    >
      {selected ? (
        <span className="absolute right-5 top-5 flex h-8 w-8 items-center justify-center rounded-full bg-[#0874ed] text-white">
          <Check size={21} />
        </span>
      ) : null}
      <div className="flex gap-4">
        <img className="h-[86px] w-[86px] object-contain" src={deviceImages[index % deviceImages.length]} alt="" />
        <div className="min-w-0 pt-2">
          <h3 className="truncate text-[24px] font-black">{device.name}</h3>
          <p className="mt-3 flex items-center gap-2 text-[18px] font-semibold" style={{ color: statusColor }}>
            <span className="h-3 w-3 rounded-full" style={{ background: statusColor }} />
            {getStatusText(device.status)}
          </p>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-b border-[#d7e8f4] pb-4">
        <Wifi size={27} className={offline ? 'text-[#6b7280]' : 'text-[#078b4f]'} />
        <span className="flex items-center gap-2 text-[18px] font-semibold">
          <Battery size={29} className={offline ? 'text-[#6b7280]' : 'text-[#078b4f]'} />
          {offline ? '--' : `${device.batteryPercent}%`}
        </span>
      </div>

      <div className="mt-5 grid flex-1 grid-cols-3 divide-x divide-[#d7e8f4]">
        {[
          { label: '藻毒素', value: offline ? '-- μg/L' : `${device.toxinUgL.toFixed(2)} μg/L`, color: offline ? '#334155' : getRiskColor(device.toxinUgL) },
          { label: '水温', value: offline ? '-- °C' : `${device.waterTempC.toFixed(1)} °C`, color: '#111827' },
          { label: 'pH', value: offline ? '--' : device.ph.toFixed(1), color: '#111827' },
        ].map((item) => (
          <div key={item.label} className="flex flex-col justify-center gap-2 px-4 first:pl-0 last:pr-0">
            <span className="text-[17px] text-[#344054]">{item.label}</span>
            <b className="text-[24px]" style={{ color: item.color }}>
              {item.value}
            </b>
          </div>
        ))}
      </div>
    </button>
  );
}

function RadarScanner() {
  return (
    <div className="relative mx-auto mt-8 h-[300px] w-[300px]">
      <div className="absolute inset-0 rounded-full border border-[#a9d8fb]" />
      <div className="absolute inset-[34px] rounded-full border border-[#c2e3fa]" />
      <div className="absolute inset-[68px] rounded-full border border-[#d7ecfb]" />
      <div className="absolute inset-[102px] rounded-full border border-[#e3f2fd]" />
      <div className="absolute left-1/2 top-0 h-full w-px bg-[#d1e8f8]" />
      <div className="absolute left-0 top-1/2 h-px w-full bg-[#d1e8f8]" />
      <div className="absolute left-[36px] top-[54px] h-2 w-2 rounded-full bg-[#36a6f2]" />
      <div className="absolute right-[52px] top-[75px] h-2 w-2 rounded-full bg-[#0874ed]" />
      <div className="absolute bottom-[58px] left-[78px] h-2 w-2 rounded-full bg-[#0874ed]" />
      <div className="absolute left-1/2 top-1/2 flex h-[74px] w-[74px] -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-[#0874ed] text-white shadow-[0_0_0_20px_rgba(8,116,237,.1),0_0_28px_rgba(8,116,237,.45)]">
        <Bluetooth size={42} />
      </div>
    </div>
  );
}

function PairingPanel() {
  return (
    <aside className="aqua-panel relative w-[430px] shrink-0 overflow-hidden px-7 py-7">
      <h2 className="text-[24px] font-black">添加新设备</h2>
      <p className="mt-7 text-[20px] font-semibold">扫描附近设备</p>
      <RadarScanner />
      <div className="mt-4 flex items-center justify-between">
        <b className="text-[20px]">已发现设备（2）</b>
        <button className="flex items-center gap-2 text-[17px] font-semibold text-[#0874ed]" type="button">
          <RefreshCw size={19} />
          刷新
        </button>
      </div>
      <div className="mt-5 flex flex-col gap-4">
        {[
          ['WaterProbe-7F2A', 'RSSI  -48 dBm', '蓝牙配对', true],
          ['Buoy-3C91', 'RSSI  -62 dBm', 'WiFi连接', false],
        ].map(([name, rssi, action, primary]) => (
          <div key={name as string} className="aqua-panel flex h-[98px] items-center justify-between px-5 shadow-none">
            <div>
              <h3 className="text-[19px] font-semibold">{name}</h3>
              <p className="mt-2 text-[16px] text-[#5b6b81]">{rssi}</p>
            </div>
            <button className={`h-12 rounded-[8px] px-5 text-[18px] font-semibold ${primary ? 'bg-[#0874ed] text-white' : 'border border-[#9ccaf0] bg-white text-[#0874ed]'}`} type="button">
              {action}
            </button>
          </div>
        ))}
      </div>

      <div className="aqua-panel relative z-10 mt-6 bg-[#f5fbff] px-5 py-5 shadow-none">
        <h3 className="flex items-center gap-2 text-[20px] font-black text-[#0874ed]">
          <ShieldCheck size={24} />
          配对提示
        </h3>
        <p className="mt-3 max-w-[245px] text-[16px] leading-7 text-[#344054]">请确保设备处于可配对模式，且与本设备距离不超过 10 米。</p>
      </div>
      <img className="pointer-events-none absolute -bottom-4 right-0 z-0 w-[205px]" src={materials.mascotScientist} alt="" />
    </aside>
  );
}

export default function DevicePairingPage() {
  const [selectedId, setSelectedId] = useState(demoReadings[0].id);
  const devices = demoReadings.slice(0, 6);

  return (
    <div className="flex h-full gap-5">
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="mb-5 flex h-[54px] items-center gap-4">
          <ToolbarButton active>
            设备列表 <ChevronDown className="-rotate-90" size={22} />
          </ToolbarButton>
          <ToolbarButton>
            <RefreshCw size={22} />
            刷新列表
          </ToolbarButton>
          <ToolbarButton>
            视图模式 <ChevronDown size={22} />
          </ToolbarButton>
          <div className="ml-auto flex h-[54px] w-[260px] items-center gap-3 rounded-[10px] border border-[#bfdcf3] bg-white/86 px-5 text-[17px] text-[#71819a]">
            <Search size={22} />
            快速筛选
          </div>
          <button className="flex h-[54px] items-center gap-2 rounded-[10px] bg-[#0874ed] px-6 text-[18px] font-semibold text-white" type="button">
            <Plus size={25} />
            新增节点
          </button>
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-3 gap-5">
          {devices.map((device, index) => (
            <DeviceCard
              key={device.id}
              device={device}
              index={index}
              selected={selectedId === device.id}
              onSelect={() => setSelectedId(device.id)}
            />
          ))}
        </div>

        <div className="mt-6 flex h-[85px] shrink-0 items-center justify-center gap-4 rounded-[10px] border-2 border-dashed border-[#0874ed] bg-white/45 text-[22px] font-semibold text-[#53657a]">
          <GripVertical size={30} />
          拖拽设备卡片可调整顺序
        </div>
      </section>
      <PairingPanel />
    </div>
  );
}
