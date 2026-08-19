interface ContentCardProps {
  title: string;
  image?: string;
}

export default function ContentCard({
  title,
  image,
}: ContentCardProps) {
  return (
    <article className="content-card">
      <div className="poster-area">
        {image ? (
          <img src={image} alt={title} />
        ) : (
          <div className="poster-placeholder" />
        )}
      </div>

      <h3>{title}</h3>
    </article>
  );
}