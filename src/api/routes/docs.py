from fastapi import APIRouter, Depends, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from src.api.dependencies.auth import require_roles
from src.models.accounts import UserGroupEnum

router = APIRouter(tags=["Docs"])


@router.get("/openapi.json")
async def get_openapi_endpoint(
    request: Request,
    user=Depends(require_roles(UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN)),
):
    return JSONResponse(request.app.openapi())


@router.get("/docs")
async def get_docs_endpoint(
    user=Depends(require_roles(UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN)),
):
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title="Online Cinema API",
    )
