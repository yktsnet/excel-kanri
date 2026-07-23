import { useRef } from "react";
import { FileEntry, pdfUrl } from "../api/files";

interface PdfPreviewProps {
  file: FileEntry | null;
  token: string;
  onBack?: () => void;
}

export default function PdfPreview({ file, token, onBack }: PdfPreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  function handlePrint() {
    iframeRef.current?.contentWindow?.print();
  }

  if (!file) {
    return (
      <div className="flex h-full min-h-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-sm text-slate-500">
        ファイルを選択してください
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col gap-2">
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="shrink-0 rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              ← 一覧に戻る
            </button>
          )}
          <p className="truncate text-sm font-medium text-slate-900">{file.name}</p>
        </div>
        <button
          type="button"
          onClick={handlePrint}
          className="shrink-0 rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          印刷
        </button>
      </div>
      <iframe
        key={file.path}
        ref={iframeRef}
        src={pdfUrl(file.path, token)}
        title={file.name}
        className="w-full flex-1 rounded-lg border border-slate-200 bg-white"
      />
    </div>
  );
}
