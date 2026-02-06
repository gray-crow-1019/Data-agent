import { ClarifyParams, TaskResponse, TaskResult } from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL || "";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("auth_token");
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function postChat(question: string, clarify?: ClarifyParams): Promise<TaskResult> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ question, clarify }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  const data = await res.json();
  return data.result as TaskResult;
}

export async function getTask(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${BASE}/tasks/${taskId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Task request failed");
  return (await res.json()) as TaskResponse;
}

export async function listTasks(limit = 20): Promise<TaskResponse[]> {
  const res = await fetch(`${BASE}/tasks?limit=${limit}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Task list failed");
  return (await res.json()) as TaskResponse[];
}

export async function rerunTask(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${BASE}/tasks/${taskId}/rerun`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Task rerun failed");
  return (await res.json()) as TaskResponse;
}

export async function getArtifact(taskId: string, kind: string): Promise<{ payload: string }> {
  const res = await fetch(`${BASE}/tasks/${taskId}/artifacts/${kind}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Artifact fetch failed");
  return (await res.json()) as { payload: string };
}

export async function deleteTask(taskId: string) {
  const res = await fetch(`${BASE}/tasks/${taskId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Task delete failed");
  return (await res.json()) as { status: string };
}

export async function downloadStepOutput(taskId: string, stepName: string) {
  const res = await fetch(`${BASE}/tasks/${taskId}/steps/${stepName}/download`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Step output fetch failed");
  return (await res.json()) as { payload: Record<string, unknown> };
}

export async function getCatalog(): Promise<{ metrics: unknown[]; dimensions: unknown[] }> {
  const res = await fetch(`${BASE}/catalog`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Catalog request failed");
  return (await res.json()) as { metrics: unknown[]; dimensions: unknown[] };
}

export async function uploadDataset(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/datasets/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!res.ok) throw new Error("Dataset upload failed");
  return (await res.json()) as {
    id: string;
    filename: string;
    table: string;
    columns: string[];
    row_count: number;
    created_at: string;
  };
}

export async function listDatasets() {
  const res = await fetch(`${BASE}/datasets`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Dataset list failed");
  return (await res.json()) as Array<{
    id: string;
    filename: string;
    table: string;
    columns: string[];
    row_count: number;
    created_at: string;
  }>;
}

export async function generateChart(table: string, plan: Record<string, unknown>) {
  const res = await fetch(`${BASE}/datasets/chart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ table, plan: [plan] }),
  });
  if (!res.ok) throw new Error("Chart generation failed");
  return (await res.json()) as { charts: Record<string, unknown>[] };
}

export async function downloadDataset(datasetId: string) {
  const res = await fetch(`${BASE}/datasets/${datasetId}/download`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Dataset download failed");
  return (await res.json()) as { payload: string };
}

export async function saveChart(taskId: string, chart: Record<string, unknown>) {
  const res = await fetch(`${BASE}/tasks/${taskId}/charts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ chart }),
  });
  if (!res.ok) throw new Error("Chart save failed");
  return (await res.json()) as { status: string; charts: Record<string, unknown>[] };
}
