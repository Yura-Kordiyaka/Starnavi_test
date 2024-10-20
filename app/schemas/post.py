from pydantic import BaseModel

from typing import List, Optional
from schemas.comment import CommentSchema

class PostBase(BaseModel):
    title: str
    content: str
    auto_reply_enabled: Optional[bool] = False
    auto_reply_delay: Optional[int] = None


class PostCreateSchema(PostBase):
    pass


class PostSchemaResponse(PostBase):
    id: int
    author_id: int
    is_blocked: bool

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        from_attributes = True
