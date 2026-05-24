import { ReactNode } from 'react';

interface AquaCardProps {
  children: ReactNode;
  className?: string;
  padding?: number;
  bordered?: boolean;
  onClick?: () => void;
}

export default function AquaCard({ children, className = '', padding = 24, bordered = false, onClick }: AquaCardProps) {
  return (
    <div
      className={`bg-white rounded-2xl ${bordered ? 'border border-[#E2E8F0]' : ''} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''} ${className}`}
      style={{ padding }}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
