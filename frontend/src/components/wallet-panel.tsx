import { Wallet, Chain, Shield, TrendingUp } from 'lucide-react';

interface WalletInfo {
  address: string;
  balance: string;
  tokens: number;
  riskScore: number;
  status: 'safe' | 'warning' | 'danger';
}

const wallets: WalletInfo[] = [
  {
    address: '0x742d35Cc6634C0532925a3b844Bc9e7595f5678',
    balance: '45.23 ETH',
    tokens: 12,
    riskScore: 15,
    status: 'safe',
  },
  {
    address: '0x1234567890abcdef1234567890abcdef12345678',
    balance: '128.5 ETH',
    tokens: 28,
    riskScore: 42,
    status: 'warning',
  },
];

export default function WalletConnectionPanel() {
  return (
    <div className="glass p-6 rounded-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">Wallets & Clusters</h2>
        <button className="px-3 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
          Connect Wallet
        </button>
      </div>

      {wallets.length === 0 ? (
        <div className="py-12 text-center">
          <Wallet className="w-12 h-12 mx-auto text-foreground/30 mb-4" />
          <p className="text-foreground/60">No wallets connected</p>
          <p className="text-sm text-foreground/40 mt-2">
            Connect your Web3 wallet to begin analysis
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {wallets.map((wallet) => (
            <div
              key={wallet.address}
              className="p-4 border border-border rounded-lg hover:border-accent/30 transition-colors group cursor-pointer"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Left Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <Wallet className="w-4 h-4 text-primary flex-shrink-0" />
                    <code className="text-xs font-mono text-accent truncate">{wallet.address}</code>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div>
                      <p className="text-foreground/60 text-xs">Balance</p>
                      <p className="text-foreground font-medium">{wallet.balance}</p>
                    </div>
                    <div>
                      <p className="text-foreground/60 text-xs">Tokens</p>
                      <p className="text-foreground font-medium">{wallet.tokens}</p>
                    </div>
                  </div>
                </div>

                {/* Risk Score */}
                <div className="flex-shrink-0 flex flex-col items-end gap-2">
                  <div
                    className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                      wallet.status === 'safe'
                        ? 'bg-success/20 text-success'
                        : wallet.status === 'warning'
                          ? 'bg-warning/20 text-warning'
                          : 'bg-error/20 text-error'
                    }`}
                  >
                    <Shield className="w-3 h-3" />
                    {wallet.riskScore}% Risk
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
