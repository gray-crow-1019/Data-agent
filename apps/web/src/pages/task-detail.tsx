import { useEffect, useState } from "react";
import ChartView from "../components/charts/chart-view";
import ExportPanel from "../components/export/export-panel";
import FindingCard from "../components/cards/finding-card";
import QueryCard from "../components/cards/query-card";
import QualityCard from "../components/cards/quality-card";
import Stepper from "../components/progress/stepper";
import DataPreview from "../components/table/data-preview";
import Button from "../components/ui/button";
import { downloadStepOutput, getTask, listTasks, rerunTask } from "../lib/api";
import { TaskResponse } from "../lib/types";

export default function TaskDetail() {
  const [taskId, setTaskId] = useState("");
  const [record, setRecord] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentTasks, setRecentTasks] = useState<TaskResponse[]>([]);

  const formatTaskOption = (item: TaskResponse) => {
    const id = item.spec.id;
    const question = item.spec.question || "";
    const shortQuestion = question.length > 36 ? `${question.slice(0, 36)}...` : question;
    return `${id} · ${shortQuestion}`;
  };

  useEffect(() => {
    listTasks(20)
      .then((records) => setRecentTasks(records))
      .catch(() => {
        setRecentTasks([]);
      });
  }, []);


  const handleLoad = async () => {
    if (!taskId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getTask(taskId.trim());
      setRecord(res);
    } catch (err) {
      setError("任务不存在或请求失败。");
    } finally {
      setLoading(false);
    }
  };

  const handleRerun = async () => {
    if (!record) return;
    setLoading(true);
    setError(null);
    try {
      const res = await rerunTask(record.spec.id);
      setRecord(res);
    } catch (err) {
      setError("复跑失败。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="flex flex-col gap-6 md:flex-row">
        <div className="flex-1">
          <h2 className="font-serif text-2xl">任务产物</h2>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            查看生成的查询、质量闸门与分析结论。
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3 text-sm">
            状态: <span className="text-[color:var(--accent)]">已完成</span>
          </div>
          <Button variant="ghost" onClick={handleRerun} disabled={loading || !record}>
            {loading ? "运行中..." : "复跑任务"}
          </Button>
        </div>
      </section>
      <section className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
        <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">加载任务</h3>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
          <select
            className="w-full min-w-0 max-w-full overflow-hidden text-ellipsis whitespace-nowrap rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3 text-sm"
            value={taskId}
            onChange={(event) => setTaskId(event.target.value)}
          >
            <option value="">选择任务回放...</option>
            {recentTasks.map((item) => (
              <option key={item.spec.id} value={item.spec.id}>
                {formatTaskOption(item)}
              </option>
            ))}
          </select>
          <Button onClick={handleLoad} disabled={loading || !taskId} className="w-full md:w-auto">
            加载
          </Button>
        </div>
        {error && <div className="mt-3 text-xs text-rose-600">{error}</div>}
      </section>
      <section className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
        <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">执行步骤</h3>
        <div className="mt-4">
          <Stepper
            steps={
              record?.result?.steps?.length
                ? record.result.steps.map((step) => ({
                    name: step.name,
                    status: step.status,
                    onDownload: async () => {
                      if (!record?.spec.id) return;
                      try {
                        const res = await downloadStepOutput(record.spec.id, step.name);
                        const blob = new Blob([JSON.stringify(res.payload, null, 2)], {
                          type: "application/json",
                        });
                        const url = URL.createObjectURL(blob);
                        const anchor = document.createElement("a");
                        anchor.href = url;
                        anchor.download = `${step.name}.json`;
                        anchor.click();
                        URL.revokeObjectURL(url);
                      } catch {
                        // ignore
                      }
                    },
                  }))
                : [
                    { name: "Clarify", status: "completed" },
                    { name: "Resolve", status: "completed" },
                    { name: "Query", status: "completed" },
                    { name: "QA", status: "completed" },
                    { name: "Analyze", status: "completed" },
                    { name: "Narrate", status: "completed" },
                  ]
            }
          />
        </div>
      </section>
      {record?.result?.charts && record.result.charts.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2">
          {record.result.charts.map((option, index) => {
            const insight = record.result?.chart_insights?.[index];
            return (
              <div key={`chart-${index}`} className="space-y-2">
                <ChartView option={option} />
                {insight && (
                  <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-3 text-xs text-[color:var(--muted)]">
                    <div className="text-[color:var(--ink)]">{String(insight.insight ?? "")}</div>
                    {insight.caveat && <div className="mt-2">注意：{String(insight.caveat)}</div>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <ChartView option={record?.result?.chart} />
      )}
      {record?.result?.chart_plan && record.result.chart_plan.length > 0 && (
        <section className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
          <div className="text-sm font-medium text-[color:var(--ink)]">图表规划</div>
          <div className="mt-2 space-y-2">
            {record.result.chart_plan.map((item, index) => (
              <div key={`plan-${index}`} className="rounded-xl border border-[color:var(--border)] bg-white/60 px-3 py-2">
                <div className="text-[color:var(--ink)]">
                  {String(item.title ?? "图表")} · {String(item.type ?? "")}
                </div>
                <div className="text-[color:var(--muted)]">
                  {String(item.reason ?? "未提供原因")}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
      {record?.result?.artifacts?.report_structured && (
        <section className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
          <div className="text-sm font-medium text-[color:var(--ink)]">结构化报告</div>
          <div className="mt-2 grid gap-3 md:grid-cols-2">
            <div>
              <div className="font-medium text-[color:var(--ink)]">方法</div>
              {((record.result.artifacts.report_structured as any).methods ?? []).map((item: string, idx: number) => (
                <div key={`m-${idx}`}>- {item}</div>
              ))}
            </div>
            <div>
              <div className="font-medium text-[color:var(--ink)]">假设</div>
              {((record.result.artifacts.report_structured as any).assumptions ?? []).map((item: string, idx: number) => (
                <div key={`a-${idx}`}>- {item}</div>
              ))}
            </div>
            <div>
              <div className="font-medium text-[color:var(--ink)]">结论</div>
              {((record.result.artifacts.report_structured as any).conclusions ?? []).map((item: string, idx: number) => (
                <div key={`c-${idx}`}>- {item}</div>
              ))}
            </div>
            <div>
              <div className="font-medium text-[color:var(--ink)]">限制</div>
              {((record.result.artifacts.report_structured as any).limitations ?? []).map((item: string, idx: number) => (
                <div key={`l-${idx}`}>- {item}</div>
              ))}
            </div>
          </div>
        </section>
      )}
      <section className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">取数方案</h3>
          {(record?.result?.queries ?? []).map((query) => (
            <QueryCard key={query.title} query={query} />
          ))}
        </div>
        <div className="space-y-4">
          <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">质量闸门</h3>
          {(record?.result?.quality ?? []).map((quality) => (
            <QualityCard key={quality.check} quality={quality} />
          ))}
        </div>
      </section>
      <section className="grid gap-6 md:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <DataPreview
            rows={record?.result?.raw_preview_rows ?? record?.result?.preview_rows}
            title="原始数据预览"
            note="原始抽样"
          />
          <DataPreview
            rows={record?.result?.processed_preview_rows}
            title="预处理后预览"
            note="缺失填补 + 字段清理"
          />
        </div>
        <ExportPanel taskId={record?.spec.id} />
      </section>
      <section className="space-y-4">
        <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">分析结论</h3>
        <div className="grid gap-4 md:grid-cols-2">
          {(record?.result?.findings ?? []).map((finding) => (
            <FindingCard key={finding.conclusion} finding={finding} />
          ))}
        </div>
        {record?.result?.narrative && (
          <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-sm text-[color:var(--muted)]">
            {record.result.narrative}
          </div>
        )}
      </section>
    </div>
  );
}
