import { useQuery } from '@tanstack/react-query';
import { getRuns } from '../lib/api';

export const useRuns = () => {
  return useQuery({
    queryKey: ['runs'],
    queryFn: getRuns,
    refetchInterval: 5000,
  });
};
