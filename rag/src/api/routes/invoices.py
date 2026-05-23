import os

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from rag.src.api.dependencies import UserDep
from rag.src.services.s3 import s3_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/download")
async def download_invoice(key: str = Query(...), _user: UserDep = None) -> Response:
    try:
        pdf_bytes = s3_service.download_invoice(key)
    except Exception:
        raise HTTPException(status_code=404, detail="Invoice not found")

    filename = os.path.basename(key)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
