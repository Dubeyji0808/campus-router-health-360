import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function metricDotRenderer(props) {
  const { cx, cy, payload } = props;
  const badMarker = payload?.is_bad || payload?.bad_hour || payload?.is_bad_hour || payload?.isBad;

  return (
    <circle
      cx={cx}
      cy={cy}
      r={badMarker ? 5 : 3}
      fill={badMarker ? '#ef4444' : '#2d7ff9'}
      stroke="none"
    />
  );
}

export default function MetricChart({ data = [], metricKey, title }) {
  if (!data || data.length === 0) {
    return <div className="metric-card"><h4>{title}</h4><p className="empty-inline">No metric data available</p></div>;
  }

  const chartData = data.map((point, index) => ({
    ...point,
    hour: point.hour ?? point.timestamp ?? point.time ?? String(index + 1),
    value: Number(point[metricKey] ?? 0),
  }));

  return (
    <div className="metric-card">
      <h4>{title}</h4>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dfe7f1" />
            <XAxis dataKey="hour" stroke="#516074" tick={{ fontSize: 11 }} />
            <YAxis stroke="#516074" tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#2d7ff9"
              strokeWidth={2}
              dot={metricDotRenderer}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
