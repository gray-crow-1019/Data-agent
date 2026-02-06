export type TaskSpec = {
  id: string;
  question: string;
  created_at: string;
  status: string;
  meta: Record<string, unknown>;
  labels?: string[];
};

export type ClarifyParams = {
  time_range?: string;
  granularity?: string;
  subject?: string;
  filters?: Record<string, unknown>;
  comparison?: string;
  missing?: string[];
};

export type RunStep = {
  name: string;
  status: string;
  started_at: string;
  ended_at?: string;
  duration_ms?: number;
  summary?: string;
  output_ref?: string;
};

export type MetricCard = {
  name: string;
  definition: string;
  granularity?: string;
  default_filters?: Record<string, unknown>;
  version?: string;
  available_dimensions?: string[];
  owner?: string;
  status?: string;
};

export type QueryCard = {
  title: string;
  sql: string;
  engine: string;
  params?: Record<string, unknown>;
  scan_cost?: string;
  row_count?: number;
  duration_ms?: number;
  data_version?: string;
  cache_hit?: boolean;
  estimated_cost?: string;
  notes?: string;
};

export type QualityCard = {
  check: string;
  passed: boolean;
  reason?: string;
  freshness_hours?: number;
  missing_rate?: number;
  anomaly_score?: number;
  drift_score?: number;
  constraints?: Record<string, unknown>;
};

export type FindingCard = {
  conclusion: string;
  evidence: string;
  confidence: string;
  alternative_explanations?: string[];
  next_steps?: string[];
  detail?: string;
};

export type TaskResult = {
  task_id: string;
  status: string;
  state?: string;
  steps?: RunStep[];
  clarify?: ClarifyParams;
  metrics: MetricCard[];
  queries: QueryCard[];
  quality: QualityCard[];
  findings: FindingCard[];
  narrative?: string;
  chart?: Record<string, unknown>;
  charts?: Record<string, unknown>[];
  chart_plan?: Record<string, unknown>[];
  chart_insights?: Record<string, unknown>[];
  analysis_type?: string;
  analysis_reason?: string;
  preview_rows?: Record<string, unknown>[];
  raw_preview_rows?: Record<string, unknown>[];
  processed_preview_rows?: Record<string, unknown>[];
  preprocessing?: Record<string, unknown>;
  dataset_profile?: Record<string, unknown>;
  warnings?: string[];
  artifacts: Record<string, unknown>;
};

export type TaskResponse = {
  spec: TaskSpec;
  result?: TaskResult;
};
