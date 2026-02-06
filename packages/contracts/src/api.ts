import { FindingCard, MetricCard, QueryCard, QualityCard } from "./cards";

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

export type TaskSpec = {
  id: string;
  question: string;
  created_at: string;
  status: string;
  meta: Record<string, unknown>;
  labels?: string[];
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
  preview_rows?: Record<string, unknown>[];
  warnings?: string[];
  artifacts: Record<string, unknown>;
};

export type TaskResponse = {
  spec: TaskSpec;
  result?: TaskResult;
};
