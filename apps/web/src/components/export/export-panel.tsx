import Button from "../ui/button";
import { getArtifact } from "../../lib/api";

export default function ExportPanel({ taskId }: { taskId?: string }) {
  const handleDownload = async (kind: string, filename: string) => {
    if (!taskId) return;
    const res = await getArtifact(taskId, kind);
    const blob = new Blob([res.payload], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-[color:var(--border)] bg-white/70 p-4">
      <h3 className="text-sm font-medium">导出与分享</h3>
      <p className="mt-2 text-xs text-[color:var(--muted)]">
        导出受策略控制（PII、小样本、权限）。
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={() => handleDownload("report_md", "report.md")} disabled={!taskId}>
          导出 Markdown
        </Button>
        <Button disabled>导出 PDF</Button>
        <Button onClick={() => handleDownload("dataset_csv", "dataset.csv")} disabled={!taskId}>
          导出 CSV
        </Button>
        <Button onClick={() => handleDownload("processed_csv", "dataset_processed.csv")} disabled={!taskId}>
          导出预处理 CSV
        </Button>
        <Button onClick={() => handleDownload("processed_full_csv", "dataset_processed_full.csv")} disabled={!taskId}>
          导出预处理完整 CSV
        </Button>
        <Button onClick={() => handleDownload("charts_json", "charts.json")} disabled={!taskId}>
          导出图表 JSON
        </Button>
        <Button variant="ghost">复制 SQL</Button>
      </div>
    </div>
  );
}
