from fastapi import HTTPException


class LocalizedHTTPException(HTTPException):
    """An HTTPException whose detail is a translation-catalog key with format params, resolved per-request locale."""

    def __init__(self, status_code: int, detail: str, **params: str) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.params = params
