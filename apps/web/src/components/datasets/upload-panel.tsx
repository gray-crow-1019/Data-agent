import { useEffect, useState } from "react";
import { downloadDataset, listDatasets, uploadDataset } from "../../lib/api";
import Button from "../ui/button";

export default function UploadPanel() {
  const [datasets, setDatasets] = useState<Array<any>>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const data = await listDatasets();
    setDatasets(data);
  };

  useEffect(() => {
    load().catch(() => {
      setDatasets([]);
    });
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      await uploadDataset(file);
      setFile(null);
      await load();
    } catch (err) {
      setError("上传失败，请检查文件格式或后端状态。");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (datasetId: string, filename: string) => {
    try {
      const res = await downloadDataset(datasetId);
      const blob = new Blob([res.payload], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("下载失败，请检查后端状态。");
    }
  };

  return (
    <div className="rounded-3xl border border-[color:var(--border)] bg-white/70 p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="font-serif text-xl">数据集上传</h3>
          <p className="text-sm text-[color:var(--muted)]">
            上传 CSV 后将自动载入数据库，可用表名进行分析。
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.mat"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <Button onClick={handleUpload} disabled={!file || loading}>
            {loading ? "上传中..." : "上传 CSV"}
          </Button>
        </div>
      </div>
      {error && <div className="mt-3 text-xs text-rose-600">{error}</div>}
      <div className="mt-4 space-y-3">
        {datasets.length === 0 ? (
          <div className="text-xs text-[color:var(--muted)]">尚未上传数据集。</div>
        ) : (
          datasets.map((ds) => (
            <div
              key={ds.id}
              className="rounded-2xl border border-[color:var(--border)] bg-white/70 px-4 py-3"
            >
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium">{ds.filename}</div>
                <div className="flex items-center gap-3 text-xs text-[color:var(--muted)]">
                  <span>{ds.row_count} 行</span>
                  <Button variant="ghost" onClick={() => handleDownload(ds.id, ds.filename)}>
                    下载
                  </Button>
                </div>
              </div>
              <div className="mt-2 text-xs text-[color:var(--muted)]">表名：{ds.table}</div>
              <div className="mt-1 text-xs text-[color:var(--muted)]">
                字段：{ds.columns.join(", ")}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
