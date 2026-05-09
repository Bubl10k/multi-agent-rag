import asyncio
import logging

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from rag.src.common import settings

logger = logging.getLogger(__name__)

pool = AsyncConnectionPool(
    settings.database.url_checkpoint,
    max_size=10,
    open=False,
    kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
)

_checkpointer: AsyncPostgresSaver | None = None
_initialized = False
_init_lock = asyncio.Lock()


async def ensure_initialized() -> None:
    global _checkpointer, _initialized
    if _initialized:
        return
    async with _init_lock:
        if not _initialized:
            await pool.open()
            _checkpointer = AsyncPostgresSaver(pool)
            await _checkpointer.setup()
            _initialized = True
            logger.info("LangGraph checkpointer initialized")


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialized")
    return _checkpointer
