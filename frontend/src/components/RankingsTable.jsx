import { useMemo } from 'react';
import { useRankings } from '../hooks/useRouters';
import { useRouterContext } from '../context/RouterContext';
import { getScoreColor, getScoreLabel } from '../utils/formatters';

export default function RankingsTable() {
  const { data, loading, error, refetch } = useRankings();
  const { selectedRouterId, setSelectedRouterId, filters } = useRouterContext();

  const filteredData = useMemo(() => {
    const next = data.filter((router) => {
      const matchesBuilding = filters.building === 'all' || router.building === filters.building;
      const matchesFirmware = filters.firmware === 'all' || router.firmware_version === filters.firmware;
      return matchesBuilding && matchesFirmware;
    });

    return [...next].sort((a, b) => Number(a.health_score) - Number(b.health_score));
  }, [data, filters]);

  const worstTen = filteredData.slice(0, 10);

  const handleRowKeyDown = (event, routerId) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setSelectedRouterId(routerId);
    }
  };

  if (loading) {
    return (
      <div className="panel rankings-panel">
        <div className="panel-header">
          <h3>Router rankings</h3>
        </div>
        <div className="loading-box">
          <div className="spinner" />
          <span>Loading rankings...</span>
        </div>
        <div className="skeleton-stack">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="skeleton-row" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel rankings-panel">
        <div className="panel-header">
          <h3>Router rankings</h3>
        </div>
        <div className="state-box error-box">
          <p>{error}</p>
          <button type="button" className="primary-button" onClick={refetch}>Retry</button>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="panel rankings-panel">
        <div className="panel-header">
          <h3>Router rankings</h3>
        </div>
        <div className="state-box empty-box">
          <p>No router data available</p>
        </div>
      </div>
    );
  }

  if (filteredData.length === 0) {
    return (
      <div className="panel rankings-panel">
        <div className="panel-header">
          <h3>Router rankings</h3>
        </div>
        <div className="state-box empty-box">
          <p>No routers match the selected filters.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel rankings-panel">
      <div className="panel-header">
        <h3>Router rankings</h3>
        <span className="count-badge">{worstTen.length} shown</span>
      </div>

      <div className="table-wrap">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>Router ID</th>
              <th>Building</th>
              <th>Health score</th>
              <th>Bad hours</th>
            </tr>
          </thead>
          <tbody>
            {worstTen.map((router) => {
              const isSelected = router.router_id === selectedRouterId;
              const scoreColor = getScoreColor(router.health_score);
              const scoreLabel = getScoreLabel(router.health_score);

              return (
                <tr
                  key={router.router_id}
                  className={isSelected ? 'selected-row' : ''}
                  onClick={() => setSelectedRouterId(router.router_id)}
                  onKeyDown={(event) => handleRowKeyDown(event, router.router_id)}
                  tabIndex={0}
                >
                  <td>{router.router_id}</td>
                  <td>{router.building}</td>
                  <td>
                    <span className={`score-badge badge-${scoreColor}`}>
                      {router.health_score}
                      <small>{scoreLabel}</small>
                    </span>
                  </td>
                  <td>{router.bad_hours_count}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
