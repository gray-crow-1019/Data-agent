const STATUS_STYLES: Record<string, string> = {
  completed: "bg-emerald-100 text-emerald-700",
  running: "bg-amber-100 text-amber-700",
  failed: "bg-rose-100 text-rose-600",
  pending: "bg-slate-100 text-slate-500",
};

export type Step = {
  name: string;
  status: string;
  onDownload?: () => void;
};

function formatName(name: string) {
  const map: Record<string, string> = {
    clarify: "澄清",
    resolve_metric: "解析指标",
    build_query_plan: "生成查询",
    govern: "治理校验",
    execute_query: "执行查询",
    quality_gate: "质量闸门",
    analyze: "分析",
    narrate: "叙事",
    package_artifact: "产物打包",
  };
  return map[name] || name;
}

export default function Stepper({ steps }: { steps: Step[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-4 lg:grid-cols-7">
      {steps.map((step) => (
        <div
          key={step.name}
          className="rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3 text-sm"
        >
          <div className="text-xs uppercase tracking-[0.2em] text-[color:var(--muted)]">
            {formatName(step.name)}
          </div>
          <div className="mt-2 flex items-center justify-between">
            <span className={`inline-flex rounded-full px-3 py-1 text-xs ${STATUS_STYLES[step.status] ?? ""}`}>
              {step.status}
            </span>
            {step.onDownload && (
              <button
                className="rounded-full border border-[color:var(--border)] px-2 py-1 text-[10px]"
                onClick={step.onDownload}
              >
                下载
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
