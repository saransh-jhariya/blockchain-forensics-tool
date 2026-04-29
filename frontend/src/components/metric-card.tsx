import { ArrowUp, ArrowDown } from 'lucide-react';

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change?: number;
  unit?: string;
  highlight?: boolean;
}

export default function MetricCard({
  icon,
  label,
  value,
  change,
  unit,
  highlight,
}: MetricCardProps) {
  const isPositive = change && change > 0;

  return (
    <div
      className="p-6 rounded-lg transition-all"
      style={{
        backgroundColor: 'rgba(20, 20, 32, 0.3)',
        backdropFilter: 'blur(12px)',
        border: highlight ? '1px solid rgb(0, 217, 255)' : '1px solid rgba(0, 217, 255, 0.1)',
        boxShadow: highlight ? '0 10px 25px -5px rgba(0, 217, 255, 0.2)' : 'none',
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          style={{
            padding: '12px',
            borderRadius: '8px',
            backgroundColor: highlight ? 'rgba(0, 217, 255, 0.2)' : 'rgba(37, 99, 235, 0.1)',
            color: highlight ? 'rgb(0, 217, 255)' : 'rgb(37, 99, 235)',
          }}
        >
          {icon}
        </div>
        {change !== undefined && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px',
              fontWeight: '500',
              color: isPositive ? 'rgb(16, 185, 129)' : 'rgb(239, 68, 68)',
            }}
          >
            {isPositive ? (
              <ArrowUp className="w-3 h-3" />
            ) : (
              <ArrowDown className="w-3 h-3" />
            )}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <p style={{ fontSize: '14px', color: 'rgba(240, 240, 248, 0.7)', marginBottom: '8px' }}>
        {label}
      </p>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <span style={{ fontSize: '24px', fontWeight: 'bold', color: 'rgb(240, 240, 248)' }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: '14px', color: 'rgba(240, 240, 248, 0.6)' }}>{unit}</span>
        )}
      </div>
    </div>
  );
}
