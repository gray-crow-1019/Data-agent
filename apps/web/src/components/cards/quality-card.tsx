import { QualityCard as QualityCardType } from "../../lib/types";

export default function QualityCard({ quality }: { quality: QualityCardType }) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">{quality.check}</h3>
        <span
          className={`rounded-full px-3 py-1 text-xs ${
            quality.passed ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-600"
          }`}
        >
          {quality.passed ? "Pass" : "Fail"}
        </span>
      </div>
      <div className="mt-2 space-y-1 text-xs text-[color:var(--muted)]">
        {quality.reason && <div>原因: {quality.reason}</div>}
        {quality.freshness_hours !== undefined && <div>新鲜度: {quality.freshness_hours}h</div>}
        {quality.missing_rate !== undefined && <div>缺失率: {quality.missing_rate * 100}%</div>}
        {quality.anomaly_score !== undefined && <div>异常分数: {quality.anomaly_score}</div>}
        {quality.drift_score !== undefined && <div>漂移分数: {quality.drift_score}</div>}
        {quality.constraints && Object.keys(quality.constraints).length ? (
          <div>约束: {Object.keys(quality.constraints).join(", ")}</div>
        ) : null}
      </div>
    </div>
  );
}
