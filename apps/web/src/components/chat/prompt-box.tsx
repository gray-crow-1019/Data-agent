import Button from "../ui/button";

export default function PromptBox({
  value,
  onChange,
  onSubmit,
  onFileChange,
  fileName,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onFileChange: (file: File | null) => void;
  fileName?: string;
  disabled?: boolean;
}) {
  return (
    <div className="glass mt-6 flex flex-col gap-3 rounded-2xl p-4">
      <textarea
        className="min-h-[96px] w-full resize-none bg-transparent text-sm text-[color:var(--ink)] focus:outline-none"
        placeholder="提一个业务问题，比如“上周哪里流失激增？”"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <div className="flex flex-wrap gap-2 text-xs text-[color:var(--muted)]">
        <span className="rounded-full border border-[color:var(--border)] px-3 py-1">对比基准</span>
        <span className="rounded-full border border-[color:var(--border)] px-3 py-1">按地区分组</span>
        <span className="rounded-full border border-[color:var(--border)] px-3 py-1">添加过滤</span>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-xs text-[color:var(--muted)]">
        <input
          type="file"
          accept=".csv,.xlsx,.xls,.mat"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
        {fileName && <span>已选择：{fileName}</span>}
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-[color:var(--muted)]">
          提示：建议包含时间范围与分组口径。
        </span>
        <Button onClick={onSubmit} disabled={disabled}>
          {disabled ? "运行中..." : "开始分析"}
        </Button>
      </div>
    </div>
  );
}
