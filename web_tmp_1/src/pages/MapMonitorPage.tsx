import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Navigation, Droplets, Thermometer, Beaker, Battery, Signal, Clock, MapPin, ChevronRight } from 'lucide-react';
import { demoReadings, demoLake, getRiskLevel, getRiskLabel, getRiskColor, getSignalLabel, getStatusText, demoDeviceHistory } from '../data/demoReadings';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { DeviceReading, DeviceHistoryPoint } from '../types/domain';

function MapController({ selectedId }: { selectedId: string | null }) {
  const map = useMap();
  useEffect(() => {
    setTimeout(() => map.invalidateSize(), 200);
  }, [selectedId, map]);
  return null;
}

function RiskLegend() {
  const items = [
    { color: '#22C55E', label: '正常 < 0.5 µg/L' },
    { color: '#F59E0B', label: '关注 0.5 - 1.0 µg/L' },
    { color: '#FF7A00', label: '警戒 1.0 - 5.0 µg/L' },
    { color: '#EF4444', label: '高风险 > 5.0 µg/L' },
  ];
  return (
    <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl h-[70px] flex items-center gap-8 px-6 z-[1000] shadow-sm">
      <span className="text-sm font-bold text-[#0F172A]">风险图例</span>
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
          <span className="text-[13px] text-[#475569]">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

function DeviceMetricChart({ deviceId }: { deviceId: string }) {
  const history = demoDeviceHistory[deviceId] ?? [];
  const data = history.map((p: DeviceHistoryPoint) => ({
    time: p.time.slice(11, 16),
    toxin: p.toxinUgL,
    temp: p.waterTempC,
    ph: p.ph,
  }));

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#64748B' }} interval={3} />
          <YAxis yAxisId="left" tick={{ fontSize: 9, fill: '#64748B' }} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 9, fill: '#64748B' }} />
          <Tooltip contentStyle={{ borderRadius: 8, fontSize: 11, border: '1px solid #E2E8F0' }} />
          <Line yAxisId="left" type="monotone" dataKey="toxin" stroke="#1A73E8" strokeWidth={2} dot={false} />
          <Line yAxisId="right" type="monotone" dataKey="temp" stroke="#10B981" strokeWidth={2} dot={false} />
          <Line yAxisId="right" type="monotone" dataKey="ph" stroke="#8B5CF6" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function MapMonitorPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedDevice = selectedId ? demoReadings.find((r) => r.id === selectedId) ?? null : null;

  const onlineDevices = demoReadings.filter((r) => r.status !== 'offline');

  return (
    <div className="flex gap-5 h-full">
      {/* Map Container */}
      <div className="flex-1 relative rounded-2xl overflow-hidden border border-[#E2E8F0]">
        <MapContainer
          center={demoLake.center}
          zoom={13}
          minZoom={11}
          maxZoom={17}
          style={{ width: '100%', height: '100%' }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapController selectedId={selectedId} />
          {onlineDevices.map((device) => {
            const risk = getRiskLevel(device.toxinUgL);
            const color = getRiskColor(device.toxinUgL);
            const isSelected = selectedId === device.id;
            const radius = isSelected ? 10 : risk === 'critical' ? 8 : 6;
            return (
              <CircleMarker
                key={device.id}
                center={[device.lat, device.lng]}
                radius={radius}
                pathOptions={{
                  fillColor: color,
                  color: isSelected ? '#0F172A' : '#FFFFFF',
                  weight: isSelected ? 3 : 1.5,
                  fillOpacity: 0.85,
                }}
                eventHandlers={{ click: () => setSelectedId(device.id) }}
              >
                <Popup>
                  <div className="text-sm">
                    <strong>{device.name}</strong><br />
                    毒素: {device.toxinUgL.toFixed(2)} µg/L<br />
                    风险: {getRiskLabel(device.toxinUgL)}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Zoom Controls */}
        <div className="absolute top-4 left-4 z-[1000] flex flex-col bg-white rounded-lg shadow-sm">
          <button className="w-10 h-10 flex items-center justify-center text-lg font-bold text-[#475569] hover:bg-[#F4F8FC] border-b border-[#E2E8F0]"
            onClick={() => {
              const mapEl = document.querySelector('.leaflet-container') as any;
              if (mapEl?._leaflet_map) mapEl._leaflet_map.zoomIn();
            }}>+</button>
          <button className="w-10 h-10 flex items-center justify-center text-lg font-bold text-[#475569] hover:bg-[#F4F8FC]"
            onClick={() => {
              const mapEl = document.querySelector('.leaflet-container') as any;
              if (mapEl?._leaflet_map) mapEl._leaflet_map.zoomOut();
            }}>-</button>
        </div>

        <RiskLegend />
      </div>

      {/* Inspector Panel */}
      <div className="w-[440px] bg-white rounded-2xl border border-[#E2E8F0] p-6 flex flex-col gap-4 overflow-y-auto">
        {selectedDevice ? (
          <>
            <div className="flex flex-col gap-1">
              <h2 className="text-lg font-bold text-[#0F172A]">{selectedDevice.name}</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-0.5 rounded-full" style={{
                  backgroundColor: getRiskColor(selectedDevice.toxinUgL) + '1A',
                  color: getRiskColor(selectedDevice.toxinUgL),
                }}>
                  {getRiskLabel(selectedDevice.toxinUgL)}
                </span>
                <span className="text-xs text-[#64748B]">{getStatusText(selectedDevice.status)}</span>
              </div>
            </div>

            {/* Core Metric */}
            <div className="flex items-center justify-between bg-[#F8FAFC] rounded-xl p-4">
              <div className="flex flex-col">
                <span className="text-xs text-[#64748B]">藻毒素浓度</span>
                <span className="text-[28px] font-bold" style={{ color: getRiskColor(selectedDevice.toxinUgL) }}>
                  {selectedDevice.toxinUgL.toFixed(2)}
                </span>
                <span className="text-xs text-[#64748B]">µg/L</span>
              </div>
              <Droplets size={40} className="text-[#1A73E8] opacity-20" />
            </div>

            {/* Grid Metrics */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: '水温', value: `${selectedDevice.waterTempC.toFixed(1)} ℃`, icon: Thermometer, color: '#10B981' },
                { label: 'pH', value: selectedDevice.ph.toFixed(1), icon: Beaker, color: '#8B5CF6' },
                { label: '电量', value: `${selectedDevice.batteryPercent}%`, icon: Battery, color: '#22C55E' },
                { label: '信号', value: `${selectedDevice.signalDbm} dBm`, icon: Signal, color: '#06B6D4' },
              ].map((m) => (
                <div key={m.label} className="flex items-center gap-3 bg-[#F8FAFC] rounded-xl p-3">
                  <m.icon size={20} style={{ color: m.color }} />
                  <div className="flex flex-col">
                    <span className="text-[11px] text-[#64748B]">{m.label}</span>
                    <span className="text-sm font-bold text-[#0F172A]">{m.value}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Chart */}
            <DeviceMetricChart deviceId={selectedDevice.id} />

            {/* Metadata */}
            <div className="flex flex-col gap-2 pt-5 border-t border-[#F1F5F9]">
              <div className="flex justify-between text-sm">
                <span className="text-[#64748B]">位置</span>
                <span className="text-[#0F172A]">{selectedDevice.locationLabel}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-[#64748B]">最后更新</span>
                <span className="text-[#0F172A]">{selectedDevice.updatedAt}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-[#64748B]">连接方式</span>
                <span className="text-[#0F172A]">{selectedDevice.connectionType === 'wifi' ? 'WiFi' : selectedDevice.connectionType === 'bluetooth' ? '蓝牙' : '无'}</span>
              </div>
            </div>

            <button className="w-full h-12 bg-[#1A73E8] text-white rounded-xl font-medium hover:bg-[#1557B0] transition-colors mt-auto">
              查看详细数据
            </button>
          </>
        ) : (
          <>
            <h2 className="text-lg font-bold text-[#0F172A]">{demoLake.name}</h2>
            <p className="text-sm text-[#64748B] leading-relaxed">{demoLake.description}</p>

            <div className="flex items-center justify-between bg-[#F8FAFC] rounded-xl p-4">
              <div className="flex flex-col">
                <span className="text-xs text-[#64748B]">在线设备</span>
                <span className="text-[28px] font-bold text-[#22C55E]">
                  {demoReadings.filter(r => r.status === 'online').length}
                </span>
                <span className="text-xs text-[#64748B]">/ {demoReadings.length} 台</span>
              </div>
              <Navigation size={40} className="text-[#1A73E8] opacity-20" />
            </div>

            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-bold text-[#0F172A]">监测节点</h4>
              {demoReadings.filter(r => r.status !== 'offline').slice(0, 8).map((device) => (
                <button
                  key={device.id}
                  onClick={() => setSelectedId(device.id)}
                  className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] hover:bg-[#E6F0FA] transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <MapPin size={16} style={{ color: getRiskColor(device.toxinUgL) }} />
                    <span className="text-sm text-[#0F172A]">{device.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium" style={{ color: getRiskColor(device.toxinUgL) }}>
                      {device.toxinUgL.toFixed(2)}
                    </span>
                    <ChevronRight size={14} className="text-[#64748B]" />
                  </div>
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
