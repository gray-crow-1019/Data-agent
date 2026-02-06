import { FindingCard as FindingCardType } from "../../lib/types";
import { formatConfidence } from "../../lib/format";

export default function FindingCard({ finding }: { finding: FindingCardType }) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{finding.conclusion}</h3>
        <span className="text-xs text-[color:var(--muted)]">
          {formatConfidence(finding.confidence)} 置信度
        </span>
      </div>
      {finding.detail && <p className="mt-2 text-sm text-[color:var(--muted)]">{finding.detail}</p>}
      <p className="mt-3 rounded-xl bg-black/5 p-2 text-xs text-[color:var(--ink)]">
        证据: {finding.evidence}
      </p>
      {finding.alternative_explanations?.length ? (
        <div className="mt-3 text-xs text-[color:var(--muted)]">
          备选解释: {finding.alternative_explanations.join(", ")}
        </div>
      ) : null}
      {finding.next_steps?.length ? (
        <div className="mt-1 text-xs text-[color:var(--muted)]">
          下一步建议: {finding.next_steps.join(", ")}
        </div>
      ) : null}
    </div>
  );
}
