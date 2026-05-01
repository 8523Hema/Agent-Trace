'use client';

import { AnalysisResult } from '@/lib/types';
import { useAnalysis } from '@/hooks/useAnalysis';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Copy, Loader2, AlertTriangle, Lightbulb } from 'lucide-react';
import { toast } from 'sonner';

interface RootCausePanelProps {
  runId: string;
  analysis?: AnalysisResult;
}

export function RootCausePanel({ runId, analysis }: RootCausePanelProps) {
  const { mutate: analyze, isPending } = useAnalysis();

  const handleCopy = () => {
    if (analysis?.fix_suggestion) {
      navigator.clipboard.writeText(analysis.fix_suggestion);
      toast.success('Fix copied to clipboard');
    }
  };

  if (!analysis) {
    return (
      <Card className="bg-slate-50 border-dashed border-2 shadow-sm mb-8">
        <CardContent className="flex flex-col items-center justify-center p-8 text-center space-y-4">
          <div className="rounded-full bg-purple-100 p-3 mb-2">
            <Sparkles className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-slate-800">AI Root Cause Analysis</h3>
          <p className="text-sm text-slate-500 max-w-md">
            Agent execution failed. Our Gemini-powered AI can analyze the trace and suggest a fix.
          </p>
          <Button 
            onClick={() => analyze(runId)} 
            disabled={isPending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing with Gemini Flash...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Analyze Failure
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4 mb-8">
      <Card className="border-red-200 shadow-sm overflow-hidden">
        <div className="bg-red-50 border-b border-red-100 px-6 py-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <h3 className="font-bold text-red-900 tracking-wide uppercase text-sm">Root Cause</h3>
        </div>
        <CardContent className="p-6 bg-white">
          <p className="text-slate-700 leading-relaxed">{analysis.root_cause}</p>
        </CardContent>
      </Card>

      <Card className="border-purple-200 shadow-sm overflow-hidden">
        <div className="bg-purple-50 border-b border-purple-100 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Lightbulb className="w-5 h-5 text-purple-600" />
            <h3 className="font-bold text-purple-900 tracking-wide uppercase text-sm">Fix Suggestion</h3>
          </div>
          <Button variant="outline" size="sm" onClick={handleCopy} className="h-8 gap-1.5 text-purple-700 border-purple-200 hover:bg-purple-100">
            <Copy className="w-3.5 h-3.5" />
            Copy Fix
          </Button>
        </div>
        <CardContent className="p-6 bg-white space-y-6">
          <p className="text-slate-700 leading-relaxed">{analysis.fix_suggestion}</p>
          
          {analysis.fix_code_hint && (
            <div className="rounded-md border border-green-200 overflow-hidden">
              <div className="bg-green-50 px-4 py-2 text-xs font-semibold text-green-800 border-b border-green-200">
                Code Hint
              </div>
              <pre className="p-4 bg-slate-950 text-green-400 text-sm overflow-x-auto">
                <code>{analysis.fix_code_hint}</code>
              </pre>
            </div>
          )}

          <div className="pt-4 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-1">
              <Badge variant="outline" className="bg-slate-100 text-slate-700 border-slate-200 font-medium">
                {analysis.failure_category}
              </Badge>
              <div className="flex-1 max-w-[200px] flex items-center gap-3">
                <Progress value={analysis.confidence * 100} className="h-2" />
                <span className="text-xs font-medium text-slate-500 whitespace-nowrap">
                  Gemini confidence: {Math.round(analysis.confidence * 100)}%
                </span>
              </div>
            </div>
            <div className="text-xs text-slate-400 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3" />
              Powered by {analysis.gemini_model || 'Gemini Flash'} (free)
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
