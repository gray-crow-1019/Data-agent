import { MetricCard as MetricCardType } from "../../lib/types";
import Badge from "../ui/badge";

export default function MetricCard({ metric }: { metric: MetricCardType }) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{metric.name}</h3>
        <Badge>{metric.status ?? "draft"}</Badge>
      </div>
      <p className="mt-2 text-sm text-[color:var(--muted)]">{metric.definition}</p>
      <div className="mt-3 grid gap-2 text-xs text-[color:var(--muted)]">
        {metric.granularity && <div>Granularity: {metric.granularity}</div>}
        {metric.version && <div>Version: {metric.version}</div>}
        {metric.available_dimensions?.length ? (
          <div>Dimensions: {metric.available_dimensions.join(", ")}</div>
        ) : null}
        {metric.default_filters && Object.keys(metric.default_filters).length ? (
          <div>Default filters: {Object.keys(metric.default_filters).join(", ")}</div>
        ) : null}
        {metric.owner && <div>Owner: {metric.owner}</div>}
      </div>
    </div>
  );
}
