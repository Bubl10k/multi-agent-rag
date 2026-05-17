from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from rag.src.api.dependencies import AuthServiceDep, CurrentUserDep, UnitOfWorkDep, UserManagerDep
from rag.src.api.schemas.auth import RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: UserManagerDep,
    uow: UnitOfWorkDep,
    service: AuthServiceDep,
):
    user = await user_manager.authenticate(credentials)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )
    return await service.create_token_pair(uow, user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    user_manager: UserManagerDep,
    uow: UnitOfWorkDep,
    service: AuthServiceDep,
):
    return await service.refresh_tokens(uow, body.refresh_token, user_manager)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    uow: UnitOfWorkDep,
    _: CurrentUserDep,
    service: AuthServiceDep,
):
    await service.revoke_refresh_token(uow, body.refresh_token)
