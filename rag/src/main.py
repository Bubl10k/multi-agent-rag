import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from rag.src.api.routes import main as main_router
from rag.src.common import settings
from rag.src.utils.exceptions import LocalizedHTTPException
from rag.src.utils.i18n import resolve_locale, translate

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("rag").setLevel(logging.DEBUG)

origins = [
    "http://localhost",
    "http://localhost:3000",
] + settings.app.ALLOWED_ORIGINS


def get_application():
    _app = FastAPI()

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-CAPTCHA-Required"],
    )

    _app.include_router(main_router.router)

    @_app.exception_handler(HTTPException)
    async def localized_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, str):
            locale = resolve_locale(request.headers.get("accept-language"))
            params = exc.params if isinstance(exc, LocalizedHTTPException) else {}
            detail = translate(detail, locale, **params)
        return JSONResponse(status_code=exc.status_code, content={"detail": detail}, headers=exc.headers)

    return _app


app = get_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
