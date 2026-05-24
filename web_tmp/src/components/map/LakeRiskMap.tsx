import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import 'leaflet.heat';
import { CircleMarker, MapContainer, Popup, useMap, TileLayer } from 'react-leaflet';
import { demoLake } from '@/data/demoReadings';
import { getRiskColor, getRiskLabel, getSignalLabel, normalizeHeatValue } from '@/utils/risk';
import MapLayerToggle from './MapLayerToggle';
import RiskLegend from './RiskLegend';
import type { DeviceReading } from '@/types/domain';

interface LakeRiskMapProps {
  readings: DeviceReading[];
  selectedDeviceId: string | null;
  onSelectDevice: (deviceId: string) => void;
  showHeat: boolean;
  showDevices: boolean;
  onToggleHeat: () => void;
  onToggleDevices: () => void;
}

const GRID_COLUMNS = 74;
const GRID_ROWS = 52;

function interpolateToxinValue(lat: number, lng: number, readings: DeviceReading[]): number {
  let weightedSum = 0;
  let weightTotal = 0;
  for (const reading of readings) {
    const latDelta = lat - reading.lat;
    const lngDelta = lng - reading.lng;
    const distanceSquared = latDelta * latDelta + lngDelta * lngDelta;
    if (distanceSquared < 0.00000008) return reading.toxinUgL;
    const weight = 1 / Math.pow(distanceSquared, 1.15);
    weightedSum += reading.toxinUgL * weight;
    weightTotal += weight;
  }
  return weightedSum / weightTotal;
}

function buildInterpolatedHeatSurface(map: L.Map, readings: DeviceReading[]): L.HeatLatLngTuple[] {
  const bounds = map.getBounds().pad(0.18);
  const north = bounds.getNorth();
  const south = bounds.getSouth();
  const east = bounds.getEast();
  const west = bounds.getWest();
  const latStep = (north - south) / GRID_ROWS;
  const lngStep = (east - west) / GRID_COLUMNS;
  const points: L.HeatLatLngTuple[] = [];

  for (let row = 0; row <= GRID_ROWS; row++) {
    const lat = south + latStep * row;
    for (let col = 0; col <= GRID_COLUMNS; col++) {
      const lng = west + lngStep * col;
      const toxinUgL = interpolateToxinValue(lat, lng, readings);
      points.push([lat, lng, normalizeHeatValue(toxinUgL)]);
    }
  }

  for (const reading of readings) {
    points.push([reading.lat, reading.lng, normalizeHeatValue(reading.toxinUgL)]);
    points.push([reading.lat, reading.lng, normalizeHeatValue(reading.toxinUgL)]);
  }

  return points;
}

function HeatLayer({ readings, show }: { readings: DeviceReading[]; show: boolean }) {
  const map = useMap();
  const layerRef = useRef<L.HeatLayer | null>(null);

  useEffect(() => {
    if (!show) {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
      return;
    }

    const pane = map.getPane('toxin-heat-pane') ?? map.createPane('toxin-heat-pane');
    pane.style.pointerEvents = 'none';
    pane.style.zIndex = '430';

    const updateHeat = () => {
      const points = buildInterpolatedHeatSurface(map, readings);
      if (layerRef.current) {
        layerRef.current.setLatLngs(points).redraw();
        return;
      }
      layerRef.current = L.heatLayer(points, {
        pane: 'toxin-heat-pane',
        radius: 40,
        blur: 38,
        max: 1,
        minOpacity: 0.34,
        gradient: { 0.05: '#16B8D8', 0.25: '#0D7DF2', 0.45: '#08A65A', 0.66: '#F7B500', 0.84: '#FF7A00', 1: '#F5222D' },
      }).addTo(map);
    };

    updateHeat();
    map.on('moveend zoomend resize', updateHeat);
    return () => {
      map.off('moveend zoomend resize', updateHeat);
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map, readings, show]);

  return null;
}

function MapSizeFix() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => map.invalidateSize({ pan: false }), 80);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

function LocateButton() {
  const map = useMap();
  return (
    <button
      onClick={() => map.flyTo(demoLake.center as [number, number], 13)}
      className="absolute top-5 right-5 z-[500] w-8 h-8 rounded-lg bg-white/90 backdrop-blur border border-[rgba(13,125,242,0.10)] flex items-center justify-center shadow-sm hover:bg-[rgba(13,125,242,0.05)]"
      title="居中定位"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0D7DF2" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M12 2v4m0 12v4M2 12h4m12 0h4" /></svg>
    </button>
  );
}

export default function LakeRiskMap({
  readings,
  selectedDeviceId,
  onSelectDevice,
  showHeat,
  showDevices,
  onToggleHeat,
  onToggleDevices,
}: LakeRiskMapProps) {
  const bounds = useMemo(() => L.latLngBounds(demoLake.bounds), []);

  return (
    <div className="aqua-panel p-2.5 relative h-[720px]">
      <div className="absolute top-5 left-1/2 -translate-x-1/2 z-[500]">
        <MapLayerToggle
          showDevices={showDevices}
          showHeat={showHeat}
          onToggleDevices={onToggleDevices}
          onToggleHeat={onToggleHeat}
        />
      </div>
      <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-[500]">
        <RiskLegend />
      </div>

      <div className="w-full h-full rounded-xl overflow-hidden border border-[rgba(13,125,242,0.08)]">
        <MapContainer
          center={demoLake.center as [number, number]}
          zoom={13}
          minZoom={11}
          maxZoom={17}
          maxBounds={bounds}
          maxBoundsViscosity={0.45}
          scrollWheelZoom
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <HeatLayer readings={readings} show={showHeat} />
          <MapSizeFix />
          <LocateButton />

          {showDevices && readings.map((reading) => {
            const color = getRiskColor(reading.toxinUgL);
            const isSelected = selectedDeviceId === reading.id;

            return (
              <CircleMarker
                key={reading.id}
                center={[reading.lat, reading.lng]}
                radius={isSelected ? 14 : reading.status === 'offline' ? 7 : 10}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: reading.status === 'offline' ? 0.3 : 0.82,
                  opacity: reading.status === 'offline' ? 0.5 : 0.95,
                  weight: isSelected ? 3 : 2,
                }}
                bubblingMouseEvents={false}
                eventHandlers={{ click: () => onSelectDevice(reading.id) }}
              >
                <Popup autoPan={false} keepInView={false}>
                  <div className="min-w-[190px] text-[#0B2540]">
                    <p className="font-bold text-sm mb-1">{reading.name}</p>
                    <p className="text-xs text-[#5A7184] mb-2">{reading.locationLabel}</p>
                    <div className="space-y-0.5 text-xs">
                      <p>藻毒素：<strong>{reading.toxinUgL.toFixed(2)} µg/L</strong> · {getRiskLabel(reading.toxinUgL)}</p>
                      <p>电量：{reading.batteryPercent}%</p>
                      <p>信号：{reading.signalDbm} dBm · {getSignalLabel(reading.signalDbm)}</p>
                      <p>水温：{reading.waterTempC.toFixed(1)} °C · pH {reading.ph.toFixed(1)}</p>
                      <p>更新：{reading.updatedAt}</p>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
