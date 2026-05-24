const PLACEHOLDER = '';

const assetMap = {
  common: {
    logoOcean: PLACEHOLDER,
    headerMascot: PLACEHOLDER,
    sidebarMascot: PLACEHOLDER,
    navOverviewIcon: PLACEHOLDER,
    navMapIcon: PLACEHOLDER,
    navDataIcon: PLACEHOLDER,
    navDeviceIcon: PLACEHOLDER,
    notificationIcon: PLACEHOLDER,
  },
  overview: {
    systemShieldIcon: PLACEHOLDER,
    onlineIcon: PLACEHOLDER,
    idleIcon: PLACEHOLDER,
    offlineIcon: PLACEHOLDER,
    avgToxinIcon: PLACEHOLDER,
    riskIcon: PLACEHOLDER,
    alertArrowIcon: PLACEHOLDER,
  },
  map: {
    markerNormal: PLACEHOLDER,
    markerAttention: PLACEHOLDER,
    markerWarning: PLACEHOLDER,
    markerDanger: PLACEHOLDER,
    deviceIllustration: PLACEHOLDER,
    layerIcon: PLACEHOLDER,
    locationIcon: PLACEHOLDER,
  },
  data: {
    microscope: PLACEHOLDER,
    trendWarningIcon: PLACEHOLDER,
    exportIcon: PLACEHOLDER,
    confidenceIcon: PLACEHOLDER,
    predictionIcon: PLACEHOLDER,
  },
  drive: {
    buoyDevice: PLACEHOLDER,
    probeDevice: PLACEHOLDER,
    bluetoothScan: PLACEHOLDER,
    deviceMascot: PLACEHOLDER,
    labFlask: PLACEHOLDER,
    addIcon: PLACEHOLDER,
    refreshIcon: PLACEHOLDER,
    wifiIcon: PLACEHOLDER,
    batteryIcon: PLACEHOLDER,
    signalIcon: PLACEHOLDER,
  },
} as const;

export function getAssetPath(path: string): string {
  return path;
}

export function isAssetAvailable(path: string): boolean {
  return path !== PLACEHOLDER && path.length > 0;
}

export default assetMap;
