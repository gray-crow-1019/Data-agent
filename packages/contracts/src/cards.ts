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
