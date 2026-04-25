from datetime import datetime
from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import String, cast, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from rag.src.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Generic[ModelType], session: AsyncSession) -> None:
        self.session = session
        self.model = model

    async def create_one(self, data: dict) -> ModelType:
        row = self.model(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get_one(self, **params) -> ModelType:
        query = select(self.model).filter_by(**params)
        result = await self.session.execute(query)
        db_row = result.scalar_one_or_none()
        return db_row

    async def get_many(
        self,
        skip: int = 1,
        limit: int = 10,
        options: list | None = None,
        search_query: str | None = None,
        search_fields: list | None = None,
        order_by: list | None = None,
        **params,
    ) -> list[ModelType]:
        offset = (skip - 1) * limit
        scalar_params = {k: v for k, v in params.items() if not isinstance(v, list)}
        list_params = {k: v for k, v in params.items() if isinstance(v, list)}
        query = select(self.model).filter_by(**scalar_params)
        for field, values in list_params.items():
            query = query.where(getattr(self.model, field).in_(values))
        query = query.offset(offset).limit(limit)
        if options:
            query = query.options(*options)

        if search_query and search_fields:
            query = await self._apply_search(query, search_query, search_fields)

        if order_by:
            query = query.order_by(*order_by)

        result = await self.session.execute(query)
        db_rows = result.scalars().all()
        return db_rows

    async def get_many_paginated(
        self,
        skip: int = 0,
        limit: int = 10,
        search_query: str | None = None,
        search_fields: list | None = None,
        options: list | None = None,
        order_by: list | None = None,
        **params,
    ) -> dict:
        count_query = select(func.count()).select_from(self.model).filter_by(**params)

        offset = (skip - 1) * limit
        query = select(self.model).filter_by(**params).offset(offset).limit(limit)

        if options:
            query = query.options(*options)

        if search_query and search_fields:
            query = await self._apply_search(query, search_query, search_fields)
            count_query = await self._apply_search(count_query, search_query, search_fields)

        if order_by:
            query = query.order_by(*order_by)

        result = await self.session.execute(query)
        records = result.scalars().all()
        result_count = await self.session.execute(count_query)
        total_count = result_count.scalar()

        return {
            "total_count": total_count,
            "records": records,
        }

    async def update_one(self, model_id: str, data: dict) -> ModelType:
        query = update(self.model).where(self.model.id == model_id).values(**data).returning(self.model)
        res = await self.session.execute(query)
        res.updated_at = datetime.now()
        await self.session.commit()
        return res.scalar_one()

    async def delete_one(self, model_id: str) -> ModelType:
        query = delete(self.model).where(self.model.id == model_id).returning(self.model)
        res = await self.session.execute(query)
        await self.session.commit()
        return res.scalar_one()

    async def get_one_or_404(self, **params) -> ModelType:
        db_row = await self.get_one(**params)
        if not db_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Object not found",
            )
        return db_row

    @staticmethod
    async def _apply_search(query, search_query: str, search_fields: list):
        if search_query and search_fields:
            search_pattern = f"%{search_query}%"
            query = query.where(or_(*(cast(field, String).ilike(search_pattern) for field in search_fields))).distinct()
        return query
