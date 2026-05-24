import { useMemo } from 'react';
import { demoReadings, demoDeviceHistory } from '@/data/demoReadings';
import { generateTrendData } from '@/utils/chart';
import DataFilterBar from '@/components/data/DataFilterBar';
import MultiMetricTrendChart from '@/components/data/MultiMetricTrendChart';
import SensorComparisonPanel from '@/components/data/SensorComparisonPanel';
import ToxinPredictionPanel from '@/components/data/ToxinPredictionPanel';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';

export default function DataAnalysisPage() {
  const trendData = useMemo(() => generateTrendData(demoReadings, demoDeviceHistory), []);
  return (
    <div className="flex flex-col gap-5">
      <DataFilterBar />
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-5">
        <MultiMetricTrendChart trendData={trendData} />
        <SensorComparisonPanel readings={demoReadings} />
      </div>
      <ToxinPredictionPanel />
      <div className="relative h-0">
        <div className="absolute -left-3 -bottom-2 z-0 pointer-events-none opacity-30">
          <ImagePlaceholder width={180} height={160} label="显微镜占位" variant="illustration" />
        </div>
      </div>
    </div>
  );
}
