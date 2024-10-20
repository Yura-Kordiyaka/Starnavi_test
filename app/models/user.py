from database.settings import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship
from models.posts import Post,Comment

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    created_at = mapped_column(DateTime, default=func.now())
    updated_at = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    posts = relationship(Post, back_populates='author')
    comments = relationship('Comment', back_populates='author')