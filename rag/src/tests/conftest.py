import os
import sys
from pathlib import Path

# Add project root to sys.path so `rag` is importable regardless of cwd.
# This file lives at <root>/rag/src/tests/conftest.py → parents[3] == <root>.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Set all required env vars BEFORE any rag imports so pydantic_settings picks them up.
os.environ.setdefault("HOST", "localhost")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("RELOAD", "false")
os.environ.setdefault("ALLOWED_ORIGINS", "[]")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-for-testing-only")
os.environ.setdefault("JWT_LIFETIME_SECONDS", "3600")
os.environ.setdefault("REFRESH_TOKEN_LIFETIME_SECONDS", "2592000")
os.environ.setdefault("ENCRYPTION_KEY", "uiMtg-OTNvgh4nJh4j-j_CPfRFhe5mH3-2Y1jJOVJL4=")
os.environ.setdefault("OPENAI_API_SECRET", "sk-test-openai-key")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from rag.src.main import app
from rag.src.models.user import User
from rag.src.services.auth import current_active_user
from rag.src.utils.unit_of_work import UnitOfWork

from rag.src.tests.helpers import USER_ID


@pytest.fixture
def mock_user() -> User:
    user = MagicMock(spec=User)
    user.id = USER_ID
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def mock_uow() -> UnitOfWork:
    uow = AsyncMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.collection_repository = AsyncMock()
    uow.llm_repository = AsyncMock()
    uow.agent_repository = AsyncMock()
    uow.conversation_repository = AsyncMock()
    uow.message_repository = AsyncMock()
    uow.refresh_token_repository = AsyncMock()
    uow.session = AsyncMock()
    return uow


@pytest_asyncio.fixture
async def async_client(mock_user, mock_uow) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[current_active_user] = lambda: mock_user
    app.dependency_overrides[UnitOfWork] = lambda: mock_uow

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
