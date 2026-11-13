export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

const TOKEN_STORAGE_KEY = "prequel_access_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

async function extractErrorMessage(res: Response): Promise<string> {
  try {
    const json = await res.json();
    const detail = json?.detail;

    if (typeof detail === "string") return detail;

    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d) => d.msg).join(" / ");
    }

    return `요청에 실패했습니다. (${res.status})`;
  } catch {
    return `요청에 실패했습니다. (${res.status})`;
  }
}

interface RequestOptions {
  auth?: boolean;
}

export async function apiGet<T>(path: string, options?: RequestOptions): Promise<T> {
  const headers: Record<string, string> = {};
  if (options?.auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${getApiBaseUrl()}${path}`, { method: "GET", headers });
  if (!res.ok) throw new Error(await extractErrorMessage(res));
  return res.json();
}

export async function apiPostJson<T>(
  path: string,
  body: unknown,
  options?: RequestOptions
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options?.auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await extractErrorMessage(res));


  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export async function apiPostForm<T>(path: string, form: Record<string, string>): Promise<T> {
  const body = new URLSearchParams(form);

  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error(await extractErrorMessage(res));
  return res.json();
}

export async function apiPostEmpty<T>(path: string, options?: RequestOptions): Promise<T> {
  const headers: Record<string, string> = {};
  if (options?.auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${getApiBaseUrl()}${path}`, { method: "POST", headers });
  if (!res.ok) throw new Error(await extractErrorMessage(res));
  return res.json();
}

export async function apiDelete<T = void>(path: string, options?: RequestOptions): Promise<T> {
  const headers: Record<string, string> = {};
  if (options?.auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${getApiBaseUrl()}${path}`, { method: "DELETE", headers });
  if (!res.ok) throw new Error(await extractErrorMessage(res));


  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}