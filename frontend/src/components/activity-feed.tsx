import { AlertCircle, CheckCircle, Zap, Shield } from 'lucide-react';

interface ActivityItem {
  id: string;
  type: 'alert' | 'success' | 'activity' | 'security';
  title: string;
  description: string;
  timestamp: string;
  severity?: 'high' | 'medium' | 'low';
}

const activities: ActivityItem[] = [
  {
    id: '1',
    type: 'alert',
    title: 'Unusual Activity Detected',
    description: 'Large transaction detected from cluster 0x1234',
    timestamp: '2 min ago',
    severity: 'high',
  },
  {
    id: '2',
    type: 'security',
    title: 'Security Alert',
    description: 'Address flagged by OFAC SDN list',
    timestamp: '15 min ago',
    severity: 'high',
  },
  {
    id: '3',
    type: 'activity',
    title: 'Bridge Event Detected',
    description: 'Wormhole bridge transfer detected',
    timestamp: '42 min ago',
    severity: 'medium',
  },
  {
    id: '4',
    type: 'success',
    title: 'Analysis Complete',
    description: 'Wallet clustering analysis finished successfully',
    timestamp: '1 hour ago',
  },
];

function getActivityIcon(type: ActivityItem['type']) {
  switch (type) {
    case 'alert':
      return <AlertCircle className="w-5 h-5" />;
    case 'success':
      return <CheckCircle className="w-5 h-5" />;
    case 'activity':
      return <Zap className="w-5 h-5" />;
    case 'security':
      return <Shield className="w-5 h-5" />;
  }
}

function getActivityColor(type: ActivityItem['type']) {
  switch (type) {
    case 'alert':
      return 'text-error';
    case 'success':
      return 'text-success';
    case 'activity':
      return 'text-accent';
    case 'security':
      return 'text-warning';
  }
}

export default function ActivityFeed() {
  return (
    <div className="glass p-6 rounded-lg">
      <h2 className="text-lg font-semibold text-foreground mb-6">Real-time Activity</h2>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="p-4 border border-border/50 rounded-lg hover:border-accent/30 transition-colors group"
          >
            <div className="flex gap-4">
              {/* Icon */}
              <div
                className={`flex-shrink-0 p-2 rounded-lg bg-foreground/5 ${getActivityColor(
                  activity.type
                )}`}
              >
                {getActivityIcon(activity.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-medium text-foreground text-sm">{activity.title}</h3>
                    <p className="text-xs text-foreground/60 mt-1">{activity.description}</p>
                  </div>
                  {activity.severity && (
                    <span
                      className={`flex-shrink-0 text-xs font-medium px-2 py-1 rounded ${
                        activity.severity === 'high'
                          ? 'bg-error/20 text-error'
                          : activity.severity === 'medium'
                            ? 'bg-warning/20 text-warning'
                            : 'bg-success/20 text-success'
                      }`}
                    >
                      {activity.severity.charAt(0).toUpperCase() + activity.severity.slice(1)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Timestamp */}
            <div className="mt-3 pl-12 text-xs text-foreground/50">{activity.timestamp}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
