from fastapi import APIRouter
from .user import user_router
from .post import post_router
from .comment import comment_router

router = APIRouter(
    prefix="/v1",
)
router.include_router(user_router)
router.include_router(post_router)
router.include_router(comment_router)
