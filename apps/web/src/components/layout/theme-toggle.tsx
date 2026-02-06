import { useEffect, useState } from "react";

const THEMES = ["dawn", "dusk"] as const;

export default function ThemeToggle() {
  const [theme, setTheme] = useState<(typeof THEMES)[number]>("dawn");

  useEffect(() => {
    if (theme === "dawn") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", "dusk");
    }
  }, [theme]);

  return (
    <button
      onClick={() => setTheme(theme === "dawn" ? "dusk" : "dawn")}
      className="rounded-full border border-[color:var(--border)] px-4 py-2 text-xs uppercase tracking-widest text-[color:var(--muted)]"
    >
      {theme === "dawn" ? "夜间" : "白天"}
    </button>
  );
}
