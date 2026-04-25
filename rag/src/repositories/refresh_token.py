import uuid

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models.refresh_token import RefreshToken
from rag.src.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        return await self.get_one(jti=jti)

    async def revoke_jti(self, jti: str) -> None:
        await self.session.execute(update(RefreshToken).where(RefreshToken.jti == jti).values(is_revoked=True))

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True)
        )
