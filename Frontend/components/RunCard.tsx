import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "./StatusBadge";
import { Run } from "@/lib/types";

interface RunCardProps {
  run: Run;
}

export function RunCard({ run }: RunCardProps) {
  const isFailed = run.status.toLowerCase() === 'failed' || run.status.toLowerCase() === 'error';
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  return (
    <Link href={`/runs/${run.id}`}>
      <Card className={`hover:shadow-md transition-shadow cursor-pointer h-full ${isFailed ? 'border-l-4 border-l-red-500' : ''}`}>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start gap-4">
            <CardTitle className="text-lg font-medium truncate">
              {run.agent_name}
            </CardTitle>
            <StatusBadge status={run.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground flex flex-col space-y-1">
            <span>Started: {formatDate(run.started_at)}</span>
            {run.duration_ms !== undefined && run.duration_ms !== null && (
              <span>Duration: {(run.duration_ms / 1000).toFixed(2)}s</span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
