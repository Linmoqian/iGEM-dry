import type { ReactNode } from 'react';

interface AquaCardProps {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
  selected?: boolean;
}

export default function AquaCard({
  children,
  className = '',
  hoverable = false,
  selected = false,
}: AquaCardProps) {
  return (
    <div
      className={`
        bg-surface rounded-[16px] border border-border-subtle
        shadow-card p-5
        transition-all duration-200
        ${hoverable ? 'hover:-translate-y-0.5 hover:shadow-hover cursor-pointer' : ''}
        ${selected ? 'border-2 border-primary shadow-hover' : ''}
        ${className}
      `.trim()}
    >
      {children}
    </div>
  );
}
