from enum import StrEnum

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class InvalidDetailsEnum(StrEnum):
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    USER_INACTIVE = "USER_INACTIVE"
    TOKEN_REUSE_DETECTED = "TOKEN_REUSE_DETECTED"
