import { QueryCard as QueryCardType } from "../../lib/types";

export default function QueryCard({ query }: { query: QueryCardType }) {
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{query.title}</h3>
        <span className="text-xs text-[color:var(--muted)]">{query.engine}</span>
      </div>
      <pre className="mt-3 whitespace-pre-wrap rounded-xl bg-black/5 p-3 text-xs text-[color:var(--ink)]">
        {query.sql}
      </pre>
      <div className="mt-3 grid gap-2 text-xs text-[color:var(--muted)]">
        <div>扫描成本: {query.scan_cost ?? query.estimated_cost ?? "n/a"}</div>
        {query.params && Object.keys(query.params).length ? (
          <div>参数: {Object.keys(query.params).join(", ")}</div>
        ) : null}
        <div>行数: {query.row_count ?? "n/a"}</div>
        <div>耗时: {query.duration_ms ? `${query.duration_ms} ms` : "n/a"}</div>
        <div>数据版本: {query.data_version ?? "n/a"}</div>
        <div>缓存命中: {query.cache_hit === undefined ? "n/a" : query.cache_hit ? "是" : "否"}</div>
        {query.notes && <div>说明: {query.notes}</div>}
      </div>
    </div>
  );
}
