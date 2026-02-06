import { TaskSpec } from "../../lib/types";
import Button from "../ui/button";

export default function TaskList({
  tasks,
  onDelete,
}: {
  tasks: TaskSpec[];
  onDelete?: (taskId: string) => void;
}) {
  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3"
        >
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium">{task.question}</div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-[color:var(--muted)]">{task.status}</span>
              {onDelete && (
                <Button
                  variant="ghost"
                  onClick={() => onDelete(task.id)}
                  className="shrink-0 whitespace-nowrap px-3"
                >
                  删除
                </Button>
              )}
            </div>
          </div>
          <div className="mt-2 text-xs text-[color:var(--muted)]">{task.created_at}</div>
          {task.labels?.length ? (
            <div className="mt-2 flex flex-wrap gap-2">
              {task.labels.map((label) => (
                <span
                  key={label}
                  className="rounded-full border border-[color:var(--border)] px-2 py-1 text-[10px] uppercase tracking-widest text-[color:var(--muted)]"
                >
                  {label}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
