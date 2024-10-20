import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.settings import get_session, Base
from app.main import app
from models.posts import Post
from sqlalchemy.future import select
from schemas.token import Token
from httpx import AsyncClient
from sqlalchemy.pool import NullPool
from models.posts import Comment
from schemas.comment import CommentAnalytics
from datetime import date, timedelta
from config import settings

DATABASE_TEST_URL = f"postgresql+asyncpg://{settings.db.DB_TEST_USER}:{settings.db.DB_TEST_PASSWORD}@{settings.db.DB_TEST_HOST}/{settings.db.DB_TEST_NAME}"

test_engine = create_async_engine(DATABASE_TEST_URL, echo=True, future=True, poolclass=NullPool)

TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def test_db_session():
    async with TestSessionLocal() as session:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def override_get_session(test_db_session):
    async def override_session():
        yield test_db_session

    app.dependency_overrides[get_session] = override_session


async def create_and_login_user(client, user_data):
    response = await client.post("/api/v1/user/sign_up", json=user_data)
    assert response.status_code == 201

    response = await client.post("/api/v1/user/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })

    assert response.status_code == 200
    token_data = Token(**response.json())
    assert token_data.access_token is not None
    return token_data.access_token


@pytest.mark.asyncio
async def test_create_post_with_profanity(test_db_session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "hashedpassword",
        "first_name": "Test",
        "last_name": "User"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = await create_and_login_user(client, user_data)

        post_data_profanity = {
            "title": "Test Post Profanity",
            "content": "this world is a piece of shit"
        }

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/post/create", json=post_data_profanity, headers=headers)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["title"] == post_data_profanity["title"]
        assert response_data["content"] == post_data_profanity["content"]

        stmt = select(Post).where(Post.title == post_data_profanity["title"])
        result = await test_db_session.execute(stmt)
        post = result.scalar_one_or_none()

        assert post is not None
        assert post.title == post_data_profanity["title"]
        assert post.is_blocked is True
        assert post.content == post_data_profanity["content"]


@pytest.mark.asyncio
async def test_create_post_with_normal_content(test_db_session):
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "hashedpassword",
        "first_name": "Test",
        "last_name": "User"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = await create_and_login_user(client, user_data)

        post_data_normal = {
            "title": "Normal Post Title",
            "content": "This is a normal post content."
        }

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/post/create", json=post_data_normal, headers=headers)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["title"] == post_data_normal["title"]
        assert response_data["content"] == post_data_normal["content"]

        stmt = select(Post).where(Post.title == post_data_normal["title"])
        result = await test_db_session.execute(stmt)
        post = result.scalar_one_or_none()

        assert post is not None
        assert post.title == post_data_normal["title"]
        assert post.is_blocked is False
        assert post.content == post_data_normal["content"]


@pytest.mark.asyncio
async def test_get_comments_breakdown(test_db_session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "hashedpassword",
        "first_name": "Test",
        "last_name": "User"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = await create_and_login_user(client, user_data)

        post_data = {
            "title": "Test Post",
            "content": "This is a test post."
        }

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/post/create", json=post_data, headers=headers)
        assert response.status_code == 201

        comment_data_1 = {
            "content": "This is a test comment.",
            "post_id": response.json()["id"],
        }

        comment_data_2 = {
            "content": "this world is a piece of shit",
            "post_id": response.json()["id"],
        }

        response = await client.post("/api/v1/comment/create", json=comment_data_1, headers=headers)
        assert response.status_code == 201

        response = await client.post("/api/v1/comment/create", json=comment_data_2, headers=headers)
        assert response.status_code == 201
        stmt = select(Comment).where(Comment.post_id == response.json()["post_id"])
        result = await test_db_session.execute(stmt)
        comments = result.scalars().all()

        date_from = date.today() - timedelta(days=3)
        date_to = date.today()

        response = await client.get(f"/api/v1/comment/daily-breakdown/{date_from}/{date_to}/", headers=headers)
        assert response.status_code == 200
        analytics: CommentAnalytics = CommentAnalytics(**response.json())
        assert analytics.total_comments == 2
        assert analytics.blocked_comments == 1

        assert len(comments) == 2
        assert sum(1 for c in comments if c.is_blocked) == 1
