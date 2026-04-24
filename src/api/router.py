from fastapi import APIRouter

from src.api.routes.accounts import router as accounts_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(accounts_router)
