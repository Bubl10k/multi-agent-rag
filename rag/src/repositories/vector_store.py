from pathlib import Path

from sqlalchemy import text

from rag.src.db.postgres import vector_engine

_SQL_DIR = Path(__file__).parent / "sql"


class VectorStoreRepository:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def get_files(self) -> list[str]:
        sql = (_SQL_DIR / "get_collection_files.sql").read_text()
        with vector_engine.connect() as conn:
            rows = conn.execute(text(sql), {"name": self.collection_name})
            return [row[0] for row in rows]
