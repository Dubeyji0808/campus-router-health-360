import { useMemo } from 'react';
import { useRankings } from '../hooks/useRouters';
import { useRouterContext } from '../context/RouterContext';

export default function FilterBar() {
  const { data } = useRankings();
  const { filters, setFilters } = useRouterContext();

  const buildingOptions = useMemo(
    () => [...new Set(data.map((router) => router.building).filter(Boolean))].sort((a, b) => a.localeCompare(b)),
    [data]
  );

  const firmwareOptions = useMemo(
    () => [...new Set(data.map((router) => router.firmware_version).filter(Boolean))].sort((a, b) => a.localeCompare(b)),
    [data]
  );

  const hasActiveFilters = filters.building !== 'all' || filters.firmware !== 'all';

  const updateFilter = (key, value) => {
    setFilters((previous) => ({ ...previous, [key]: value }));
  };

  return (
    <div className="filter-bar panel">
      <div className="filter-field">
        <label htmlFor="building-filter">Building</label>
        <select
          id="building-filter"
          value={filters.building}
          onChange={(event) => updateFilter('building', event.target.value)}
        >
          <option value="all">All buildings</option>
          {buildingOptions.map((building) => (
            <option key={building} value={building}>
              {building}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-field">
        <label htmlFor="firmware-filter">Firmware</label>
        <select
          id="firmware-filter"
          value={filters.firmware}
          onChange={(event) => updateFilter('firmware', event.target.value)}
        >
          <option value="all">All firmware</option>
          {firmwareOptions.map((firmware) => (
            <option key={firmware} value={firmware}>
              {firmware}
            </option>
          ))}
        </select>
      </div>

      {hasActiveFilters && (
        <button
          type="button"
          className="secondary-button"
          onClick={() => setFilters({ building: 'all', firmware: 'all' })}
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
