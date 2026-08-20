export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") {
      return data.detail;
    }
  } catch {
    // 응답 본문이 JSON이 아닌 경우 기본 메시지 사용
  }
  return fallback;
}


export async function login(loginId: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ username: loginId, password }),
  });

  if (!res.ok) {
    const detail = await parseErrorDetail(
      res,
      "로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    );
    throw new ApiError(res.status, detail);
  }

  return res.json();
}


export type SignupPayload = {
  login_id: string;
  password: string;
  username: string;
  email: string;
  language: string;
};

export async function signup(payload: SignupPayload) {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const detail = await parseErrorDetail(
      res,
      "회원가입 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    );
    throw new ApiError(res.status, detail);
  }

  return res.json();
}


export async function fetchCurrentUser(token: string) {
  const res = await fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const detail = await parseErrorDetail(res, "사용자 정보를 불러오지 못했습니다.");
    throw new ApiError(res.status, detail);
  }

  return res.json();
}


export async function logout(token: string) {
  const res = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const detail = await parseErrorDetail(res, "로그아웃 중 오류가 발생했습니다.");
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

// ---------- Access token 저장 (localStorage) ----------

const ACCESS_TOKEN_KEY = "prequel_access_token";

export function saveAccessToken(token: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearAccessToken() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  }
}