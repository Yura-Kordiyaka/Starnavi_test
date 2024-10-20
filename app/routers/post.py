from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.settings import get_session
from schemas.comment import CommentSchema
from services.user_auth import get_current_user
from schemas.post import PostCreateSchema, PostSchemaResponse
from models.user import User
from crud.post import post_create, get_posts
from crud.comment import get_all_comments_to_post

post_router = APIRouter(
    prefix="/post",
    tags=["post"],
)


@post_router.post("/create", status_code=201)
async def create_post(post: PostCreateSchema, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_session)) -> PostSchemaResponse:
    response = await post_create(user, post, db)
    return response


@post_router.get("/posts", response_model=list[PostSchemaResponse])
async def get_all_posts(skip: int = 0, limit: int = 10, user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_session)):
    response = await get_posts(skip, limit, user, db)
    return response


@post_router.get("/posts/{post_id}/comments", response_model=list[CommentSchema])
async def get_post_comments(post_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_session)):
    response = await get_all_comments_to_post(post_id, skip, limit, db)
    return response
