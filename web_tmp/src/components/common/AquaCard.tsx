import type { ReactNode } from 'react';

interface AquaCardProps { children: ReactNode; className?: string; onClick?: () => void; }

export default function AquaCard({ children, className = '', onClick }: AquaCardProps) {
  return (
    <div className={`aqua-card ${onClick ? 'cursor-pointer' : ''} ${className}`} onClick={onClick}>
      {children}
    </div>
  );
}
