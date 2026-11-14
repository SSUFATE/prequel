
import LiteratureDetail from "@/components/literature/LiteratureDetail";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return <LiteratureDetail workId={id} />;
}
