import type {
  MessageResponse,
  SignupPayload,
} from "@/types/auth";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";


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


// ---------- 인증 관련 API ----------
export async function login(loginId: string, password: string): Promise<MessageResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    credentials: "include", // 쿠키를 포함한 요청을 허용
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

export async function signup(payload: SignupPayload) {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    credentials: "include", // 쿠키를 포함한 요청을 허용
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

// ---------- 회원가입 중복 확인 ----------

export async function checkLoginId(
  loginId: string,
  signal?: AbortSignal
): Promise<boolean> {
  const params = new URLSearchParams({ login_id: loginId });

  const res = await fetch(
    `${API_BASE_URL}/auth/check-login-id?${params}`,
    { signal }
  );

  if (!res.ok) {
    throw new ApiError(
      res.status,
      await parseErrorDetail(res, "아이디 중복 확인에 실패했습니다.")
    );
  }

  const data: { available: boolean } = await res.json();
  return data.available;
}

export async function checkEmail(
  email: string,
  signal?: AbortSignal
): Promise<boolean> {
  const params = new URLSearchParams({ email });

  const res = await fetch(
    `${API_BASE_URL}/auth/check-email?${params}`,
    { signal }
  );

  if (!res.ok) {
    throw new ApiError(
      res.status,
      await parseErrorDetail(res, "이메일 중복 확인에 실패했습니다.")
    );
  }

  const data: { available: boolean } = await res.json();
  return data.available;
}

// ---------- 로그아웃 ----------
export async function logout(): Promise<MessageResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include", // 쿠키를 포함한 요청을 허용
  });

  if (!res.ok) {
    const detail = await parseErrorDetail(res, "로그아웃 중 오류가 발생했습니다.");
    throw new ApiError(res.status, detail);
  }

  return res.json();
}