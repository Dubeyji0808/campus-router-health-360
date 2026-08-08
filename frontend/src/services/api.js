const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function ensureJson(response) {
  if (response.status === 204) return null;
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return response.text();
}

async function apiRequest(url, options = {}, fallbackMessage) {
  try {
    const response = await fetch(`${BASE_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(fallbackMessage);
    }

    return await ensureJson(response);
  } catch (error) {
    const message = error instanceof Error && error.message ? error.message : fallbackMessage;
    throw new Error(message);
  }
}

export async function getRankings() {
  try {
    const payload = await apiRequest('/api/rankings', { method: 'GET' }, 'Could not load rankings — check backend connection');
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.rankings)) return payload.rankings;
    if (Array.isArray(payload?.data)) return payload.data;
    return [];
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Could not load rankings — check backend connection');
  }
}

export async function getRouterDetail(routerId) {
  try {
    const payload = await apiRequest(
      `/api/router/${encodeURIComponent(routerId)}`,
      { method: 'GET' },
      'Could not load router details — check backend connection'
    );
    return payload || null;
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Could not load router details — check backend connection');
  }
}

export async function askCopilot(question) {
  try {
    const payload = await apiRequest(
      '/api/copilot',
      {
        method: 'POST',
        body: JSON.stringify({ question }),
      },
      'Could not ask copilot — check backend connection'
    );
    return payload || null;
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : 'Could not ask copilot — check backend connection');
  }
}

export async function getBuildings() {
  const rankings = await getRankings();
  return [...new Set(rankings.map((router) => router.building).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

export async function getFirmwareVersions() {
  const rankings = await getRankings();
  return [...new Set(rankings.map((router) => router.firmware_version).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}
