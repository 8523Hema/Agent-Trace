'use client';

import { useRuns } from '@/hooks/useRuns';
import { RunCard } from '@/components/RunCard';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const { data: runs, isLoading, isError } = useRuns();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AgentTrace — All Runs</h1>
          <p className="text-muted-foreground mt-2">Loading runs...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-xl bg-muted animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AgentTrace — All Runs</h1>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Failed to load runs. Ensure the backend is running.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AgentTrace — All Runs</h1>
        <p className="text-muted-foreground mt-2">
          {runs?.length === 1 ? '1 Run' : `${runs?.length || 0} Runs`} Total
        </p>
      </div>

      {!runs || runs.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 text-center border rounded-lg bg-card text-card-foreground shadow-sm">
          <h3 className="mt-4 text-lg font-semibold">No runs found</h3>
          <p className="mb-4 mt-2 text-sm text-muted-foreground">
            Start an agent to see its trace here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {runs.map((run) => (
            <RunCard key={run.id} run={run} />
          ))}
        </div>
      )}
    </div>
  );
}
