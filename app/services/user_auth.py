from datetime import timedelta, datetime
from jose import JWTError, jwt
from typing import Union, Any
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from models.user import User
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from schemas.token import Token
from fastapi.security import OAuth2PasswordBearer
from schemas.user import UserResponseSchemas
from database.settings import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = settings.token.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.token.REFRESH_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.token.ALGORITHM
JWT_SECRET_KEY = settings.token.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.token.JWT_REFRESH_SECRET_KEY

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


async def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = id
    except JWTError as e:
        print(e)
        raise credentials_exception
    return token_data


def verify_refresh_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = id
    except JWTError as e:
        print(e)
        raise credentials_exception
    return token_data


async def login_user(db: Depends(get_session), user_log: OAuth2PasswordRequestForm = Depends()) -> Token:
    existing_user = await db.execute(select(User).filter(
        (User.username == user_log.username)))
    existing_user = existing_user.scalars().first()
    if existing_user:
        if verify_password(user_log.password, existing_user.password):
            access = await create_access_token(existing_user.id)
            refresh = await create_refresh_token(existing_user.id)
            token = Token(access_token=access, refresh_token=refresh)
            return token
        else:
            raise HTTPException(status_code=400, detail="User with this credentials does not exist")
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="api/v1/user/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth),
                           db: AsyncSession = Depends(get_session)) -> UserResponseSchemas:
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if user_id is None or exp is None:
            raise credentials_exception

        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except jwt.JWTError:
        raise credentials_exception

    existing_user_result = await db.execute(select(User).filter(User.id == int(user_id)))
    existing_user = existing_user_result.scalars().first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return existing_user
