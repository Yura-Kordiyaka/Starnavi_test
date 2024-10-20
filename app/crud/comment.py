from database.settings import get_session
from schemas.comment import CommentCreate, CommentSchema, CommentAnalytics, CommentsRequest
from models.user import User
from models.posts import Post
from sqlalchemy.ext.asyncio import AsyncSession
from utils.ai_helper import check_profanity
from models.posts import Comment
from fastapi import Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy import case
from utils.ai_helper import reply_to_comments


async def comment_create(user: User, comment: CommentCreate,
                         background_tasks: BackgroundTasks,
                         db: AsyncSession = Depends(get_session),
                         ) -> CommentSchema:
    post = await db.get(Post, comment.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    check = check_profanity(comment.content)
    if not isinstance(db, AsyncSession):
        raise ValueError("db is not an instance of AsyncSession")
    new_comment = Comment(
        author_id=user.id,
        is_blocked=check,
        **comment.dict(),
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment)

    if post.auto_reply_enabled and new_comment.is_blocked == False:
        combined_text = post.title + " " + post.content
        background_tasks.add_task(reply_to_comments, new_comment, combined_text, db, post.auto_reply_delay)

    return CommentSchema.from_orm(new_comment)


async def get_all_comments_to_post(post_id: int, skip: int, limit: int, db: AsyncSession = Depends(get_session)) -> \
list[CommentSchema]:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db.execute(
        select(Comment).where(Comment.post_id == post_id).offset(skip).limit(limit)
    )
    comments = result.scalars().all()

    comment_responses = [CommentSchema.from_orm(comment) for comment in comments]
    return comment_responses


async def get_comments_daily_breakdown(
        db: AsyncSession,
        user_id: int,
        request: CommentsRequest
) -> CommentAnalytics:
    posts = await db.execute(
        select(Post.id)
        .where(Post.author_id == user_id)
    )
    post_ids = posts.scalars().all()

    if not post_ids:
        return CommentAnalytics(date=str(request.date_from), total_comments=0, blocked_comments=0)

    result = await db.execute(
        select(
            func.date(Comment.created_at).label('date'),
            func.count(Comment.id).label('total_comments'),
            func.sum(case((Comment.is_blocked == True, 1), else_=0)).label('blocked_comments')
        )
        .where(
            Comment.post_id.in_(post_ids),
            Comment.created_at >= request.date_from,
            Comment.created_at <= request.date_to,
        )
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
    )

    total_comments = 0
    blocked_comments = 0
    date = str(request.date_from)

    for row in result:
        total_comments += row.total_comments
        blocked_comments += row.blocked_comments

    return CommentAnalytics(
        date=date,
        total_comments=total_comments,
        blocked_comments=blocked_comments
    )
