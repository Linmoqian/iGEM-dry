'use client';

import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import 'leaflet.heat';
import { CircleMarker, MapContainer, Popup, useMap, TileLayer } from 'react-leaflet';
import {
  DeviceReading,
  demoLake,
  getRiskColor,
  getRiskLabel,
  getSignalLabel,
  normalizeHeatValue,
} from '../lib/demoReadings';

interface MonitoringMapProps {
  readings: DeviceReading[];
  selectedDeviceId?: string | null;
  onSelectDevice?: (deviceId: string) => void;
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

    if (distanceSquared < 0.00000008) {
      return reading.toxinUgL;
    }

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

  for (let row = 0; row <= GRID_ROWS; row += 1) {
    const lat = south + latStep * row;

    for (let column = 0; column <= GRID_COLUMNS; column += 1) {
      const lng = west + lngStep * column;
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

function HeatLayer({ readings }: MonitoringMapProps) {
  const map = useMap();
  const layerRef = useRef<L.HeatLayer | null>(null);

  useEffect(() => {
    const heatPaneName = 'toxin-heat-pane';
    const heatPane = map.getPane(heatPaneName) ?? map.createPane(heatPaneName);
    heatPane.style.opacity = '0.78';
    heatPane.style.mixBlendMode = 'screen';
    heatPane.style.pointerEvents = 'none';
    heatPane.style.zIndex = '430';

    const updateHeatSurface = () => {
      const points = buildInterpolatedHeatSurface(map, readings);

      if (layerRef.current) {
        layerRef.current.setLatLngs(points).redraw();
        return;
      }

      layerRef.current = L.heatLayer(points, {
        pane: heatPaneName,
        radius: 54,
        blur: 48,
        max: 1,
        maxZoom: 18,
        minOpacity: 0.34,
        gradient: {
          0.05: '#22c55e',
          0.25: '#84cc16',
          0.45: '#facc15',
          0.66: '#fb923c',
          0.84: '#f97316',
          1: '#ef4444',
        },
      }).addTo(map);
    };

    updateHeatSurface();
    map.on('moveend zoomend resize', updateHeatSurface);

    return () => {
      map.off('moveend zoomend resize', updateHeatSurface);

      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map, readings]);

  return null;
}

function MapSizeController({ selectedDeviceId }: { selectedDeviceId?: string | null }) {
  const map = useMap();

  useEffect(() => {
    const timer = window.setTimeout(() => {
      map.invalidateSize({ pan: false });
    }, 80);

    return () => window.clearTimeout(timer);
  }, [map, selectedDeviceId]);

  return null;
}

export default function MonitoringMap({
  readings,
  selectedDeviceId,
  onSelectDevice,
}: MonitoringMapProps) {
  const bounds = useMemo(() => L.latLngBounds(demoLake.bounds), []);

  return (
    <MapContainer
      center={demoLake.center}
      zoom={13}
      minZoom={11}
      maxZoom={17}
      maxBounds={bounds}
      maxBoundsViscosity={0.45}
      scrollWheelZoom
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="map-tiles"
      />
      <HeatLayer readings={readings} />
      <MapSizeController selectedDeviceId={selectedDeviceId} />

      {readings.map((reading) => {
        const color = getRiskColor(reading.toxinUgL);
        const isSelected = selectedDeviceId === reading.id;

        return (
          <CircleMarker
            key={reading.id}
            center={[reading.lat, reading.lng]}
            radius={isSelected ? 15 : reading.status === 'offline' ? 8 : 11}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: reading.status === 'offline' ? 0.35 : 0.82,
              opacity: reading.status === 'offline' ? 0.55 : 0.95,
              weight: isSelected ? 4 : 2,
            }}
            bubblingMouseEvents={false}
            eventHandlers={{
              click: () => onSelectDevice?.(reading.id),
            }}
          >
            <Popup autoPan={false} keepInView={false}>
              <div className="min-w-[190px] text-slate-900">
                <p className="font-bold text-base mb-1">{reading.name}</p>
                <p className="text-xs text-slate-600 mb-3">{reading.locationLabel}</p>
                <div className="space-y-1 text-sm">
                  <p>藻毒素：<strong>{reading.toxinUgL.toFixed(2)} µg/L</strong> · {getRiskLabel(reading.toxinUgL)}</p>
                  <p>电量：{reading.batteryPercent}%</p>
                  <p>信号：{reading.signalDbm} dBm · {getSignalLabel(reading.signalDbm)}</p>
                  <p>水温：{reading.waterTempC.toFixed(1)} °C · pH {reading.ph.toFixed(1)}</p>
                  <p>更新：{reading.updatedAt}</p>
                  <p className="pt-2 text-xs text-slate-500">右侧面板显示历史曲线</p>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
