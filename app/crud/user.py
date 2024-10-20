import schemas.user
import schemas.token
from models.user import User
from fastapi import Depends, HTTPException
from database.settings import get_session
from schemas.user import UserResponseSchemas, UserCreateSchemas
from services.user_auth import create_access_token, create_refresh_token, get_hashed_password
from sqlalchemy import select

async def create_user(db: Depends(get_session), user_in: UserCreateSchemas) -> UserResponseSchemas:
    user_in.password = get_hashed_password(user_in.password)
    existing_user = await db.execute(select(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)))
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    user = User(**user_in.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    access = await create_access_token(user.id)
    refresh = await create_refresh_token(user.id)
    token = schemas.token.Token(access_token=access, refresh_token=refresh)
    return UserResponseSchemas(**user_in.dict(), id=user.id, token=token)



