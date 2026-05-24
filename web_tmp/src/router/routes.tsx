import { createBrowserRouter } from 'react-router-dom';
import AppShell from '@/layouts/AppShell';
import OverviewPage from '@/pages/OverviewPage';
import MapMonitorPage from '@/pages/MapMonitorPage';
import DataAnalysisPage from '@/pages/DataAnalysisPage';
import DevicePairingPage from '@/pages/DevicePairingPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: 'map', element: <MapMonitorPage /> },
      { path: 'data', element: <DataAnalysisPage /> },
      { path: 'device', element: <DevicePairingPage /> },
      {
        path: '*',
        element: (
          <div className="flex items-center justify-center h-full text-[#5A7184]">
            <div className="text-center">
              <p className="text-4xl font-black text-[#0B2540] mb-2">404</p>
              <p className="text-sm">页面未找到</p>
            </div>
          </div>
        ),
      },
    ],
  },
]);
