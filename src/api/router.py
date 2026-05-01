from fastapi import APIRouter

from src.api.routes.accounts import router as accounts_router
from src.api.routes.movies import router as movies_router
from src.api.routes.cart import router as cart_router
from src.api.routes.notifications import router as notifications_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(accounts_router)
api_router.include_router(movies_router)
api_router.include_router(cart_router)
api_router.include_router(notifications_router)
