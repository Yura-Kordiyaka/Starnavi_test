from database.settings import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'))
    auto_reply_enabled = Column(Boolean, default=False)
    auto_reply_delay = Column(Integer)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    author_id = Column(Integer, ForeignKey('users.id'))
    is_blocked = Column(Boolean, default=False)
    content = Column(String)
    reply_from_ai = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    post = relationship('Post', back_populates='comments')
    author = relationship('User', back_populates='comments')
