from pydantic import BaseModel
# import uuid
from datetime import datetime, date
from typing import Optional, List
from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel

class Book(BaseModel):
    uid: Optional[int]
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BookDetailModel(Book):
    reviews: List[ReviewModel]
    tags: List[TagModel]

    class Config:
        from_attributes = True
        

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str 
    # created_at: Optional[datetime]
    # updated_at: Optional[datetime] 
    class Config:
        from_attributes = True

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str

    class Config:
        from_attributes = True

 