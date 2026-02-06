import { useState } from "react";
import Shell from "./components/layout/shell";
import Home from "./pages/home";
import MetaBrowser from "./pages/meta-browser";
import TaskDetail from "./pages/task-detail";

export type PageKey = "home" | "task" | "meta";

const pageMap: Record<PageKey, { label: string; component: JSX.Element }> = {
  home: { label: "工作台", component: <Home /> },
  task: { label: "任务回放", component: <TaskDetail /> },
  meta: { label: "元数据", component: <MetaBrowser /> },
};

export default function App() {
  const [page, setPage] = useState<PageKey>("home");

  return (
    <Shell
      activePage={page}
      pages={pageMap}
      onNavigate={(next) => setPage(next)}
    >
      {pageMap[page].component}
    </Shell>
  );
}
