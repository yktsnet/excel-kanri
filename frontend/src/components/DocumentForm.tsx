import { FormEvent, useEffect, useState } from "react";
import { DocumentType, fetchDocumentTypes, generateDocument } from "../api/documents";

interface DocumentFormProps {
  token: string;
}

export default function DocumentForm({ token }: DocumentFormProps) {
  const [types, setTypes] = useState<DocumentType[]>([]);
  const [docType, setDocType] = useState("");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocumentTypes(token)
      .then((result) => {
        setTypes(result);
        if (result.length > 0) {
          setDocType(result[0].doc_type);
        }
      })
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : "書類種別の取得に失敗しました")
      );
  }, [token]);

  const selected = types.find((t) => t.doc_type === docType);

  useEffect(() => {
    setFields({});
  }, [docType]);

  function handleFieldChange(name: string, value: string) {
    setFields((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError(null);
    setSuccessMessage(null);
    setSubmitting(true);
    try {
      const payload = Object.fromEntries(
        selected.fields.map((name) => [name, fields[name] ?? ""])
      );
      const result = await generateDocument(token, docType, payload);
      setSuccessMessage(`生成しました: ${result.pdf_path ?? result.xlsx_path}`);
      setFields({});
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成に失敗しました");
    } finally {
      setSubmitting(false);
    }
  }

  if (loadError) {
    return <p className="text-sm text-red-600">{loadError}</p>;
  }

  return (
    <div className="w-full max-w-lg rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="mb-6 text-xl font-semibold text-slate-900">書類生成</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">書類種別</label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          >
            {types.map((t) => (
              <option key={t.doc_type} value={t.doc_type}>
                {t.doc_type}
              </option>
            ))}
          </select>
        </div>

        {selected?.fields.map((name) => (
          <div key={name}>
            <label className="mb-1 block text-sm font-medium text-slate-700">{name}</label>
            <input
              type="text"
              required
              value={fields[name] ?? ""}
              onChange={(e) => handleFieldChange(name, e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
          </div>
        ))}

        {error && <p className="text-sm text-red-600">{error}</p>}
        {successMessage && <p className="text-sm text-green-600">{successMessage}</p>}

        <button
          type="submit"
          disabled={submitting || !selected}
          className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {submitting ? "生成中..." : "生成"}
        </button>
      </form>
    </div>
  );
}
