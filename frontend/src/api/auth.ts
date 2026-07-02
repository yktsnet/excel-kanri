export type Role = "viewer" | "editor";

export interface AuthConfig {
  demo_mode: boolean;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: number;
  email: string;
  role: Role;
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `リクエストに失敗しました (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function fetchAuthConfig(): Promise<AuthConfig> {
  return fetch("/api/auth/config").then((res) => parseOrThrow<AuthConfig>(res));
}

export function login(email: string, password: string): Promise<LoginResult> {
  return fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }).then((res) => parseOrThrow<LoginResult>(res));
}

export function fetchCurrentUser(token: string): Promise<CurrentUser> {
  return fetch("/api/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  }).then((res) => parseOrThrow<CurrentUser>(res));
}
