import { useEffect, useState } from "react";
import { getCatalog } from "../lib/api";

type Metric = {
  name: string;
  owner?: string;
  status?: string;
  version?: string;
  granularity?: string;
};

type Dimension = {
  name: string;
  description: string;
  hierarchy?: string;
  primary_key?: string;
};

const ASSETS = [
  { table: "analytics.activation_rates", freshness: "hourly", lineage: "events -> metrics", tier: "gold" },
  { table: "analytics.sessions", freshness: "daily", lineage: "events -> sessions", tier: "silver" },
];

export default function MetaBrowser() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [dimensions, setDimensions] = useState<Dimension[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    getCatalog()
      .then((catalog) => {
        setMetrics((catalog.metrics ?? []) as Metric[]);
        setDimensions((catalog.dimensions ?? []) as Dimension[]);
      })
      .catch(() => {
        setMetrics([]);
        setDimensions([]);
      });
  }, []);

  const filteredMetrics = metrics.filter((metric) =>
    `${metric.name} ${metric.owner ?? ""}`.toLowerCase().includes(query.toLowerCase())
  );
  const filteredDimensions = dimensions.filter((dim) =>
    `${dim.name} ${dim.description}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="font-serif text-2xl">语义目录</h2>
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          浏览 Agent 使用的可信指标与维度。
        </p>
      </div>
      <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
        <input
          className="w-full bg-transparent text-sm text-[color:var(--ink)] focus:outline-none"
          placeholder="搜索指标、维度、负责人..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>
      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
          <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">指标</h3>
          <ul className="mt-4 space-y-3">
            {filteredMetrics.map((metric) => (
              <li
                key={metric.name}
                className="flex items-center justify-between rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3"
              >
                <div>
                  <div className="font-medium">{metric.name}</div>
                  <div className="text-xs text-[color:var(--muted)]">
                    Owner: {metric.owner ?? "n/a"} · {metric.granularity ?? "n/a"} ·{" "}
                    {metric.version ?? "n/a"}
                  </div>
                </div>
                <span className="rounded-full bg-[color:var(--accent)]/10 px-3 py-1 text-xs text-[color:var(--accent)]">
                  {metric.status ?? "unknown"}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
          <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">维度</h3>
          <ul className="mt-4 space-y-3">
            {filteredDimensions.map((dim) => (
              <li
                key={dim.name}
                className="rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3"
              >
                <div className="font-medium">{dim.name}</div>
                <div className="text-xs text-[color:var(--muted)]">{dim.description}</div>
                <div className="mt-1 text-xs text-[color:var(--muted)]">
                  层级: {dim.hierarchy ?? "n/a"} · 主键: {dim.primary_key ?? "n/a"}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
      <section className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
        <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">数据资产</h3>
        <ul className="mt-4 space-y-3">
          {ASSETS.map((asset) => (
            <li
              key={asset.table}
              className="flex flex-col gap-1 rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3 text-xs text-[color:var(--muted)]"
            >
              <div className="text-sm font-medium text-[color:var(--ink)]">{asset.table}</div>
              <div>更新频率: {asset.freshness}</div>
              <div>血缘: {asset.lineage}</div>
              <div>认证等级: {asset.tier}</div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
