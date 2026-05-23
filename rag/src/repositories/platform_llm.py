from rag.src.models.platform_llm import PlatformLLM
from rag.src.repositories.base import BaseRepository


class PlatformLLMRepository(BaseRepository[PlatformLLM]):
    def __init__(self, session):
        super().__init__(PlatformLLM, session)
