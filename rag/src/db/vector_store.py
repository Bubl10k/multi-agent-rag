from langchain_core.documents import Document
from langchain_postgres import PGVector

from rag.src.common.settings import settings
from rag.src.db.embeddings import TextEmbedding


class VectorStore:
    """Vector Store uses PGVector to store and search embeddings."""

    def __init__(self, collection_name: str, embedding: TextEmbedding | None = None):
        self.collection_name = collection_name
        if embedding is None:
            embedding = TextEmbedding(
                model=settings.llm.EMBEDDING_MODEL,
                api_key=settings.llm.OPENAI_API_SECRET,
            )
        self._store = PGVector(
            embeddings=embedding.langchain_embeddings,
            collection_name=collection_name,
            connection=settings.database.url_pgvector,
            use_jsonb=True,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        return self._store.add_texts(texts, metadatas=metadatas)

    def add_documents(self, documents: list[Document]) -> list[str]:
        return self._store.add_documents(documents)

    def search(self, query: str, k: int = 4) -> list[Document]:
        return self._store.similarity_search(query, k=k)

    def search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]:
        return self._store.similarity_search_with_score(query, k=k)

    def delete_collection(self) -> None:
        self._store.delete_collection()
