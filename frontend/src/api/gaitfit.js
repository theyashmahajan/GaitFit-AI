export const API_BASE = "http://localhost:8000";

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/upload-video`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function fetchStatus(jobId) {
  const res = await fetch(`${API_BASE}/status/${jobId}`);
  if (!res.ok) {
    throw new Error("Failed to fetch status");
  }
  return res.json();
}

export async function fetchResults(jobId) {
  const res = await fetch(`${API_BASE}/results/${jobId}`);
  if (!res.ok) {
    throw new Error("Failed to fetch results");
  }
  return res.json();
}
