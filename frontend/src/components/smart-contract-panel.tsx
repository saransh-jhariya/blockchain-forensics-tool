import { Code, Send, Eye, Copy } from 'lucide-react';

interface ContractFunction {
  name: string;
  type: 'read' | 'write';
  params: string;
  description: string;
}

const contractFunctions: ContractFunction[] = [
  {
    name: 'balanceOf',
    type: 'read',
    params: 'address',
    description: 'Get token balance of an address',
  },
  {
    name: 'transfer',
    type: 'write',
    params: 'to, amount',
    description: 'Transfer tokens to recipient',
  },
  {
    name: 'totalSupply',
    type: 'read',
    params: 'none',
    description: 'Get total token supply',
  },
  {
    name: 'approve',
    type: 'write',
    params: 'spender, amount',
    description: 'Approve spending of tokens',
  },
];

export default function SmartContractPanel() {
  return (
    <div className="glass p-6 rounded-lg">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-2">Smart Contract Interaction</h2>
        <p className="text-sm text-foreground/60">
          Contract: <code className="text-accent font-mono">0xA0b...9E3F</code>
        </p>
      </div>

      {/* Contract Functions */}
      <div className="space-y-3">
        {contractFunctions.map((func) => (
          <div
            key={func.name}
            className="p-4 border border-border rounded-lg hover:border-accent/30 transition-colors group"
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  {func.type === 'read' ? (
                    <Eye className="w-4 h-4 text-success" />
                  ) : (
                    <Send className="w-4 h-4 text-accent" />
                  )}
                  <code className="font-mono font-semibold text-foreground">{func.name}</code>
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-medium ${
                      func.type === 'read'
                        ? 'bg-success/20 text-success'
                        : 'bg-accent/20 text-accent'
                    }`}
                  >
                    {func.type.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-foreground/60 mb-1">{func.description}</p>
                <p className="text-xs text-foreground/50 font-mono">
                  <span className="text-foreground/40">Parameters:</span> {func.params}
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button className="p-2 hover:bg-card rounded transition-colors">
                  <Copy className="w-4 h-4 text-foreground/40" />
                </button>
              </div>
            </div>

            {/* Input Section */}
            {func.type === 'write' && (
              <div className="flex gap-2 mt-3 pt-3 border-t border-border/50">
                <input
                  type="text"
                  placeholder="Enter parameters..."
                  className="flex-1 px-3 py-2 bg-input border border-border rounded text-xs text-foreground placeholder:text-foreground/40 focus:outline-none focus:border-accent/50"
                />
                <button className="px-3 py-2 bg-accent text-accent-foreground rounded text-xs font-medium hover:bg-accent/90 transition-colors">
                  Execute
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
