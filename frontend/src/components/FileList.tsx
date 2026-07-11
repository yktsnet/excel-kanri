import { useEffect, useState } from "react";
import { cn } from "../lib/utils";
import { FileEntry, fetchFiles } from "../api/files";

interface FileListProps {
  token: string;
  selectedPath: string | null;
  onSelect: (file: FileEntry) => void;
  refreshSignal?: number;
}

const SOURCE_LABEL: Record<FileEntry["source"], string> = {
  generated: "生成",
  shared: "共有",
};

const SOURCE_BADGE_CLASS: Record<FileEntry["source"], string> = {
  generated: "bg-emerald-100 text-emerald-800",
  shared: "bg-amber-100 text-amber-800",
};

export default function FileList({ token, selectedPath, onSelect, refreshSignal }: FileListProps) {
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFiles(token)
      .then(setFiles)
      .catch((err) => setError(err instanceof Error ? err.message : "一覧の取得に失敗しました"));
  }, [token, refreshSignal]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg border border-slate-200 bg-white">
      {/* SearchBar (Issue 03) をここに載せる */}
      <div className="flex-1 overflow-y-auto">
        {error && <p className="p-4 text-sm text-red-600">{error}</p>}
        {!error && files.length === 0 && (
          <p className="p-4 text-sm text-slate-500">ファイルがありません</p>
        )}
        <ul className="divide-y divide-slate-100">
          {files.map((file) => (
            <li key={file.path}>
              <button
                type="button"
                onClick={() => onSelect(file)}
                className={cn(
                  "flex w-full flex-col gap-1 px-4 py-3 text-left hover:bg-slate-50",
                  selectedPath === file.path && "bg-slate-100"
                )}
              >
                <span className="flex items-center gap-2">
                  <span
                    className={cn(
                      "shrink-0 rounded px-1.5 py-0.5 text-xs font-medium",
                      SOURCE_BADGE_CLASS[file.source]
                    )}
                  >
                    {SOURCE_LABEL[file.source]}
                  </span>
                  <span className="truncate text-sm font-medium text-slate-900">{file.name}</span>
                </span>
                <span className="text-xs text-slate-500">
                  {new Date(file.updated_at).toLocaleString("ja-JP")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
