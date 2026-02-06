export default function DataPreview({
  rows,
  title = "数据预览",
  note = "仅聚合结果",
}: {
  rows?: Array<Record<string, unknown>>;
  title?: string;
  note?: string;
}) {
  const preview = rows && rows.length ? rows : [];
  const headers = preview.length ? Object.keys(preview[0]) : ["segment", "metric", "value"];
  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">{title}</h3>
        <span className="text-xs text-[color:var(--muted)]">{note}</span>
      </div>
      <div className="mt-3 overflow-auto">
        <table className="w-full text-left text-xs">
          <thead className="text-[color:var(--muted)]">
            <tr>
              {headers.map((header) => (
                <th key={header} className="py-2">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.length ? (
              preview.map((row, index) => (
                <tr key={index} className="border-t border-[color:var(--border)]">
                  {headers.map((header) => (
                    <td key={header} className="py-2">
                      {String(row[header] ?? "")}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td className="py-3 text-xs text-[color:var(--muted)]" colSpan={headers.length}>
                  暂无可预览的数据。
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-3 text-[10px] uppercase tracking-[0.2em] text-[color:var(--muted)]">
        细粒度数据已被策略隐藏
      </div>
    </div>
  );
}
