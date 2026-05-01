import { useQuery } from '@tanstack/react-query';
import { getRunById } from '../lib/api';

export const useRunDetail = (id: string | null | undefined) => {
  return useQuery({
    queryKey: ['run', id],
    queryFn: () => getRunById(id as string),
    enabled: !!id,
    refetchInterval: (query) => {
      // Keep polling if status is running, otherwise stop
      const status = query.state.data?.status?.toLowerCase();
      if (status === 'completed' || status === 'success' || status === 'failed' || status === 'error') {
        return false;
      }
      return 5000;
    },
  });
};
