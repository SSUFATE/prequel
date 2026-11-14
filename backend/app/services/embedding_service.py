from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-m3"


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def encode(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()


embedding_service = EmbeddingService()