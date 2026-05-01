import { useMutation, useQueryClient } from '@tanstack/react-query';
import { analyzeRun } from '../lib/api';

export const useAnalysis = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => analyzeRun(id),
    onSuccess: (data, variables) => {
      // Update the specific run detail in the cache with the analysis results
      queryClient.setQueryData(['run', variables], (oldData: any) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          analysis: data
        };
      });
    },
  });
};
