import type { RealtimeEvent } from '../types/domain';
import { serviceConfig } from './config';

export function connectRealtime(onEvent: (event: RealtimeEvent) => void): () => void {
  if (serviceConfig.useMocks || !serviceConfig.websocketUrl) return () => undefined;

  const socket = new WebSocket(serviceConfig.websocketUrl);
  socket.addEventListener('message', (message) => {
    try {
      onEvent(JSON.parse(message.data) as RealtimeEvent);
    } catch {
      // Ignore malformed events; the next valid event remains usable.
    }
  });

  return () => socket.close(1000, 'page disposed');
}
