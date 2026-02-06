const TEMPLATES = [
  { title: "波动解释", desc: "拆解波动来源与贡献度" },
  { title: "漏斗分析", desc: "关键步骤转化与流失" },
  { title: "留存分析", desc: "分 cohort 留存走势" },
  { title: "A/B 测试", desc: "实验效果与显著性" },
  { title: "自动报表", desc: "定期指标快照" },
];

export default function TemplateGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {TEMPLATES.map((item) => (
        <div key={item.title} className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
          <div className="text-sm font-medium">{item.title}</div>
          <p className="mt-2 text-xs text-[color:var(--muted)]">{item.desc}</p>
        </div>
      ))}
    </div>
  );
}
