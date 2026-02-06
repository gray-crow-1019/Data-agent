import { HTMLAttributes } from "react";

export default function Badge({ className = "", ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={`inline-flex items-center rounded-full border border-[color:var(--border)] px-3 py-1 text-xs uppercase tracking-wide text-[color:var(--muted)] ${className}`}
      {...props}
    />
  );
}
