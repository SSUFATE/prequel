import { apiDelete, apiGet, apiPostEmpty } from "./client";

export interface FavoriteWorkResponse {
  favorite_id: number;
  work_id: number;
  title: string;
  author: string | null;
  genre: string | null;
  era: string | null;
  cover_url: string | null;
  favorited_at: string;
}

export interface FavoriteResponse {
  favorite_id: number;
  work_id: number;
  created_at: string;
}

export function getMyFavoriteWorks(): Promise<FavoriteWorkResponse[]> {
  return apiGet<FavoriteWorkResponse[]>("/api/v1/favorites", { auth: true });
}

export function addFavorite(workId: number): Promise<FavoriteResponse> {
  return apiPostEmpty<FavoriteResponse>(`/api/v1/favorites/${workId}`, { auth: true });
}

export function removeFavorite(workId: number): Promise<void> {
  return apiDelete<void>(`/api/v1/favorites/${workId}`, { auth: true });
}