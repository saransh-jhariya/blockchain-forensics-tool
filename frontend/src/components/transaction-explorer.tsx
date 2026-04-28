import { Search, Filter, ExternalLink } from 'lucide-react';

const transactions = [
  {
    id: '0x1a2b3c...',
    from: '0x742d...5678',
    to: '0x9abc...def0',
    value: '2.5 ETH',
    status: 'confirmed',
    time: '2 min ago',
  },
  {
    id: '0x4d5e6f...',
    from: '0x1234...5678',
    to: '0x9abc...def0',
    value: '1.2 ETH',
    status: 'confirmed',
    time: '5 min ago',
  },
  {
    id: '0x7g8h9i...',
    from: '0x742d...5678',
    to: '0xabcd...ef12',
    value: '0.8 ETH',
    status: 'pending',
    time: '8 min ago',
  },
  {
    id: '0x9j0k1l...',
    from: '0x2468...ace0',
    to: '0x742d...5678',
    value: '3.5 ETH',
    status: 'confirmed',
    time: '12 min ago',
  },
];

export default function TransactionExplorer() {
  return (
    <div className="glass p-6 rounded-lg">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Transaction Explorer</h2>

        {/* Search and Filter */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-foreground/40" />
            <input
              type="text"
              placeholder="Search by address or hash..."
              className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-lg text-sm text-foreground placeholder:text-foreground/40 focus:outline-none focus:border-accent/50"
            />
          </div>
          <button className="p-2 bg-input border border-border rounded-lg hover:border-accent/50 transition-colors">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-foreground/60 text-sm">
              <th className="text-left py-3 px-3 font-medium">Transaction</th>
              <th className="text-left py-3 px-3 font-medium">From</th>
              <th className="text-left py-3 px-3 font-medium">To</th>
              <th className="text-right py-3 px-3 font-medium">Value</th>
              <th className="text-center py-3 px-3 font-medium">Status</th>
              <th className="text-right py-3 px-3 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr
                key={tx.id}
                className="border-b border-border/50 hover:bg-card/50 transition-colors"
              >
                <td className="py-4 px-3">
                  <div className="flex items-center gap-2">
                    <code className="text-xs text-accent font-mono">{tx.id}</code>
                    <button className="p-1 hover:bg-card rounded">
                      <ExternalLink className="w-3 h-3 text-foreground/40" />
                    </button>
                  </div>
                </td>
                <td className="py-4 px-3 text-sm text-foreground/80">
                  <code className="font-mono text-xs">{tx.from}</code>
                </td>
                <td className="py-4 px-3 text-sm text-foreground/80">
                  <code className="font-mono text-xs">{tx.to}</code>
                </td>
                <td className="py-4 px-3 text-right text-sm font-semibold text-accent">
                  {tx.value}
                </td>
                <td className="py-4 px-3 text-center">
                  <span
                    className={`inline-block px-2 py-1 text-xs font-medium rounded ${
                      tx.status === 'confirmed'
                        ? 'bg-success/20 text-success'
                        : 'bg-warning/20 text-warning'
                    }`}
                  >
                    {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                  </span>
                </td>
                <td className="py-4 px-3 text-right text-sm text-foreground/60">{tx.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
