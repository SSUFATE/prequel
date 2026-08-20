export type KContentType = "MOVIE" | "DRAMA" | "WEBTOON"

export interface KContent {
  content_id: number;
  title: string;
  content_type: KContentType;
  overview: string | null;
  release_date: string;
  poster_url: string | null;
}

export interface KContentListResponse {
  total: number;
  page: number;
  size: number;
  items: KContent[];
}

export interface KContentListParams {
  search?: string;
  content_type?: KContentType;
  page?: number;
  size?: number;
}