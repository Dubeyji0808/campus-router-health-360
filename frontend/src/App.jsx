import { RouterProvider } from './context/RouterContext';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <RouterProvider>
      <div className="app-shell">
        <header className="app-header">
          <div>
            <p className="eyebrow">Operations dashboard</p>
            <h1>Campus Router Health 360</h1>
          </div>
        </header>
        <Dashboard />
      </div>
    </RouterProvider>
  );
}
