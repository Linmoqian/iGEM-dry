import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import DeviceCard from './DeviceCard';
import type { DeviceItem } from '@/types/domain';

interface DeviceCardGridProps {
  devices: DeviceItem[];
  onDragEnd: (devices: DeviceItem[]) => void;
  onConnect: (id: string, type: 'bluetooth' | 'wifi') => void;
  onDisconnect: (id: string) => void;
  onDetails: (device: DeviceItem) => void;
  onEdit: (device: DeviceItem) => void;
  onDelete: (device: DeviceItem) => void;
}

export default function DeviceCardGrid({
  devices,
  onDragEnd,
  onConnect,
  onDisconnect,
  onDetails,
  onEdit,
  onDelete,
}: DeviceCardGridProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = devices.findIndex((d) => d.id === active.id);
      const newIndex = devices.findIndex((d) => d.id === over.id);
      onDragEnd(arrayMove(devices, oldIndex, newIndex));
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={devices.map((d) => d.id)} strategy={rectSortingStrategy}>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {devices.map((device) => (
            <DeviceCard
              key={device.id}
              device={device}
              onConnect={(type) => onConnect(device.id, type)}
              onDisconnect={() => onDisconnect(device.id)}
              onDetails={() => onDetails(device)}
              onEdit={() => onEdit(device)}
              onDelete={() => onDelete(device)}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
