import { API_BASE_URL, ApiError } from "@/api/auth";

export type Language = "ko" | "en" | "ja" | "zh";

export interface UserResponse {
  user_id: number;
  login_id: string;
  username: string;
  email: string;
  language: Language;
  profile_image_url: string | null;
  role: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  language?: Language;
}


async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("auth:unauthorized"));
    }

    const error = await response.json().catch(() => null);

    const message =
      typeof error?.detail === "string"
        ? error.detail
        : response.status === 401
          ? "로그인이 필요하거나 인증이 만료되었습니다."
          : "요청을 처리하지 못했습니다.";

    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

// 회원정보 조회
export function getMyInfo(): Promise<UserResponse> {
  return request<UserResponse>("/users/me");
}

// 회원정보 수정
export function updateMyInfo(
  data: UserUpdate
): Promise<UserResponse> {
  return request<UserResponse>("/users/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
}

// 프로필 이미지 업로드
export function uploadProfileImage(
  file: File
): Promise<UserResponse> {
  const formData = new FormData();

  formData.append("file", file);

  return request<UserResponse>(
    "/users/me/profile-image",
    {
      method: "POST",
      body: formData,
    }
  );
}

// 프로필 이미지 삭제
export function deleteProfileImage(): Promise<UserResponse> {
  return request<UserResponse>(
    "/users/me/profile-image",
    {
      method: "DELETE",
    }
  );
}

// 회원 탈퇴 (비밀번호 확인)
export function deleteMyAccount(
  password: string
): Promise<{ message: string }> {
  return request<{ message: string }>("/users/me", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ password }),
  });
}

// 이미지 URL
export function getProfileImageUrl(
  imageUrl: string | null
): string | null {
  if (!imageUrl) return null;

  if (
    imageUrl.startsWith("http://") ||
    imageUrl.startsWith("https://")
  ) {
    return imageUrl;
  }

  const SERVER_URL = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

  return `${SERVER_URL}${imageUrl.startsWith("/") ? "" : "/"}${imageUrl}`;
}