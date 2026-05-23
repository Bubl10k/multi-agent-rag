"""Shared test constants and ORM-object factories used across test modules."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from rag.src.agent.types import AgentType

USER_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OTHER_USER_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
LLM_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
COLLECTION_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
AGENT_ID = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
CONVERSATION_ID = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
MESSAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

NOW = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def make_llm_obj(user_id: uuid.UUID = USER_ID) -> SimpleNamespace:
    return SimpleNamespace(id=LLM_ID, model_name="gpt-4o", is_active=True, user_id=user_id)


def make_collection_obj(user_id: uuid.UUID = USER_ID) -> SimpleNamespace:
    return SimpleNamespace(
        id=COLLECTION_ID,
        name="test-collection",
        description="A test collection",
        embedding_model="text-embedding-3-small",
        user_id=user_id,
    )


def make_agent_obj(user_id: uuid.UUID = USER_ID) -> SimpleNamespace:
    return SimpleNamespace(
        id=AGENT_ID,
        name="test-agent",
        prompt="You are a helpful assistant.",
        agent_type=AgentType.GENERAL,
        agent_config={},
        is_active=True,
        user_id=user_id,
        llm=make_llm_obj(user_id),
        platform_llm=None,
        collections=[],
    )


def make_message_obj() -> SimpleNamespace:
    return SimpleNamespace(id=MESSAGE_ID, role="user", content="Hello", created_at=NOW)


def make_conversation_obj(user_id: uuid.UUID = USER_ID) -> SimpleNamespace:
    return SimpleNamespace(
        id=CONVERSATION_ID,
        agent_id=AGENT_ID,
        user_id=user_id,
        created_at=NOW,
        messages=[make_message_obj()],
    )
