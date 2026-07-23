import { useEffect, useState } from "react";
import LoginForm from "./components/LoginForm";
import GenerateModal from "./components/GenerateModal";
import FileList from "./components/FileList";
import PdfPreview from "./components/PdfPreview";
import SearchBar from "./components/SearchBar";
import DocumentTable from "./components/DocumentTable";
import { CurrentUser, fetchCurrentUser } from "./api/auth";
import { FileEntry } from "./api/files";
import { GenerateResult } from "./api/documents";

const TOKEN_STORAGE_KEY = "excel-kanri.token";

export default function App() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY)
  );
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileEntry | null>(null);
  const [isGenerateModalOpen, setGenerateModalOpen] = useState(false);
  const [refreshSignal, setRefreshSignal] = useState(0);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    fetchCurrentUser(token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
      });
  }, [token]);

  function handleLoggedIn(newToken: string) {
    localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
  }

  function handleGenerated(result: GenerateResult) {
    setGenerateModalOpen(false);
    setRefreshSignal((n) => n + 1);
    if (result.pdf_path) {
      const path = result.pdf_path;
      const name = path.split("/").pop() ?? path;
      setSelectedFile({
        name,
        source: "generated",
        path,
        updated_at: new Date().toISOString(),
      });
    }
  }

  if (!token || !user) {
    return <LoginForm onLoggedIn={handleLoggedIn} />;
  }

  return (
    <div className="flex h-screen flex-col bg-slate-50 p-4 md:p-8">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600">
          {user.email}（{user.role === "editor" ? "編集者" : "閲覧者"}）としてログイン中
        </p>
        <button
          onClick={handleLogout}
          className="text-sm font-medium text-slate-600 underline hover:text-slate-900"
        >
          ログアウト
        </button>
      </div>

      <div className="mt-8 grid min-h-0 flex-1 grid-cols-1 grid-rows-[minmax(0,1fr)_minmax(0,1fr)] gap-6 md:grid-cols-[320px_1fr] md:grid-rows-1">
        <div className="flex min-h-0 flex-col gap-3">
          {user.role === "editor" && (
            <button
              type="button"
              onClick={() => setGenerateModalOpen(true)}
              className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800"
            >
              新規作成
            </button>
          )}
          <SearchBar token={token} onSelect={setSelectedFile} />
          <div className="min-h-0 flex-1">
            <FileList
              token={token}
              selectedPath={selectedFile?.path ?? null}
              onSelect={setSelectedFile}
              refreshSignal={refreshSignal}
            />
          </div>
        </div>
        <div className="min-h-0">
          {selectedFile === null ? (
            <DocumentTable token={token} onSelect={setSelectedFile} refreshSignal={refreshSignal} />
          ) : (
            <PdfPreview file={selectedFile} token={token} onBack={() => setSelectedFile(null)} />
          )}
        </div>
      </div>

      {isGenerateModalOpen && user.role === "editor" && (
        <GenerateModal
          token={token}
          onClose={() => setGenerateModalOpen(false)}
          onGenerated={handleGenerated}
        />
      )}
    </div>
  );
}
