from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from rag.src.api.dependencies import CurrentUserDep, UnitOfWorkDep, UserManagerDep
from rag.src.api.schemas.auth import RefreshRequest, TokenResponse
from rag.src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: UserManagerDep,
    uow: UnitOfWorkDep,
):
    user = await user_manager.authenticate(credentials)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )
    return await AuthService().create_token_pair(uow, user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    user_manager: UserManagerDep,
    uow: UnitOfWorkDep,
):
    return await AuthService().refresh_tokens(uow, body.refresh_token, user_manager)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    uow: UnitOfWorkDep,
    _: CurrentUserDep,
):
    await AuthService().revoke_refresh_token(uow, body.refresh_token)
