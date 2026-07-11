export interface DocumentType {
  doc_type: string;
  fields: string[];
}

export interface GenerateResult {
  id: number;
  doc_type: string;
  xlsx_path: string;
  pdf_path: string | null;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `リクエストに失敗しました (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function fetchDocumentTypes(token: string): Promise<DocumentType[]> {
  return fetch("/api/documents/types", {
    headers: { Authorization: `Bearer ${token}` },
  }).then((res) => parseOrThrow<DocumentType[]>(res));
}

export function generateDocument(
  token: string,
  docType: string,
  fields: Record<string, string>
): Promise<GenerateResult> {
  return fetch("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ doc_type: docType, fields }),
  }).then((res) => parseOrThrow<GenerateResult>(res));
}
