import { Menu, Bell, Settings, Wallet, LogOut } from 'lucide-react';

export default function Header() {
  return (
    <header className="sticky top-0 z-40" style={{ borderBottom: '1px solid rgba(0, 217, 255, 0.1)', backgroundColor: 'rgba(20, 20, 32, 0.5)', backdropFilter: 'blur(12px)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                ForensicsAI
              </h1>
              <p className="text-xs" style={{ color: 'rgba(240, 240, 248, 0.6)' }}>Blockchain Analysis</p>
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            {/* Wallet Button */}
            <button className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg text-primary transition-colors" style={{ backgroundColor: 'rgba(37, 99, 235, 0.1)', borderColor: 'rgb(37, 99, 235)' }}>
              <Wallet className="w-4 h-4" />
              <span className="text-sm font-medium">Connect</span>
            </button>

            {/* Notifications */}
            <button className="p-2 rounded-lg transition-colors relative" style={{ backgroundColor: 'rgba(20, 20, 32, 0.8)' }}>
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full"></span>
            </button>

            {/* Settings */}
            <button className="p-2 rounded-lg transition-colors" style={{ backgroundColor: 'rgba(20, 20, 32, 0.8)' }}>
              <Settings className="w-5 h-5" />
            </button>

            {/* Profile Dropdown */}
            <button className="p-2 rounded-lg transition-colors" style={{ backgroundColor: 'rgba(20, 20, 32, 0.8)' }}>
              <LogOut className="w-5 h-5" />
            </button>

            {/* Mobile Menu */}
            <button className="sm:hidden p-2 rounded-lg transition-colors" style={{ backgroundColor: 'rgba(20, 20, 32, 0.8)' }}>
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
