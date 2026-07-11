import { FormEvent, useState } from "react";
import { FileEntry } from "../api/files";
import { SearchResult, searchDocuments } from "../api/search";

interface SearchBarProps {
  token: string;
  onSelect: (file: FileEntry) => void;
}

function toFileEntry(result: SearchResult): FileEntry {
  const name = result.pdf_path.split("/").pop() ?? result.pdf_path;
  return {
    name,
    source: "generated",
    path: result.pdf_path,
    updated_at: new Date().toISOString(),
  };
}

export default function SearchBar({ token, onSelect }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setError(null);
      return;
    }
    searchDocuments(token, trimmed)
      .then((res) => {
        setResults(res);
        setError(null);
      })
      .catch((err) => {
        setResults([]);
        setError(err instanceof Error ? err.message : "検索に失敗しました");
      });
  }

  return (
    <div className="border-b border-slate-200 p-3">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="氏名・部屋番号などで検索"
          className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          className="shrink-0 rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          検索
        </button>
      </form>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {results.length > 0 && (
        <ul className="mt-2 divide-y divide-slate-100 rounded-md border border-slate-200 bg-white">
          {results.map((result) => (
            <li key={result.doc_id}>
              <button
                type="button"
                onClick={() => onSelect(toFileEntry(result))}
                className="flex w-full flex-col gap-1 px-3 py-2 text-left hover:bg-slate-50"
              >
                <span className="text-sm font-medium text-slate-900">{result.doc_type}</span>
                <span className="text-xs text-slate-500">{result.snippet}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
