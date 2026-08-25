import { useCallback, useEffect, useMemo, useState } from 'react';
import L from 'leaflet';
import 'leaflet.heat';
import { Marker, MapContainer, TileLayer, Tooltip, useMap } from 'react-leaflet';
import {
  BarChart3,
  Battery,
  Crosshair,
  Droplets,
  Layers3,
  MapPin,
  RadioTower,
  Signal,
  Thermometer,
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { demoLake, demoReadings, getRiskColor, getRiskLabel, getRiskLevel, getStatusText } from '../data/demoReadings';
import { materials } from '../data/materials';
import { monitoringService } from '../services/monitoringService';
import type { DeviceReading } from '../types/domain';

function HeatLayer({ devices, visible }: { devices: DeviceReading[]; visible: boolean }) {
  const map = useMap();
  useEffect(() => {
    if (!visible) return undefined;
    const points = devices
      .filter((device) => device.status !== 'offline')
      .map((device) => [device.lat, device.lng, Math.max(.12, Math.min(1, device.toxinUgL / 6.5))] as L.HeatLatLngTuple);
    const layer = L.heatLayer(points, {
      radius: 74,
      blur: 46,
      maxZoom: 16,
      minOpacity: .42,
      gradient: { .12: '#2bb5ff', .35: '#79dfc6', .55: '#ffe35b', .75: '#ff8a35', 1: '#ef232b' },
    }).addTo(map);
    const redrawTimer = window.setTimeout(() => layer.redraw(), 40);
    return () => { window.clearTimeout(redrawTimer); map.removeLayer(layer); };
  }, [devices, map, visible]);
  return null;
}

function MapTools() {
  const map = useMap();
  return (
    <div className="absolute left-4 top-4 z-[600] flex flex-col overflow-hidden rounded-[9px] border border-[#c8dce9] bg-white/95 shadow">
      <button className="h-11 w-11 border-b border-[#d7e7f4] text-[25px]" type="button" aria-label="放大地图" onClick={() => map.zoomIn()}>+</button>
      <button className="h-11 w-11 border-b border-[#d7e7f4] text-[25px]" type="button" aria-label="缩小地图" onClick={() => map.zoomOut()}>−</button>
      <button className="flex h-11 w-11 items-center justify-center" type="button" aria-label="回到东湖监测区" onClick={() => map.setView(demoLake.center, 14)}><Crosshair size={20} /></button>
    </div>
  );
}

function SelectedFollower({ device }: { device?: DeviceReading }) {
  const map = useMap();
  useEffect(() => {
    if (device) map.flyTo([device.lat, device.lng], Math.max(map.getZoom(), 14), { duration: .6 });
  }, [device, map]);
  return null;
}

function markerIcon(device: DeviceReading, selected: boolean) {
  const label = getRiskLevel(device.toxinUgL) === 'critical' ? '!' : '●';
  return L.divIcon({
    className: '',
    html: `<div class="device-map-marker${selected ? ' selected' : ''}" style="background:${getRiskColor(device.toxinUgL)}"><span>${label}</span></div>`,
    iconSize: [38, 46],
    iconAnchor: [19, 42],
  });
}

function RiskLegend() {
  const items = [
    ['#059669', '正常', '< 0.5 μg/L'], ['#f5b400', '关注', '0.5 - 1.0 μg/L'],
    ['#f97316', '警戒', '1.0 - 5.0 μg/L'], ['#ef232b', '高风险', '> 5.0 μg/L'],
  ];
  return (
    <div className="absolute bottom-4 left-4 right-4 z-[600] flex min-h-[72px] items-center gap-7 rounded-[12px] border border-[#c7def0] bg-white/95 px-5 shadow-[0_8px_24px_rgba(49,103,157,.16)] backdrop-blur-sm">
      <b className="whitespace-nowrap text-[15px]">风险图例</b>
      <div className="grid flex-1 grid-cols-4 gap-4">
        {items.map(([color, label, range]) => <span key={label} className="flex items-center gap-2 text-[13px]"><span className="h-4 w-4 shrink-0 rounded-full" style={{ background: color }} /><b>{label}</b><span className="text-[#506076]">{range}</span></span>)}
      </div>
    </div>
  );
}

function LakeMap({ devices, selected, onSelect }: { devices: DeviceReading[]; selected?: DeviceReading; onSelect: (device: DeviceReading) => void }) {
  const [deviceLayer, setDeviceLayer] = useState(true);
  const [heatLayer, setHeatLayer] = useState(true);
  return (
    <section className="aqua-panel relative min-w-0 flex-1 overflow-hidden p-3">
      <div className="relative h-full overflow-hidden rounded-[12px] border border-[#c7e0f6] bg-[#c4eefd]">
        <MapContainer center={demoLake.center} zoom={14} minZoom={12} maxZoom={18} zoomControl={false} preferCanvas>
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            eventHandlers={{ tileerror: () => undefined }}
          />
          <HeatLayer devices={devices} visible={heatLayer} />
          <SelectedFollower device={selected} />
          {deviceLayer ? devices.filter((device) => device.status !== 'offline').map((device) => (
            <Marker key={device.id} position={[device.lat, device.lng]} icon={markerIcon(device, selected?.id === device.id)} eventHandlers={{ click: () => onSelect(device) }}>
              <Tooltip direction="top" offset={[0, -35]} opacity={.96}>
                <b>{device.name}</b><br />藻毒素 {device.toxinUgL.toFixed(2)} μg/L
              </Tooltip>
            </Marker>
          )) : null}
          <MapTools />
        </MapContainer>
        <div className="absolute left-1/2 top-4 z-[600] flex -translate-x-1/2 gap-3">
          <button className={`flex h-11 items-center gap-2 rounded-[14px] border px-5 text-[15px] font-semibold shadow ${deviceLayer ? 'border-[#a7d2ef] bg-white text-[#14213d]' : 'border-transparent bg-white/75 text-[#718096]'}`} type="button" onClick={() => setDeviceLayer((value) => !value)}><RadioTower size={20} />设备图层</button>
          <button className={`flex h-11 items-center gap-2 rounded-[14px] border px-5 text-[15px] font-semibold shadow ${heatLayer ? 'border-[#90cff5] bg-[#eff9ff] text-[#0878e8]' : 'border-transparent bg-white/75 text-[#718096]'}`} type="button" onClick={() => setHeatLayer((value) => !value)}><Droplets size={20} />热力图层</button>
        </div>
        <RiskLegend />
      </div>
    </section>
  );
}

function MetricCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return <div className="aqua-panel flex min-h-[78px] flex-col justify-center gap-2 px-4 shadow-none"><span className="flex items-center gap-2 text-[13px] font-semibold" style={{ color }}>{icon}{label}</span><b className="text-[21px] text-[#111827]">{value}</b></div>;
}

function SelectedDevicePanel({ device }: { device?: DeviceReading }) {
  const navigate = useNavigate();
  if (!device) return <aside className="aqua-panel grid w-[360px] shrink-0 place-items-center text-[#718096]">请选择地图中的设备</aside>;
  const onlineColor = device.status === 'online' ? '#059669' : device.status === 'idle' ? '#f59e0b' : '#64748b';
  return (
    <aside className="aqua-panel relative w-[360px] shrink-0 overflow-hidden px-5 py-5">
      <div className="relative z-10 flex h-full flex-col">
        <p className="text-[14px] font-semibold text-[#516176]">选中设备</p>
        <div className="mt-2 flex flex-wrap items-center gap-2"><h1 className="mr-1 text-[22px] font-black">{device.name}</h1><span className="h-2.5 w-2.5 rounded-full" style={{ background: getRiskColor(device.toxinUgL) }} /><b className="text-[14px]" style={{ color: getRiskColor(device.toxinUgL) }}>{getRiskLabel(device.toxinUgL)}</b></div>
        <div className="mt-3 flex items-center justify-between border-y border-[#d9e9f4] py-3 text-[14px]"><b>设备状态</b><span className="flex items-center gap-2 font-semibold" style={{ color: onlineColor }}><span className="h-2.5 w-2.5 rounded-full" style={{ background: onlineColor }} />{getStatusText(device.status)}</span></div>
        <div className="py-4"><span className="text-[13px] font-semibold text-[#516176]">藻毒素浓度</span><div className="mt-2 flex items-end gap-2"><b className="text-[42px] leading-none" style={{ color: getRiskColor(device.toxinUgL) }}>{device.status === 'offline' ? '--' : device.toxinUgL.toFixed(2)}</b><span className="pb-1 text-[15px]">μg/L</span></div><div className="mt-3 flex justify-between text-[13px]"><span>更新时间</span><span>{device.updatedAt}</span></div></div>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard icon={<Battery size={18} />} label="电量" value={`${device.batteryPercent} %`} color="#078b4f" />
          <MetricCard icon={<Signal size={18} />} label="信号强度" value={`${device.signalDbm} dBm`} color="#078b4f" />
          <MetricCard icon={<Thermometer size={18} />} label="水温" value={`${device.waterTempC.toFixed(1)} °C`} color="#0878e8" />
          <MetricCard icon={<Droplets size={18} />} label="pH" value={device.ph.toFixed(1)} color="#0878e8" />
        </div>
        <div className="aqua-panel mt-4 space-y-3 px-4 py-4 text-[13px] shadow-none">
          <div className="flex justify-between gap-3"><b className="flex items-center gap-2"><MapPin size={17} />位置</b><span className="text-right">{device.locationLabel}</span></div>
          <div className="flex justify-between gap-3"><b className="flex items-center gap-2"><Layers3 size={17} />设备类型</b><span>水体检测节点</span></div>
          <div className="flex justify-between gap-3"><b className="flex items-center gap-2"><RadioTower size={17} />连接方式</b><span>{device.connectionType === 'wifi' ? 'Wi-Fi' : device.connectionType === 'bluetooth' ? '蓝牙' : '未连接'}</span></div>
        </div>
        <button className="primary-button relative z-10 mt-4 flex h-12 w-full items-center justify-center gap-2" type="button" onClick={() => navigate(`/data?device=${device.id}`)}><BarChart3 size={20} />查看历史数据</button>
        <img className="pointer-events-none absolute -bottom-8 -right-8 -z-0 w-[150px] opacity-[.08]" src={materials.mascotHero} alt="" />
      </div>
    </aside>
  );
}

export default function MapMonitorPage() {
  const [searchParams] = useSearchParams();
  const [devices, setDevices] = useState<DeviceReading[]>(demoReadings);
  const [selectedId, setSelectedId] = useState(searchParams.get('device') || demoReadings[0].id);

  const load = useCallback(async () => setDevices(await monitoringService.getLatestReadings()), []);
  useEffect(() => { load(); window.addEventListener('igem:refresh', load); return () => window.removeEventListener('igem:refresh', load); }, [load]);

  const query = (searchParams.get('q') || '').toLowerCase();
  const risk = searchParams.get('risk');
  const visibleDevices = useMemo(() => devices.filter((device) => {
    const queryMatch = !query || device.name.toLowerCase().includes(query) || device.locationLabel.toLowerCase().includes(query) || device.id.toLowerCase().includes(query);
    const riskMatch = !risk || (risk === 'offline' ? device.status === 'offline' : getRiskLevel(device.toxinUgL) === risk);
    return queryMatch && riskMatch;
  }), [devices, query, risk]);
  const selected = devices.find((device) => device.id === selectedId) || visibleDevices[0];

  useEffect(() => {
    const requested = searchParams.get('device');
    if (requested && devices.some((device) => device.id === requested)) setSelectedId(requested);
    else if (query && visibleDevices[0]) setSelectedId(visibleDevices[0].id);
  }, [devices, query, searchParams, visibleDevices]);

  return (
    <div className="flex h-[calc(100vh-142px)] min-h-[680px] gap-4">
      <LakeMap devices={visibleDevices} selected={selected} onSelect={(device) => setSelectedId(device.id)} />
      <SelectedDevicePanel device={selected} />
    </div>
  );
}
