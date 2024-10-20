from pydantic import BaseModel
from typing import Optional
from datetime import date


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int


class CommentSchema(CommentBase):
    id: int
    post_id: int
    is_blocked: bool

    class Config:
        orm_mode = True
        from_attributes = True


class CommentsRequest(BaseModel):
    date_from: date
    date_to: date


class CommentAnalytics(BaseModel):
    total_comments: int
    blocked_comments: int
