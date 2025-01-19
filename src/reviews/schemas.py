from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ReviewModel(BaseModel):
    uid: int 
    rating: int = Field(lt = 5)
    review_text: str
    user_uid: Optional[uuid.UUID] 
    book_uid: Optional[int]
    created_at: Optional[datetime] 
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 


class ReviewCreateModel(BaseModel):
    rating: int = Field(lt = 5)
    review_text: str

    class Config:
        from_attributes = True