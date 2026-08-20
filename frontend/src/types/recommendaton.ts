export type TagCategory = 
  | "ERA_SETTING"
  | "GENRE"
  | "SUBJECT"
  | "MOOD"
  | "EMOTIONAL"
  | "RELATIONSHIP"
  | "CULTURAL_CONTEXT"

export interface MatchedTag {
  tag_id: number;
  name: string;
  category: TagCategory
  content_weight: number;
  literature_weight: number;
}

export interface Recommendation {
  work_id: number;
  title: string;
  author: string;
  summary: string;
  genre: string;
  era: string;
  published_year: number;
  cover_url: string | null;
  similarity_score: number;
  matched_tags: MatchedTag[];
}

export interface RecommendationResponse {
  content_id: number;
  content_title: string;
  recommendations: Recommendation[];
}

export interface RecommendationParams {
  limit?: number;
  category?: TagCategory;
}