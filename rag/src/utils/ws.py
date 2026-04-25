import uuid

from fastapi import Query, WebSocketException, status
from fastapi_users.jwt import decode_jwt

from rag.src.common import settings


async def ws_get_user_id(token: str = Query(...)) -> uuid.UUID:
    """Decode JWT and return user_id for WebSocket connections."""
    try:
        data = decode_jwt(token, settings.auth.JWT_SECRET, ["fastapi-users:auth"])
        return uuid.UUID(data["sub"])
    except Exception:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
