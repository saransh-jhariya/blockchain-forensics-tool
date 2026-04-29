import { Zap, Shield, TrendingUp, Database } from 'lucide-react';
import Header from '@/components/header';
import MetricCard from '@/components/metric-card';
import TransactionChart from '@/components/transaction-chart';
import GasFeesChart from '@/components/gas-fees-chart';
import TransactionExplorer from '@/components/transaction-explorer';
import ActivityFeed from '@/components/activity-feed';
import WalletConnectionPanel from '@/components/wallet-panel';
import SmartContractPanel from '@/components/smart-contract-panel';
import NetworkStatus from '@/components/network-status';
import Footer from '@/components/footer';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Blockchain Forensics Dashboard</h1>
          <p className="text-foreground/60">
            Real-time wallet clustering, transaction analysis, and cross-chain tracing
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            icon={<Database className="w-5 h-5" />}
            label="Active Wallets"
            value="2,847"
            change={12}
            highlight
          />
          <MetricCard
            icon={<Zap className="w-5 h-5" />}
            label="Transactions/Hour"
            value="15,240"
            change={8}
          />
          <MetricCard
            icon={<Shield className="w-5 h-5" />}
            label="Risk Alerts"
            value="23"
            change={-5}
          />
          <MetricCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Total Value Traced"
            value="$2.4M"
            change={15}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <TransactionChart />
          </div>
          <GasFeesChart />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <TransactionExplorer />
          </div>
          <ActivityFeed />
        </div>

        {/* Secondary Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <WalletConnectionPanel />
          <NetworkStatus />
        </div>

        {/* Smart Contract Panel */}
        <SmartContractPanel />
      </main>

      <Footer />
    </div>
  );
}
