'use client';

import { use } from 'react';
import Link from 'next/link';
import { useRunDetail } from '@/hooks/useRunDetail';
import { StatusBadge } from '@/components/StatusBadge';
import { StepTimeline } from '@/components/StepTimeline';
import { RootCausePanel } from '@/components/RootCausePanel';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Copy, Share2, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  const { data: run, isLoading, isError } = useRunDetail(id);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !run) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full hover:bg-slate-200">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">Run Details</h1>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Failed to load run details. It may not exist.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const isFailed = run.status.toLowerCase() === 'failed' || run.status.toLowerCase() === 'error';

  const handleShare = () => {
    const shareUrl = `${window.location.origin}/share/${run.share_token}`;
    navigator.clipboard.writeText(shareUrl);
    toast.success('Share link copied to clipboard');
  };

  return (
    <div className="max-w-4xl mx-auto pb-12">
      <div className="flex items-center gap-4 mb-8">
        <Link href="/">
          <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full hover:bg-slate-200">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold tracking-tight">{run.agent_name}</h1>
            <StatusBadge status={run.status} />
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
            {run.duration_ms !== undefined && run.duration_ms !== null && (
              <span>Duration: {(run.duration_ms / 1000).toFixed(2)}s</span>
            )}
            <span className="flex items-center gap-1.5 before:content-['•'] before:mr-2">
              <span className="font-semibold text-slate-700">{run.steps?.length || 0}</span> Steps
            </span>
          </div>
        </div>
      </div>

      {isFailed && (
        <RootCausePanel runId={run.id} analysis={run.analysis} />
      )}

      <div className="mt-8 mb-16">
        <h2 className="text-xl font-bold mb-6 tracking-tight">Execution Timeline</h2>
        {run.steps && run.steps.length > 0 ? (
          <StepTimeline steps={run.steps.sort((a, b) => a.step_index - b.step_index)} />
        ) : (
          <div className="p-8 text-center border rounded-lg bg-slate-50 text-slate-500">
            No steps recorded for this run.
          </div>
        )}
      </div>

      <div className="border-t pt-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Share2 className="w-5 h-5 text-slate-400" />
          <span className="font-medium text-slate-700">Share this run</span>
        </div>
        <Button variant="outline" onClick={handleShare} className="gap-2 border-slate-300">
          <Copy className="w-4 h-4" />
          Copy Link
        </Button>
      </div>
    </div>
  );
}
