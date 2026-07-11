import { MouseEvent } from "react";
import DocumentForm from "./DocumentForm";
import { GenerateResult } from "../api/documents";

interface GenerateModalProps {
  token: string;
  onClose: () => void;
  onGenerated: (result: GenerateResult) => void;
}

export default function GenerateModal({ token, onClose, onGenerated }: GenerateModalProps) {
  function handleOverlayClick(e: MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="relative max-h-full w-full max-w-lg overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          aria-label="閉じる"
          className="absolute right-3 top-3 text-lg font-medium text-slate-400 hover:text-slate-600"
        >
          ×
        </button>
        <DocumentForm token={token} onGenerated={onGenerated} />
      </div>
    </div>
  );
}
