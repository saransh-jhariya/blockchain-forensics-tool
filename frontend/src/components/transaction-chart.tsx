'use client';

import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const transactionData = [
  { time: '00:00', txns: 120, volume: 2400 },
  { time: '04:00', txns: 150, volume: 2210 },
  { time: '08:00', txns: 200, volume: 2290 },
  { time: '12:00', txns: 220, volume: 2000 },
  { time: '16:00', txns: 190, volume: 2181 },
  { time: '20:00', txns: 250, volume: 2500 },
  { time: '24:00', txns: 280, volume: 2100 },
];

export default function TransactionChart() {
  return (
    <div className="glass p-6 rounded-lg">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">Transaction Activity</h2>
        <p className="text-sm text-foreground/60 mt-1">24-hour transaction volume and count</p>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={transactionData}>
            <defs>
              <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d9ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00d9ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 217, 255, 0.1)" />
            <XAxis
              dataKey="time"
              stroke="rgba(240, 240, 248, 0.5)"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="rgba(240, 240, 248, 0.5)" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(20, 20, 32, 0.9)',
                border: '1px solid rgba(0, 217, 255, 0.3)',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#f0f0f8' }}
            />
            <Area
              type="monotone"
              dataKey="volume"
              stroke="#00d9ff"
              fillOpacity={1}
              fill="url(#colorVolume)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
