import { FormEvent, useEffect, useState } from "react";
import { cn } from "../lib/utils";
import { fetchAuthConfig, login, Role } from "../api/auth";

const DEMO_CREDENTIALS: Record<Role, { email: string; password: string }> = {
  viewer: { email: "viewer@example.com", password: "demo-viewer" },
  editor: { email: "editor@example.com", password: "demo-editor" },
};

interface LoginFormProps {
  onLoggedIn: (token: string) => void;
}

export default function LoginForm({ onLoggedIn }: LoginFormProps) {
  const [demoMode, setDemoMode] = useState(false);
  const [demoRole, setDemoRole] = useState<Role>("viewer");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAuthConfig()
      .then((config) => setDemoMode(config.demo_mode))
      .catch(() => setDemoMode(false));
  }, []);

  useEffect(() => {
    if (!demoMode) return;
    const creds = DEMO_CREDENTIALS[demoRole];
    setEmail(creds.email);
    setPassword(creds.password);
  }, [demoMode, demoRole]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const result = await login(email, password);
      onLoggedIn(result.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-xl font-semibold text-slate-900">ログイン</h1>

        {demoMode && (
          <div className="mb-6 flex rounded-md border border-slate-200 p-1">
            {(["viewer", "editor"] as Role[]).map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => setDemoRole(role)}
                className={cn(
                  "flex-1 rounded px-3 py-1.5 text-sm font-medium transition-colors",
                  demoRole === role
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                )}
              >
                {role === "viewer" ? "閲覧者" : "編集者"}
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              メールアドレス
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              パスワード
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {submitting ? "ログイン中..." : "ログイン"}
          </button>
        </form>
      </div>
    </div>
  );
}
