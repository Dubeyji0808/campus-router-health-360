import { useRouterContext } from '../context/RouterContext';
import FilterBar from '../components/FilterBar';
import RankingsTable from '../components/RankingsTable';
import RouterDetailPanel from '../components/RouterDetailPanel';

export default function Dashboard() {
  const { selectedRouterId } = useRouterContext();

  return (
    <main className="dashboard-shell">
      <FilterBar />

      <div className="dashboard-grid">
        <RankingsTable />

        {selectedRouterId ? (
          <RouterDetailPanel />
        ) : (
          <div className="panel empty-state-panel">
            <div className="empty-state-icon">⌁</div>
            <h3>Select a router to view details and ask the copilot</h3>
          </div>
        )}
      </div>
    </main>
  );
}
