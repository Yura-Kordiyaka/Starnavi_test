from fastapi import Depends
from database.settings import get_session
from schemas.post import PostCreateSchema, PostSchemaResponse
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from utils.ai_helper import check_profanity
from models.posts import Post
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def post_create(user: User, post: PostCreateSchema,
                      db: AsyncSession = Depends(get_session)) -> PostSchemaResponse:
    combined_text = post.title + " " + post.content
    check = check_profanity(combined_text)
    new_post = Post(
        author_id=user.id,
        is_blocked=check,
        **post.dict(),
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    stmt = select(Post).options(selectinload(Post.comments)).where(Post.id == new_post.id)
    result = await db.execute(stmt)
    post_with_comments = result.scalar_one_or_none()

    return PostSchemaResponse.from_orm(post_with_comments)


async def get_posts(skip: int, limit: int, user: User, db: AsyncSession = Depends(get_session)) -> list[
    PostSchemaResponse]:
    result = await db.execute(
        select(Post).where(Post.author_id == user.id).offset(skip).limit(limit)
    )

    posts = result.scalars().all()

    post_responses = [PostSchemaResponse.from_orm(post) for post in posts]

    return post_responses
