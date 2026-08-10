import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './layouts/AppShell';

const OverviewPage = lazy(() => import('./pages/OverviewPage'));
const MapMonitorPage = lazy(() => import('./pages/MapMonitorPage'));
const DataAnalysisPage = lazy(() => import('./pages/DataAnalysisPage'));
const DevicePairingPage = lazy(() => import('./pages/DevicePairingPage'));

function PageLoader() {
  return <div className="empty-state h-full"><div><span className="mx-auto mb-3 block h-8 w-8 animate-spin rounded-full border-2 border-[#b9dcf5] border-t-[#0878e8]" /><p>正在加载监测模块…</p></div></div>;
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/map" element={<MapMonitorPage />} />
          <Route path="/data" element={<DataAnalysisPage />} />
          <Route path="/device" element={<DevicePairingPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
