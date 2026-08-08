import { createContext, useContext, useMemo, useState } from 'react';

const RouterContext = createContext(null);

export function RouterProvider({ children }) {
  const [selectedRouterId, setSelectedRouterId] = useState(null);
  const [filters, setFilters] = useState({ building: 'all', firmware: 'all' });

  const value = useMemo(
    () => ({
      selectedRouterId,
      setSelectedRouterId,
      filters,
      setFilters,
    }),
    [selectedRouterId, filters]
  );

  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}

export function useRouterContext() {
  const context = useContext(RouterContext);

  if (!context) {
    throw new Error('useRouterContext must be used within a RouterProvider');
  }

  return context;
}
