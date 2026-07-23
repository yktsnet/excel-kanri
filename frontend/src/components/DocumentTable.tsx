import { useEffect, useMemo, useState } from "react";
import { cn } from "../lib/utils";
import { FileEntry } from "../api/files";
import { DocumentRecord, DocumentType, fetchDocumentTypes, fetchDocuments } from "../api/documents";

interface DocumentTableProps {
  token: string;
  onSelect: (file: FileEntry) => void;
  refreshSignal?: number;
}

function toFileEntry(doc: DocumentRecord): FileEntry {
  const name = doc.pdf_path.split("/").pop() ?? doc.pdf_path;
  return {
    name,
    source: "generated",
    path: doc.pdf_path,
    updated_at: doc.created_at,
  };
}

export default function DocumentTable({ token, onSelect, refreshSignal }: DocumentTableProps) {
  const [types, setTypes] = useState<DocumentType[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchDocumentTypes(token), fetchDocuments(token)])
      .then(([fetchedTypes, fetchedDocuments]) => {
        setTypes(fetchedTypes);
        setDocuments(fetchedDocuments);
        setError(null);
        setSelectedType((current) => current ?? fetchedTypes[0]?.doc_type ?? null);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "書類一覧の取得に失敗しました"));
  }, [token, refreshSignal]);

  const currentType = useMemo(
    () => types.find((type) => type.doc_type === selectedType) ?? null,
    [types, selectedType]
  );

  const rows = useMemo(
    () => documents.filter((doc) => doc.doc_type === selectedType),
    [documents, selectedType]
  );

  return (
    <div className="flex h-full min-h-0 flex-col rounded-lg border border-slate-200 bg-white">
      <div className="flex flex-wrap gap-2 border-b border-slate-200 p-3">
        {types.map((type) => (
          <button
            key={type.doc_type}
            type="button"
            onClick={() => setSelectedType(type.doc_type)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium",
              selectedType === type.doc_type
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            )}
          >
            {type.doc_type}
          </button>
        ))}
      </div>

      <div className="min-h-0 flex-1 overflow-auto">
        {error && <p className="p-4 text-sm text-red-600">{error}</p>}
        {!error && types.length === 0 && (
          <p className="p-4 text-sm text-slate-500">書類種別がありません</p>
        )}
        {!error && types.length > 0 && rows.length === 0 && (
          <p className="p-4 text-sm text-slate-500">書類がありません</p>
        )}
        {!error && currentType && rows.length > 0 && (
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 bg-slate-50 text-xs font-medium uppercase text-slate-500">
              <tr>
                {currentType.fields.map((field) => (
                  <th key={field} className="whitespace-nowrap px-4 py-2">
                    {field}
                  </th>
                ))}
                <th className="whitespace-nowrap px-4 py-2">作成日時</th>
                <th className="whitespace-nowrap px-4 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((doc) => (
                <tr
                  key={doc.id}
                  onClick={() => onSelect(toFileEntry(doc))}
                  className="cursor-pointer hover:bg-slate-50"
                >
                  {currentType.fields.map((field) => (
                    <td key={field} className="whitespace-nowrap px-4 py-2 text-slate-900">
                      {doc.fields[field] ?? ""}
                    </td>
                  ))}
                  <td className="whitespace-nowrap px-4 py-2 text-slate-500">
                    {new Date(doc.created_at).toLocaleString("ja-JP")}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2 text-right">
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        onSelect(toFileEntry(doc));
                      }}
                      className="rounded-md border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
                    >
                      PDFを見る
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
