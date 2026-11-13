import axiosInstance from "./axiosInstance";
import type { 
  RecommendationResponse,
  RecommendationParams,
} from "@/types/recommendation";

export const getRecommendations = async (
  contentId: number,
  params: RecommendationParams = {}
): Promise<RecommendationResponse> => {
  const endpoint = params.category
    ? `/api/v1/k-contents/${contentId}/recommendations?category=${params.category}&limit=${params.limit ?? 20}`
    : `/api/v1/k-contents/${contentId}/hybrid-recommendations`;

  const response = await axiosInstance.get<RecommendationResponse>(
    endpoint,
    {
      params: {
        limit: params.limit ?? 20,
        ...(params.category && { category: params.category }),
      },
    }
  );

  return response.data;
};