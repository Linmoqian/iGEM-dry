export const serviceConfig = {
  useMocks: import.meta.env.VITE_USE_MOCKS !== 'false',
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, ''),
  websocketUrl: import.meta.env.VITE_WS_URL || '',
};

export const mockDelay = (milliseconds = 180) =>
  new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds));
