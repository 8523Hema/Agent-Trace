'use client';

import { useState } from 'react';
import { Step } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Check, X, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface StepTimelineProps {
  steps: Step[];
}

export function StepTimeline({ steps }: StepTimelineProps) {
  return (
    <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:ml-[2.25rem] before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
      {steps.map((step, index) => (
        <StepCard key={step.id || index} step={step} index={index} />
      ))}
    </div>
  );
}

function StepCard({ step, index }: { step: Step; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isFailed = step.status.toLowerCase() === 'failed' || step.status.toLowerCase() === 'error';

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'llm_call':
      case 'llm':
        return 'bg-blue-500 hover:bg-blue-600';
      case 'tool_call':
      case 'tool':
        return 'bg-purple-500 hover:bg-purple-600';
      case 'tool_result':
        return 'bg-indigo-500 hover:bg-indigo-600';
      case 'agent_action':
        return 'bg-orange-500 hover:bg-orange-600';
      case 'agent_finish':
        return 'bg-green-500 hover:bg-green-600';
      default:
        return 'bg-slate-500 hover:bg-slate-600';
    }
  };

  return (
    <div className="relative flex items-start gap-6">
      <div className={`mt-1.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-4 border-background ${isFailed ? 'bg-red-100 text-red-600 font-bold' : 'bg-green-100 text-green-600 font-bold'} shadow-sm relative z-10`}>
        {isFailed ? <X className="h-5 w-5" /> : <span>{index + 1}</span>}
      </div>
      
      <Card 
        className={`w-full transition-all cursor-pointer hover:shadow-md ${isFailed ? 'border-red-300 shadow-sm bg-red-50/10' : ''}`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Badge className={`${getTypeColor(step.step_type)} text-white border-none shadow-sm`}>
                {step.step_type}
              </Badge>
              <h3 className="font-semibold text-lg">{step.name}</h3>
            </div>
            <div className="flex items-center gap-3 text-muted-foreground text-sm font-medium">
              {step.duration_ms !== undefined && step.duration_ms !== null && (
                <span>{Math.round(step.duration_ms)}ms</span>
              )}
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </div>
          </div>

          {isFailed && step.error && (
            <div className="mt-2 p-3 bg-red-100 border border-red-200 rounded-md text-red-800 text-sm flex items-start gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
              <div className="break-words font-medium">
                {step.error}
              </div>
            </div>
          )}

          {isExpanded && (
            <div className="mt-4 space-y-4 pt-4 border-t border-slate-200" onClick={(e) => e.stopPropagation()}>
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider mb-2 text-slate-500">Input</h4>
                <pre className="bg-slate-900 text-blue-300 p-4 rounded-lg overflow-x-auto text-xs font-mono leading-relaxed shadow-inner border border-slate-800">
                  {JSON.stringify(step.input, null, 2)}
                </pre>
              </div>
              
              {step.output && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider mb-2 text-slate-500">Output</h4>
                  <pre className="bg-slate-900 text-indigo-300 p-4 rounded-lg overflow-x-auto text-xs font-mono leading-relaxed shadow-inner border border-slate-800">
                    {JSON.stringify(step.output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
