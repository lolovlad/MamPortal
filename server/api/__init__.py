from fastapi import APIRouter
from .login import router as login_router
from .user import router as user_router
from .env import router as env_router
from .article import router as article_router
from .event import router as event_router
from .calendar import router as calendar_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(user_router)
router.include_router(env_router)
router.include_router(article_router)
router.include_router(event_router)
router.include_router(calendar_router)