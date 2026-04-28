'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const gasData = [
  { time: '00:00', gwei: 45 },
  { time: '04:00', gwei: 52 },
  { time: '08:00', gwei: 38 },
  { time: '12:00', gwei: 65 },
  { time: '16:00', gwei: 48 },
  { time: '20:00', gwei: 72 },
  { time: '24:00', gwei: 55 },
];

export default function GasFeesChart() {
  return (
    <div className="glass p-6 rounded-lg">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">Gas Fees Trend</h2>
        <p className="text-sm text-foreground/60 mt-1">Ethereum network gas price (Gwei)</p>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={gasData}>
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
            <Line
              type="monotone"
              dataKey="gwei"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
