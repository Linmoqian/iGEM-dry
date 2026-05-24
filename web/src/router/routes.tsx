import { createBrowserRouter } from 'react-router-dom';
import AppShell from '../layouts/AppShell';
import OverviewPage from '../pages/OverviewPage';
import MapMonitorPage from '../pages/MapMonitorPage';
import DataAnalysisPage from '../pages/DataAnalysisPage';
import DevicePairingPage from '../pages/DevicePairingPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: 'map', element: <MapMonitorPage /> },
      { path: 'data', element: <DataAnalysisPage /> },
      { path: 'device', element: <DevicePairingPage /> },
    ],
  },
]);

export default router;
