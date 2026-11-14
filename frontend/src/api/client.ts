export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
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

// 공통 API 요청 함수
async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) {
    if (res.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("auth:unauthorized"));
    }

    throw new Error(await extractErrorMessage(res));
  }

  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

// GET
export async function apiGet<T>(
  path: string
): Promise<T> {
  return request<T>(path, {
    method: "GET",
  });
}

// POST - JSON
export async function apiPostJson<T>(
  path: string,
  body: unknown
): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

// POST - Form
export async function apiPostForm<T>(
  path: string,
  form: Record<string, string>
): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams(form),
  });
}

// POST - Empty
export async function apiPostEmpty<T>(
  path: string
): Promise<T> {
  return request<T>(path, {
    method: "POST",
  });
}

// DELETE
export async function apiDelete<T = void>(
  path: string
): Promise<T> {
  return request<T>(path, {
    method: "DELETE",
  });
}