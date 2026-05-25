import { Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './layouts/AppShell';
import OverviewPage from './pages/OverviewPage';
import MapMonitorPage from './pages/MapMonitorPage';
import DataAnalysisPage from './pages/DataAnalysisPage';
import DevicePairingPage from './pages/DevicePairingPage';

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/map" element={<MapMonitorPage />} />
        <Route path="/data" element={<DataAnalysisPage />} />
        <Route path="/device" element={<DevicePairingPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
