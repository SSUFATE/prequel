import axiosInstance from "./axiosInstance";
import type {
  KContent,
  KContentListParams,
  KContentListResponse,
} from "@/types/kcontent";

export const getKContents = async (
  params: KContentListParams = {}
): Promise<KContentListResponse> => {
  const response = await axiosInstance.get<KContentListResponse>(
    "/api/v1/k-contents",
    {
      params: {
        search: params.search,
        content_type: params.content_type,
        page: params.page ?? 1,
        size: params.size ?? 10,
      },
    }
  );

  return response.data;
};

export const getKContentById = async (
  contentId: number
): Promise<KContent> => {
  const response = await axiosInstance.get<KContent>(
    `/api/v1/k-contents/${contentId}`
  );

  return response.data;
}