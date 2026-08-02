import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

export default function LineChartWidget({ data, title, lines = [{ key: 'messages', color: '#3B82F6', name: 'Messages' }] }) {
  return (
    <div className="glass-card p-6">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          {lines.map(({ key, color, name }) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={color}
              strokeWidth={2}
              dot={{ r: 4 }}
              name={name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ActivityChart({ data, title }) {
  return (
    <LineChartWidget
      data={data}
      title={title}
      lines={[
        { key: 'messages', color: '#3B82F6', name: 'Messages' },
        { key: 'score', color: '#22c55e', name: 'Avg Score' },
      ]}
    />
  );
}
