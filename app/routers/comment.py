from fastapi import Depends, APIRouter, BackgroundTasks
from starlette import status

from database.settings import get_session
from schemas.comment import CommentCreate, CommentsRequest, CommentAnalytics, CommentSchema
from models.user import User
from fastapi import Path
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_auth import get_current_user
from crud.comment import comment_create, get_comments_daily_breakdown
from datetime import date

comment_router = APIRouter(prefix="/comment", tags=["comment"])


@comment_router.post("/create", response_model=CommentSchema,status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate, background_tasks: BackgroundTasks,
                         db: AsyncSession = Depends(get_session),
                         user: User = Depends(get_current_user),
                         ):
    response = await comment_create(user, comment, background_tasks, db)
    return response


@comment_router.get("/daily-breakdown/{date_from}/{date_to}/", response_model=CommentAnalytics)
async def get_comments_breakdown(date_from: date = Path(...),
                                 date_to: date = Path(...), user: User = Depends(get_current_user),
                                 db: AsyncSession = Depends(get_session)):
    request = CommentsRequest(date_from=date_from, date_to=date_to)
    breakdown = await get_comments_daily_breakdown(db, user.id, request)
    return breakdown
