import { useMemo, useState } from 'react';
import { demoReadings, demoSummary } from '@/data/demoReadings';
import LakeRiskMap from '@/components/map/LakeRiskMap';
import SelectedDevicePanel from '@/components/map/SelectedDevicePanel';
import { useNavigate } from 'react-router-dom';

export default function MapMonitorPage() {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
  const [showHeat, setShowHeat] = useState(true);
  const [showDevices, setShowDevices] = useState(true);
  const navigate = useNavigate();

  const selectedReading = useMemo(
    () => demoReadings.find((r) => r.id === selectedDeviceId) ?? demoSummary.maxToxinReading,
    [selectedDeviceId]
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-4 items-start">
        <LakeRiskMap
          readings={demoReadings}
          selectedDeviceId={selectedDeviceId}
          onSelectDevice={setSelectedDeviceId}
          showHeat={showHeat}
          showDevices={showDevices}
          onToggleHeat={() => setShowHeat((v) => !v)}
          onToggleDevices={() => setShowDevices((v) => !v)}
        />
        <SelectedDevicePanel
          reading={selectedReading}
          onViewHistory={() => navigate('/data')}
        />
      </div>
    </div>
  );
}
