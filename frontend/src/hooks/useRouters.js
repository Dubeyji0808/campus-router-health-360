import { useCallback, useEffect, useState } from 'react';
import { askCopilot, getRankings, getRouterDetail } from '../services/api';

export function useRankings() {
  const [state, setState] = useState({ data: [], loading: true, error: null });

  const refetch = useCallback(async () => {
    setState((previous) => ({ ...previous, loading: true, error: null }));

    try {
      const data = await getRankings();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({ data: [], loading: false, error: error.message || 'Could not load rankings — check backend connection' });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useRouterDetail(routerId) {
  const [state, setState] = useState({ data: null, loading: false, error: null });

  const refetch = useCallback(async () => {
    if (!routerId) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    setState({ data: null, loading: true, error: null });

    try {
      const data = await getRouterDetail(routerId);
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({ data: null, loading: false, error: error.message || 'Could not load router details — check backend connection' });
    }
  }, [routerId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}

export function useCopilot() {
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const askQuestion = useCallback(async (questionText) => {
    const trimmed = String(questionText || '').trim();

    if (!trimmed) {
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await askCopilot(trimmed);
      setAnswer(result);
      return result;
    } catch (caughtError) {
      setError(caughtError.message || 'Could not get an answer. Try again.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetAnswer = useCallback(() => {
    setAnswer(null);
    setError(null);
  }, []);

  return { answer, loading, error, askQuestion, resetAnswer };
}
