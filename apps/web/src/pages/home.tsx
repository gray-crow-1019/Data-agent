import { useEffect, useState } from "react";
import ChatPanel, { ChatMessage } from "../components/chat/chat-panel";
import PromptBox from "../components/chat/prompt-box";
import FindingCard from "../components/cards/finding-card";
import QualityCard from "../components/cards/quality-card";
import QueryCard from "../components/cards/query-card";
import ChartView from "../components/charts/chart-view";
import DataPreview from "../components/table/data-preview";
import TaskList from "../components/history/task-list";
import { deleteTask, generateChart, listTasks, postChat, saveChart, uploadDataset } from "../lib/api";
import { TaskResponse, TaskResult } from "../lib/types";

const STEP_LABELS: Record<string, string> = {
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

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "请描述你要分析的问题。我可以澄清时间范围与分组口径。",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TaskResult | null>(null);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | undefined>(undefined);
  const [customChart, setCustomChart] = useState<Record<string, unknown> | null>(null);
  const [customCharts, setCustomCharts] = useState<Record<string, unknown>[]>([]);
  const [chartType, setChartType] = useState("auto");
  const [chartX, setChartX] = useState<string>("");
  const [chartY, setChartY] = useState<string>("");
  const [chartAgg, setChartAgg] = useState("mean");
  const [filterField, setFilterField] = useState<string>("");
  const [filterOp, setFilterOp] = useState<string>("eq");
  const [filterValue, setFilterValue] = useState<string>("");

  useEffect(() => {
    listTasks(10)
      .then((records) => setTasks(records))
      .catch(() => {
        setTasks([]);
      });
  }, []);

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      const records = await listTasks(10);
      setTasks(records);
    } catch {
      // ignore
    }
  };

  const handleRun = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    const nextMessages = [
      ...messages,
      { role: "user" as const, content: question.trim() },
      {
        role: "assistant" as const,
        content: "正在运行分析流程，稍后会给出结果。",
      },
    ];
    setMessages(nextMessages);
    try {
      let tableHint = "";
      if (file) {
        const uploaded = await uploadDataset(file);
        tableHint = `\\n使用表 ${uploaded.table} 进行分析。`;
        setFile(null);
        setFileName(undefined);
      }
      const res = await postChat(`${question.trim()}${tableHint}`);
      setResult(res);
      setCustomCharts([]);
      setCustomChart(null);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.narrative ?? "Analysis completed.",
        },
      ]);
      const records = await listTasks(10);
      setTasks(records);
      setQuestion("");
    } catch (err) {
      setError("请求失败，请检查后端是否启动。");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateChart = async () => {
    if (!result?.dataset_profile) return;
    const table = String((result.dataset_profile as Record<string, unknown>).table || "");
    if (!table || !chartX) return;
    const columnTypes = (result.dataset_profile as Record<string, unknown>)
      .column_types as Record<string, string> | undefined;
    const numericCols = Object.entries(columnTypes ?? {})
      .filter(([, v]) => v === "numeric")
      .map(([k]) => k);
    let effectiveType = chartType;
    let x = chartX;
    let y = chartY || null;
    if (chartType === "auto") {
      const t = columnTypes?.[chartX];
      if (t === "numeric") {
        effectiveType = "hist";
        y = chartX;
        x = chartX;
      } else if (t === "datetime") {
        effectiveType = "line";
        y = chartY || numericCols[0] || null;
      } else {
        effectiveType = "bar";
      }
    }
    const filters =
      filterField && filterValue
        ? [
            {
              field: filterField,
              op: filterOp,
              value: filterValue,
            },
          ]
        : [];
    const plan: Record<string, unknown> = {
      title: "自定义图表",
      type: effectiveType,
      x,
      y,
      agg: chartAgg,
      top_n: 10,
      filters,
    };
    const res = await generateChart(table, plan);
    if (res.charts?.length) {
      const chart = res.charts[0];
      setCustomChart(chart);
      setCustomCharts((prev) => [...prev, chart]);
      if (result?.task_id) {
        try {
          await saveChart(result.task_id, chart);
        } catch {
          // ignore
        }
      }
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 md:grid-cols-[1.35fr_0.65fr]">
        <div>
          <h2 className="font-serif text-2xl">实时分析工作台</h2>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            与分析引擎对话，明确口径并生成结构化结果。
          </p>
          <div className="mt-6 rounded-3xl bg-white/60 p-5">
            <ChatPanel messages={messages} />
            <PromptBox
              value={question}
              onChange={setQuestion}
              onSubmit={handleRun}
              onFileChange={(next) => {
                setFile(next);
                setFileName(next?.name);
              }}
              fileName={fileName}
              disabled={loading}
            />
            {error && (
              <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
                {error}
              </div>
            )}
          </div>
        </div>
        <div className="space-y-4">
          <div className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-5">
            <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">
              Agent 日志
            </h3>
            <div className="mt-4 space-y-3">
              {(result?.steps ?? []).length === 0 ? (
                <div className="text-xs text-[color:var(--muted)]">暂无执行记录。</div>
              ) : (
                result?.steps?.map((step, index) => {
                  const durationValue =
                    step.duration_ms ??
                    (step.started_at && step.ended_at
                      ? new Date(step.ended_at).getTime() - new Date(step.started_at).getTime()
                      : 0);
                  const duration =
                    durationValue <= 0 ? "<1 ms" : `${durationValue} ms`;
                  return (
                    <div
                      key={`${step.name}-${index}`}
                      className="rounded-2xl border border-[color:var(--border)] bg-white/80 px-4 py-3 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{STEP_LABELS[step.name] ?? step.name}</span>
                        <span className="text-[color:var(--muted)]">{step.status}</span>
                      </div>
                      <div className="mt-2 text-[color:var(--muted)]">耗时：{duration}</div>
                    </div>
                  );
                })
              )}
              {result?.artifacts?.llm_trace_messages && (
                <details className="mt-4 rounded-2xl border border-[color:var(--border)] bg-white/80 px-4 py-3 text-xs">
                  <summary className="cursor-pointer text-[color:var(--muted)]">查看 LLM Trace JSON</summary>
                  <pre className="mt-2 whitespace-pre-wrap text-[11px] text-[color:var(--ink)]">
                    {JSON.stringify(result.artifacts.llm_trace_messages, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
          <div className="rounded-3xl border border-[color:var(--border)] bg-amber-50/70 p-4 text-xs text-amber-700">
            成本提示：大查询会触发采样与限流策略。
          </div>
        </div>
      </section>
      {result && (
        <section className="space-y-6">
          {result.warnings?.length ? (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-700">
              {result.warnings.join(" · ")}
            </div>
          ) : null}
          {result.dataset_profile && (
            <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
              <div className="text-sm font-medium text-[color:var(--ink)]">数据概况</div>
              <div className="mt-2 flex flex-wrap gap-4">
                <div>行数：{String(result.dataset_profile.row_count ?? "-")}</div>
                <div>字段数：{String((result.dataset_profile.columns as string[] | undefined)?.length ?? "-")}</div>
              </div>
              {result.analysis_type && (
                <div className="mt-3 text-[color:var(--ink)]">
                  任务类型：{result.analysis_type}（{result.analysis_reason ?? "未提供原因"}）
                </div>
              )}
            </div>
          )}
          {result.dataset_profile && (
            <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
              <div className="text-sm font-medium text-[color:var(--ink)]">图表交互（傻瓜模式）</div>
              <div className="mt-3 flex flex-wrap gap-3">
                <select
                  className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                  value={chartX}
                  onChange={(event) => setChartX(event.target.value)}
                >
                  <option value="">选择字段</option>
                  {(result.dataset_profile.columns as string[] | undefined)?.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
                <select
                  className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                  value={chartType}
                  onChange={(event) => setChartType(event.target.value)}
                >
                  <option value="auto">自动推荐</option>
                  <option value="bar">柱状图</option>
                  <option value="line">折线图</option>
                  <option value="pie">饼图</option>
                  <option value="box">箱线图</option>
                  <option value="hist">直方图</option>
                  <option value="scatter">散点图</option>
                </select>
                <select
                  className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                  value={chartY}
                  onChange={(event) => setChartY(event.target.value)}
                >
                  <option value="">数值字段（时间序列可选）</option>
                  {(result.dataset_profile.columns as string[] | undefined)?.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
                <button
                  className="rounded-full border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                  onClick={handleGenerateChart}
                >
                  生成图表
                </button>
              </div>
              <div className="mt-2 text-xs text-[color:var(--muted)]">
                提示：数值字段默认给直方图/箱线图；类别字段默认柱状图；时间字段默认折线图。
              </div>
              <details className="mt-3 text-xs text-[color:var(--muted)]">
                <summary className="cursor-pointer">高级筛选（可选）</summary>
                <div className="mt-3 flex flex-wrap gap-3">
                  <select
                    className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                    value={filterField}
                    onChange={(event) => setFilterField(event.target.value)}
                  >
                    <option value="">选择筛选字段</option>
                    {(result.dataset_profile.columns as string[] | undefined)?.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                  <select
                    className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                    value={filterOp}
                    onChange={(event) => setFilterOp(event.target.value)}
                  >
                    <option value="eq">等于</option>
                    <option value="neq">不等于</option>
                    <option value="contains">包含</option>
                  </select>
                  <input
                    className="rounded-xl border border-[color:var(--border)] bg-white/70 px-3 py-2 text-xs"
                    placeholder="筛选值"
                    value={filterValue}
                    onChange={(event) => setFilterValue(event.target.value)}
                  />
                </div>
              </details>
              {customChart && (
                <div className="mt-4">
                  <ChartView option={customChart} />
                </div>
              )}
            </div>
          )}
          {result.chart_plan && result.chart_plan.length > 0 && (
            <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
              <div className="text-sm font-medium text-[color:var(--ink)]">图表规划</div>
              <div className="mt-2 space-y-2">
                {result.chart_plan.map((item, index) => (
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
            </div>
          )}
          {result.artifacts?.report_structured && (
            <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-xs text-[color:var(--muted)]">
              <div className="text-sm font-medium text-[color:var(--ink)]">结构化报告</div>
              <div className="mt-2 grid gap-3 md:grid-cols-2">
                <div>
                  <div className="font-medium text-[color:var(--ink)]">方法</div>
                  {((result.artifacts.report_structured as any).methods ?? []).map((item: string, idx: number) => (
                    <div key={`m-${idx}`}>- {item}</div>
                  ))}
                </div>
                <div>
                  <div className="font-medium text-[color:var(--ink)]">假设</div>
                  {((result.artifacts.report_structured as any).assumptions ?? []).map((item: string, idx: number) => (
                    <div key={`a-${idx}`}>- {item}</div>
                  ))}
                </div>
                <div>
                  <div className="font-medium text-[color:var(--ink)]">结论</div>
                  {((result.artifacts.report_structured as any).conclusions ?? []).map((item: string, idx: number) => (
                    <div key={`c-${idx}`}>- {item}</div>
                  ))}
                </div>
                <div>
                  <div className="font-medium text-[color:var(--ink)]">限制</div>
                  {((result.artifacts.report_structured as any).limitations ?? []).map((item: string, idx: number) => (
                    <div key={`l-${idx}`}>- {item}</div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {result.charts && result.charts.length + customCharts.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2">
              {[...result.charts, ...customCharts].map((option, index) => {
                const insight = result.chart_insights?.[index];
                return (
                  <div key={`chart-${index}`} className="space-y-2">
                    <ChartView option={option} />
                    {insight && (
                      <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-3 text-xs text-[color:var(--muted)]">
                        <div className="text-[color:var(--ink)]">{String(insight.insight ?? "")}</div>
                        {insight.caveat && (
                          <div className="mt-2">注意：{String(insight.caveat)}</div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <ChartView option={result.chart} />
          )}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">取数方案</h3>
              {result.queries.map((query) => (
                <QueryCard key={query.title} query={query} />
              ))}
            </div>
            <div className="space-y-4">
              <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">质量闸门</h3>
              {result.quality.map((quality) => (
                <QualityCard key={quality.check} quality={quality} />
              ))}
            </div>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <DataPreview rows={result.raw_preview_rows ?? result.preview_rows} title="原始数据预览" note="原始抽样" />
            <DataPreview
              rows={result.processed_preview_rows ?? []}
              title="预处理后预览"
              note="缺失填补 + 字段清理"
            />
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4 text-sm">
              <h3 className="text-sm font-medium">预处理方案</h3>
              <div className="mt-3 space-y-2 text-xs text-[color:var(--muted)]">
                {(result.preprocessing?.steps as string[] | undefined)?.length ? (
                  (result.preprocessing?.steps as string[]).map((step, index) => (
                    <div key={`prep-${index}`}>- {step}</div>
                  ))
                ) : (
                  <div>暂无预处理建议。</div>
                )}
              </div>
            </div>
            <div className="space-y-4">
              <h3 className="text-sm uppercase tracking-[0.3em] text-[color:var(--muted)]">分析结论</h3>
              <div className="grid gap-4">
                {result.findings.map((finding) => (
                  <FindingCard key={finding.conclusion} finding={finding} />
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
      <section className="grid gap-6 md:grid-cols-1">
        <div className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
          <h3 className="font-serif text-xl">历史任务</h3>
          <p className="mt-2 text-sm text-[color:var(--muted)]">
            回放或复跑最近任务。
          </p>
          <div className="mt-4">
            <TaskList tasks={tasks.map((record) => record.spec)} onDelete={handleDeleteTask} />
          </div>
        </div>
      </section>
    </div>
  );
}
