from rag.src.models import LLM
from rag.src.repositories.base import BaseRepository


class LLMRepository(BaseRepository[LLM]):
    def __init__(self, session):
        super().__init__(LLM, session)
