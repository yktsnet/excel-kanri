import { useEffect, useState } from "react";
import LoginForm from "./components/LoginForm";
import { CurrentUser, fetchCurrentUser } from "./api/auth";

const TOKEN_STORAGE_KEY = "excel-kanri.token";

export default function App() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY)
  );
  const [user, setUser] = useState<CurrentUser | null>(null);

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

  if (!token || !user) {
    return <LoginForm onLoggedIn={handleLoggedIn} />;
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
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
    </div>
  );
}
