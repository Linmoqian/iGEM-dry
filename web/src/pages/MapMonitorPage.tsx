import { useState } from 'react';
import { BarChart3, Battery, Beaker, Crosshair, Droplets, MapPin, RadioTower, Signal, Thermometer, UserRound } from 'lucide-react';
import { demoReadings, getRiskColor, getRiskLabel, getStatusText } from '../data/demoReadings';
import { materials } from '../data/materials';
import type { DeviceReading } from '../types/domain';

const markerPositions: Record<string, { left: number; top: number }> = {
  'aq-006': { left: 62, top: 56 },
  'aq-002': { left: 44, top: 47 },
  'aq-003': { left: 26, top: 46 },
  'aq-001': { left: 31, top: 61 },
  'aq-004': { left: 72, top: 51 },
  'aq-007': { left: 55, top: 74 },
  'aq-008': { left: 36, top: 35 },
  'aq-010': { left: 78, top: 35 },
  'aq-011': { left: 18, top: 61 },
  'aq-012': { left: 51, top: 34 },
  'aq-013': { left: 18, top: 76 },
};

function MapLabel({ children, left, top }: { children: string; left: number; top: number }) {
  return (
    <span className="absolute rounded bg-white/40 px-1 text-[18px] font-semibold text-[#53657a] drop-shadow-sm" style={{ left: `${left}%`, top: `${top}%` }}>
      {children}
    </span>
  );
}

function DeviceMarker({ device, selected, onClick }: { device: DeviceReading; selected: boolean; onClick: () => void }) {
  const position = markerPositions[device.id];
  if (!position || device.status === 'offline') return null;
  const color = getRiskColor(device.toxinUgL);

  return (
    <button
      className="absolute z-20 -translate-x-1/2 -translate-y-1/2"
      style={{ left: `${position.left}%`, top: `${position.top}%` }}
      type="button"
      onClick={onClick}
      title={device.name}
    >
      <span className="relative flex h-[66px] w-[54px] items-start justify-center">
        <span
          className="absolute bottom-[7px] h-[12px] w-[32px] rounded-full opacity-70"
          style={{ background: selected ? color : '#143a55' }}
        />
        <span
          className="flex h-[52px] w-[42px] items-center justify-center rounded-[22px_22px_24px_24px] border-[4px] border-white text-white shadow-[0_8px_18px_rgba(16,55,95,0.28)]"
          style={{ background: color, outline: selected ? `4px solid ${color}55` : 'none' }}
        >
          <Beaker size={24} />
        </span>
        <span className="absolute bottom-[11px] h-[16px] w-[16px] rotate-45 border-b-[4px] border-r-[4px] border-white" style={{ background: color }} />
      </span>
    </button>
  );
}

function MapCanvas({ selected, onSelect }: { selected: DeviceReading; onSelect: (device: DeviceReading) => void }) {
  return (
    <section className="aqua-panel relative flex-1 overflow-hidden p-3">
      <div className="relative h-full overflow-hidden rounded-[12px] border border-[#c7e0f6] bg-[#c4eefd]">
        <div className="absolute inset-0 bg-[linear-gradient(22deg,rgba(255,255,255,.55)_1px,transparent_1px),linear-gradient(112deg,rgba(255,255,255,.5)_1px,transparent_1px)] bg-[length:86px_86px,110px_110px] opacity-70" />
        <div className="absolute -left-[6%] top-[5%] h-[88%] w-[34%] rotate-[-10deg] rounded-[45%] bg-[#f7eddc]/80 shadow-[0_0_0_16px_rgba(255,255,255,.16)]" />
        <div className="absolute right-[-10%] top-[7%] h-[82%] w-[37%] rotate-[12deg] rounded-[45%] bg-[#dfeccb]/85 shadow-[0_0_0_18px_rgba(255,255,255,.16)]" />
        <div className="absolute bottom-[-15%] left-[10%] h-[34%] w-[70%] rounded-[50%] bg-[#dff1cf]/70" />
        <div className="absolute inset-[2%] rounded-[48%] bg-[#7bcff2]/55" />
        <div className="absolute left-[18%] top-[16%] h-[72%] w-[64%] rounded-[48%] bg-[#83daf4]/70 blur-[1px]" />
        <div className="absolute left-[31%] top-[22%] h-[55%] w-[48%] rounded-[50%] bg-[radial-gradient(circle_at_48%_45%,rgba(239,25,25,.72)_0,rgba(255,107,70,.68)_25%,rgba(255,224,87,.62)_43%,rgba(154,231,206,.46)_61%,rgba(124,213,246,.18)_78%,transparent_100%)] blur-[12px]" />
        <div className="absolute left-[36%] top-[30%] h-[42%] w-[36%] rounded-[50%] bg-[radial-gradient(circle,rgba(239,25,25,.45),rgba(255,190,64,.32)_42%,transparent_75%)] blur-[22px]" />

        <MapLabel left={8} top={17}>东湖西路</MapLabel>
        <MapLabel left={34} top={11}>湖光湾区</MapLabel>
        <MapLabel left={76} top={39}>东湖生态旅游风景区</MapLabel>
        <MapLabel left={80} top={80}>落雁景区</MapLabel>
        <MapLabel left={14} top={84}>楚风园</MapLabel>

        <div className="absolute left-5 top-5 z-30 flex flex-col overflow-hidden rounded-[10px] bg-white/90 shadow">
          {['+', '−'].map((item) => (
            <button key={item} className="h-12 w-12 border-b border-[#d7e7f4] text-[28px] font-semibold last:border-0" type="button">
              {item}
            </button>
          ))}
          <button className="flex h-12 w-12 items-center justify-center" type="button">
            <Crosshair size={24} />
          </button>
        </div>

        <div className="absolute left-[42%] top-8 z-30 flex gap-4">
          <button className="flex h-[55px] items-center gap-3 rounded-[16px] bg-white/90 px-8 text-[20px] font-semibold shadow" type="button">
            <RadioTower size={24} />
            设备图层
          </button>
          <button className="flex h-[55px] items-center gap-3 rounded-[16px] bg-white/95 px-8 text-[20px] font-semibold text-[#0874ed] shadow" type="button">
            <Droplets size={24} />
            热力图层
          </button>
        </div>

        {demoReadings.map((device) => (
          <DeviceMarker key={device.id} device={device} selected={selected.id === device.id} onClick={() => onSelect(device)} />
        ))}

        <div className="absolute bottom-8 left-7 z-30 flex h-[86px] items-center gap-10 rounded-[4px] bg-white/92 px-8 shadow-[0_8px_24px_rgba(49,103,157,.15)]">
          <b className="text-[18px]">风险图例 <span className="font-normal text-[#344054]">（藻毒素浓度 μg/L）</span></b>
          {[
            ['#059669', '正常  < 0.5'],
            ['#f5c400', '关注  0.5 - 1.0'],
            ['#f97316', '警戒  1.0 - 5.0'],
            ['#ef1919', '高风险  > 5.0'],
          ].map(([color, label]) => (
            <span key={label} className="flex items-center gap-3 text-[17px]">
              <span className="h-5 w-5 rounded-full" style={{ background: color }} />
              {label}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function SelectedDevicePanel({ device }: { device: DeviceReading }) {
  return (
    <aside className="aqua-panel relative w-[420px] shrink-0 overflow-hidden px-6 py-6">
      <img className="pointer-events-none absolute -bottom-7 right-0 w-[190px] opacity-85" src={materials.mascotHero} alt="" />
      <div className="relative z-10">
        <p className="mb-4 text-[18px] font-semibold text-[#344054]">选中设备</p>
        <div className="flex items-center gap-3">
          <h1 className="text-[25px] font-black">{device.name}</h1>
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: getRiskColor(device.toxinUgL) }} />
          <b className="text-[17px]" style={{ color: getRiskColor(device.toxinUgL) }}>
            {getRiskLabel(device.toxinUgL)}
          </b>
        </div>
        <div className="mt-4 flex items-center gap-2 text-[17px] font-semibold text-[#078b4f]">
          <span className="h-3 w-3 rounded-full bg-[#078b4f]" />
          {getStatusText(device.status)}
        </div>

        <div className="aqua-panel mt-6 px-6 py-6 shadow-none">
          <span className="text-[17px] text-[#344054]">藻毒素浓度</span>
          <div className="mt-4 flex items-end gap-3">
            <b className="text-[48px] leading-none" style={{ color: getRiskColor(device.toxinUgL) }}>
              {device.toxinUgL.toFixed(2)}
            </b>
            <span className="pb-1 text-[20px]">μg/L</span>
          </div>
          <div className="mt-6 flex justify-between text-[16px]">
            <span>更新时间</span>
            <span>{device.updatedAt}</span>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-4">
          {[
            { icon: Battery, label: '电量', value: `${device.batteryPercent} %`, color: '#078b4f' },
            { icon: Signal, label: '信号强度', value: `${device.signalDbm} dBm`, color: '#078b4f' },
            { icon: Thermometer, label: '水温', value: `${device.waterTempC.toFixed(1)} °C`, color: '#0874ed' },
            { icon: Beaker, label: 'pH', value: device.ph.toFixed(1), color: '#0874ed' },
          ].map((item) => (
            <div key={item.label} className="aqua-panel flex h-[105px] flex-col justify-center gap-2 px-5 shadow-none">
              <span className="flex items-center gap-3 text-[17px]">
                <item.icon size={22} style={{ color: item.color }} />
                {item.label}
              </span>
              <b className="text-[25px]">{item.value}</b>
            </div>
          ))}
        </div>

        <div className="aqua-panel mt-5 flex flex-col gap-4 px-5 py-4 text-[16px] shadow-none">
          <div className="flex justify-between">
            <span className="flex items-center gap-2"><UserRound size={19} />位置</span>
            <span>{device.locationLabel}</span>
          </div>
          <div className="flex justify-between">
            <span className="flex items-center gap-2"><Droplets size={19} />设备类型</span>
            <span>预警浮标</span>
          </div>
          <div className="flex justify-between">
            <span className="flex items-center gap-2"><MapPin size={19} />备注</span>
            <span>东湖湖心浮标点</span>
          </div>
        </div>

        <button className="mt-7 flex h-[58px] w-[260px] items-center justify-center gap-3 rounded-[10px] bg-[#0874ed] text-[20px] font-bold text-white" type="button">
          <BarChart3 size={24} />
          查看历史数据
        </button>
      </div>
    </aside>
  );
}

export default function MapMonitorPage() {
  const [selected, setSelected] = useState<DeviceReading>(demoReadings[0]);

  return (
    <div className="flex h-full gap-5">
      <MapCanvas selected={selected} onSelect={setSelected} />
      <SelectedDevicePanel device={selected} />
    </div>
  );
}
