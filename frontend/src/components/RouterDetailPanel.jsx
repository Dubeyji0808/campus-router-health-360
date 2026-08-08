import MetricChart from './MetricChart';
import CopilotBox from './CopilotBox';
import { useRouterContext } from '../context/RouterContext';
import { useRouterDetail } from '../hooks/useRouters';
import { getScoreColor, getScoreLabel } from '../utils/formatters';

export default function RouterDetailPanel() {
  const { selectedRouterId } = useRouterContext();
  const { data, loading, error, refetch } = useRouterDetail(selectedRouterId);

  if (!selectedRouterId) return null;

  if (loading) {
    return (
      <div className="panel detail-panel">
        <div className="loading-box">
          <div className="spinner" />
          <span>Loading router details...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel detail-panel">
        <div className="state-box error-box">
          <p>Could not load router details</p>
          <button type="button" className="primary-button" onClick={refetch}>Retry</button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const metadata = data.info || {};
  const metrics = data.metrics_timeseries || [];
  const complaints = [...(data.complaints || [])].sort((a, b) => new Date(b.date) - new Date(a.date));
  const scoreColor = getScoreColor(data.health_score);
  const scoreLabel = getScoreLabel(data.health_score);

  return (
    <div className="panel detail-panel">
      <div className="detail-header-row">
        <div>
          <p className="muted-label">Router</p>
          <h3>{data.router_id}</h3>
        </div>
        <div className={`score-badge badge-${scoreColor} detail-badge`}>
          {data.health_score}
          <small>{scoreLabel}</small>
        </div>
      </div>

      <div className="metadata-row">
        <span><strong>Building:</strong> {metadata.building || 'N/A'}</span>
        <span><strong>Room:</strong> {metadata.room || 'N/A'}</span>
        <span><strong>Model:</strong> {metadata.model || 'N/A'}</span>
        <span><strong>Firmware:</strong> {metadata.firmware_version || 'N/A'}</span>
        <span><strong>User type:</strong> {metadata.user_type || 'N/A'}</span>
      </div>

      <div className="metrics-grid">
        <MetricChart data={metrics} metricKey="latency_ms" title="Latency (ms)" />
        <MetricChart data={metrics} metricKey="packet_loss_pct" title="Packet loss (%)" />
      </div>

      <div className="complaints-section">
        <h4>Complaints</h4>
        {complaints.length === 0 ? (
          <p className="empty-inline">No complaints logged for this router</p>
        ) : (
          <div className="complaint-list">
            {complaints.map((complaint) => (
              <div className="complaint-card" key={complaint.ticket_id || complaint.id || complaint.date}>
                <div className="complaint-meta">
                  <strong>{complaint.ticket_id || 'Ticket'}</strong>
                  <span>{complaint.date || 'Unknown date'}</span>
                </div>
                <p>{complaint.complaint_text || complaint.text || 'No complaint text provided'}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <CopilotBox routerId={selectedRouterId} />
    </div>
  );
}
