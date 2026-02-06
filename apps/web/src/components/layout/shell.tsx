import { ReactNode } from "react";
import { PageKey } from "../../app";
import ThemeToggle from "./theme-toggle";
import Toast from "../ui/toast";

export default function Shell({
  activePage,
  pages,
  onNavigate,
  children,
}: {
  activePage: PageKey;
  pages: Record<PageKey, { label: string; component: JSX.Element }>;
  onNavigate: (page: PageKey) => void;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen p-6 md:p-10">
      <div className="glass mx-auto flex min-h-[85vh] max-w-7xl flex-col overflow-hidden rounded-[32px] shadow-xl">
        <header className="flex items-center justify-between border-b border-[color:var(--border)] px-8 py-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[color:var(--muted)]">
              数据分析 Agent
            </p>
            <h1 className="font-serif text-3xl">洞察工作台</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-[color:var(--border)] px-4 py-2 text-xs text-[color:var(--muted)] md:flex">
              <span className="h-2 w-2 rounded-full bg-[color:var(--accent)]"></span>
              在线环境
            </div>
            <ThemeToggle />
          </div>
        </header>
        <div className="grid flex-1 grid-cols-1 gap-6 px-6 py-6 md:grid-cols-[220px_1fr] md:px-8">
          <aside className="flex flex-row gap-3 md:flex-col">
            {Object.entries(pages).map(([key, page]) => (
              <button
                key={key}
                onClick={() => onNavigate(key as PageKey)}
                className={`rounded-2xl border border-transparent px-4 py-3 text-left text-sm transition md:text-base ${
                  activePage === key
                    ? "border-[color:var(--border)] bg-white/70"
                    : "text-[color:var(--muted)] hover:bg-white/50"
                }`}
              >
                <div className="font-medium">{page.label}</div>
                <div className="mt-1 text-xs text-[color:var(--muted)]">
                  {key === "home" && "提问 · 探索 · 迭代"}
                  {key === "task" && "产物 · 证据"}
                  {key === "meta" && "指标 · 维度"}
                </div>
              </button>
            ))}
          </aside>
          <main className="reveal min-w-0 rounded-3xl bg-white/60 p-6 shadow-inner">
            {children}
          </main>
        </div>
      </div>
      <div className="pointer-events-none fixed bottom-6 right-6">
        <Toast message="数据访问受策略控制，仅展示聚合结果。" />
      </div>
    </div>
  );
}
