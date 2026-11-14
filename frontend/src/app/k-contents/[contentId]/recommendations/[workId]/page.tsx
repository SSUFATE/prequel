
import LiteratureDetail from "@/components/literature/LiteratureDetail";

export default async function Page({
  params,
}: {
  params: Promise<{
    contentId: string;
    workId: string;
  }>;
}) {
  const { contentId, workId } = await params;

  return (
    <LiteratureDetail
      contentId={contentId}
      workId={workId}
    />
  );
}
