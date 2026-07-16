import { useRef } from "react";
import { FileEntry, pdfUrl } from "../api/files";

interface PdfPreviewProps {
  file: FileEntry | null;
  token: string;
}

export default function PdfPreview({ file, token }: PdfPreviewProps) {
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
      <div className="flex items-center justify-between">
        <p className="truncate text-sm font-medium text-slate-900">{file.name}</p>
        <button
          type="button"
          onClick={handlePrint}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
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
