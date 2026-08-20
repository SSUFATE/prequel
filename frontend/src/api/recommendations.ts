import axiosInstance from "./axiosInstance";
import type { 
  RecommendationResponse,
  RecommendationParams,
  TagCategory
} from "@/types/recommendation";

export const getRecommendations = async (
  contentId: number,
  params: RecommendationParams = {}
): Promise<RecommendationResponse> => {
  console.log("contentId:", contentId);
  console.log("category:", params.category);
  console.log("limit:", params.limit);
  const response = await axiosInstance.get<RecommendationResponse>(
    `/api/v1/k-contents/${contentId}/recommendations`,
    {
      params: {
        limit: params.limit ?? 20,
        category: params.category,
      },
    }
  );

  return response.data;
};