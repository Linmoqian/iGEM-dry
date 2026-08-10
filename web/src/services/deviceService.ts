import type { DeviceInput, DeviceReading, DiscoveredDevice } from '../types/domain';
import { request } from './apiClient';
import { mockDelay, serviceConfig } from './config';
import { getMockDevices, mockDiscoveredDevices, setMockDevices } from './mockStore';

function createDevice(input: DeviceInput): DeviceReading {
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
  return {
    id: `aq-${Date.now().toString(36)}`,
    name: input.name,
    status: 'idle',
    connectionType: input.connectionType,
    locationLabel: input.locationLabel,
    lat: input.lat ?? 30.5667 + (Math.random() - 0.5) * 0.02,
    lng: input.lng ?? 114.3833 + (Math.random() - 0.5) * 0.02,
    batteryPercent: 100,
    signalDbm: -55,
    toxinUgL: 0,
    waterTempC: 24.5,
    ph: 7.2,
    updatedAt: timestamp,
  };
}

export const deviceService = {
  async list(): Promise<DeviceReading[]> {
    if (!serviceConfig.useMocks) return request<DeviceReading[]>('/devices');
    await mockDelay();
    return getMockDevices();
  },

  async create(input: DeviceInput): Promise<DeviceReading> {
    if (!serviceConfig.useMocks) {
      return request<DeviceReading>('/devices', { method: 'POST', body: JSON.stringify(input) });
    }
    await mockDelay(260);
    const device = createDevice(input);
    setMockDevices([...getMockDevices(), device]);
    return device;
  },

  async update(id: string, patch: Partial<DeviceReading>): Promise<DeviceReading> {
    if (!serviceConfig.useMocks) {
      return request<DeviceReading>(`/devices/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(patch) });
    }
    await mockDelay(180);
    let updated: DeviceReading | undefined;
    const next = getMockDevices().map((device) => {
      if (device.id !== id) return device;
      updated = { ...device, ...patch, id: device.id };
      return updated;
    });
    if (!updated) throw new Error('设备不存在');
    setMockDevices(next);
    return updated;
  },

  async remove(id: string): Promise<void> {
    if (!serviceConfig.useMocks) {
      await request<void>(`/devices/${encodeURIComponent(id)}`, { method: 'DELETE' });
      return;
    }
    await mockDelay(180);
    setMockDevices(getMockDevices().filter((device) => device.id !== id));
  },

  async reorder(ids: string[]): Promise<DeviceReading[]> {
    if (!serviceConfig.useMocks) {
      return request<DeviceReading[]>('/devices/order', { method: 'PUT', body: JSON.stringify({ ids }) });
    }
    const byId = new Map(getMockDevices().map((device) => [device.id, device]));
    const ordered = ids.map((id) => byId.get(id)).filter((device): device is DeviceReading => Boolean(device));
    const omitted = getMockDevices().filter((device) => !ids.includes(device.id));
    return setMockDevices([...ordered, ...omitted]);
  },

  async scan(): Promise<DiscoveredDevice[]> {
    if (!serviceConfig.useMocks) return request<DiscoveredDevice[]>('/devices/scan', { method: 'POST' });
    await mockDelay(900);
    return mockDiscoveredDevices.map((device) => ({ ...device }));
  },

  async pair(discovered: DiscoveredDevice): Promise<DeviceReading> {
    if (!serviceConfig.useMocks) {
      return request<DeviceReading>('/devices/pair', { method: 'POST', body: JSON.stringify(discovered) });
    }
    await mockDelay(850);
    const existing = getMockDevices().find((device) => device.name === discovered.name);
    if (existing) return existing;
    const device = createDevice({
      name: discovered.name,
      connectionType: discovered.connectionType,
      locationLabel: '待部署监测点',
    });
    device.status = 'online';
    device.signalDbm = discovered.signalDbm;
    setMockDevices([...getMockDevices(), device]);
    return device;
  },
};
