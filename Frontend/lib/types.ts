export interface Step {
  id: string;
  run_id: string;
  step_index: number;
  step_type: string;
  name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  error?: string;
  status: string;
  started_at: string;
  ended_at?: string;
  duration_ms?: number;
  metadata?: Record<string, any>;
}

export interface AnalysisResult {
  id: string;
  run_id: string;
  root_cause: string;
  fix_suggestion: string;
  fix_code_hint?: string;
  confidence: number;
  failure_category: string;
  analyzed_at: string;
  gemini_model: string;
}

export interface Run {
  id: string;
  agent_name: string;
  status: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  error?: string;
  started_at: string;
  ended_at?: string;
  duration_ms?: number;
  share_token: string;
  steps: Step[];
  analysis?: AnalysisResult;
}
