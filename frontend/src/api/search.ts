export interface SearchResult {
  doc_id: number;
  doc_type: string;
  snippet: string;
  pdf_path: string;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `リクエストに失敗しました (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function searchDocuments(token: string, q: string): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q });
  return fetch(`/api/search?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then((res) => parseOrThrow<SearchResult[]>(res));
}
