from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr


class TextEmbedding:
    """Text Embeddings uses OpenAI's embedding API to embed text."""

    def __init__(self, model: str, api_key: str):
        self._embeddings: Embeddings = OpenAIEmbeddings(model=model, api_key=SecretStr(api_key))

    def embed_query(self, text: str) -> list[float]:
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(texts)

    @property
    def langchain_embeddings(self) -> Embeddings:
        return self._embeddings