export type FileSource = "generated" | "shared";

export interface FileEntry {
  name: string;
  source: FileSource;
  path: string;
  updated_at: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `リクエストに失敗しました (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function fetchFiles(token: string): Promise<FileEntry[]> {
  return fetch("/api/files", {
    headers: { Authorization: `Bearer ${token}` },
  }).then((res) => parseOrThrow<FileEntry[]>(res));
}

// iframe の src に渡す URL。Authorization ヘッダを付与できないため ?token= クエリで認証する。
export function pdfUrl(path: string, token: string): string {
  return `/api/pdf/${encodeURI(path)}?token=${encodeURIComponent(token)}`;
}
