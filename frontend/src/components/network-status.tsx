import { Check, AlertCircle, Zap } from 'lucide-react';

interface ChainStatus {
  name: string;
  status: 'healthy' | 'slow' | 'offline';
  avgBlockTime: string;
  txsPerSecond: number;
  gasPrice?: string;
}

const chains: ChainStatus[] = [
  {
    name: 'Ethereum',
    status: 'healthy',
    avgBlockTime: '12.5s',
    txsPerSecond: 15,
    gasPrice: '45 Gwei',
  },
  {
    name: 'Polygon',
    status: 'healthy',
    avgBlockTime: '2.1s',
    txsPerSecond: 65,
    gasPrice: '1.2 Gwei',
  },
  {
    name: 'Arbitrum',
    status: 'healthy',
    avgBlockTime: '0.25s',
    txsPerSecond: 200,
  },
  {
    name: 'Optimism',
    status: 'slow',
    avgBlockTime: '2.0s',
    txsPerSecond: 120,
  },
];

function getStatusIcon(status: ChainStatus['status']) {
  switch (status) {
    case 'healthy':
      return <Check className="w-4 h-4 text-success" />;
    case 'slow':
      return <AlertCircle className="w-4 h-4 text-warning" />;
    case 'offline':
      return <AlertCircle className="w-4 h-4 text-error" />;
  }
}

function getStatusColor(status: ChainStatus['status']) {
  switch (status) {
    case 'healthy':
      return 'bg-success/10 text-success';
    case 'slow':
      return 'bg-warning/10 text-warning';
    case 'offline':
      return 'bg-error/10 text-error';
  }
}

export default function NetworkStatus() {
  return (
    <div className="glass p-6 rounded-lg">
      <h2 className="text-lg font-semibold text-foreground mb-6">Network Status</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {chains.map((chain) => (
          <div
            key={chain.name}
            className={`p-4 border border-border rounded-lg transition-all hover:border-accent/30 ${getStatusColor(
              chain.status
            )}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(chain.status)}
                <h3 className="font-medium text-foreground">{chain.name}</h3>
              </div>
              <span className="text-xs px-2 py-1 rounded-full bg-foreground/10 text-foreground/70 font-medium">
                {chain.status.charAt(0).toUpperCase() + chain.status.slice(1)}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-foreground/60">Avg Block Time:</span>
                <span className="text-foreground font-mono">{chain.avgBlockTime}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-foreground/60 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> TPS:
                </span>
                <span className="text-foreground font-mono">{chain.txsPerSecond}</span>
              </div>
              {chain.gasPrice && (
                <div className="flex items-center justify-between pt-2 border-t border-foreground/10">
                  <span className="text-foreground/60">Gas Price:</span>
                  <span className="text-foreground font-mono">{chain.gasPrice}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Overall Stats */}
      <div className="mt-6 pt-6 border-t border-border flex justify-around text-center">
        <div>
          <p className="text-xs text-foreground/60 mb-1">Networks Active</p>
          <p className="text-2xl font-bold text-accent">4</p>
        </div>
        <div>
          <p className="text-xs text-foreground/60 mb-1">Avg TPS</p>
          <p className="text-2xl font-bold text-accent">400</p>
        </div>
        <div>
          <p className="text-xs text-foreground/60 mb-1">Monitored</p>
          <p className="text-2xl font-bold text-accent">24/7</p>
        </div>
      </div>
    </div>
  );
}
