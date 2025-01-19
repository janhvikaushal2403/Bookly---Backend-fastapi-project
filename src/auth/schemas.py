from pydantic import BaseModel, Field
import uuid
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel
from datetime import datetime
from typing import Optional, List



class UserCreateModel(BaseModel):
    first_name: str = Field(max_length= 25)
    last_name: str = Field (max_length= 25)
    email: str = Field(max_length = 40)
    username: str = Field(max_length = 12)
    password: str = Field(min_length = 8)

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str 
    # password: str = Field(exclude= True)
    is_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class  UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]

    class Config:
        from_attributes = True


class UserLoginModel(BaseModel):
    email: str = Field(max_length = 40)
    password: str = Field(min_length = 8) 

    class Config:
        from_attributes = True


class EmailModel(BaseModel):
    email_addresses: List[str]

    class Config:
        from_attributes = True


class PasswordResetRequestModel(BaseModel):
    email: str

    class Config:
        from_attributes = True


class PasswordResetConfirmModel(BaseModel):
    new_password: str = Field(min_length = 8)
    confirm_new_password: str = Field(min_length = 8)

    class Config:
        from_attributes = True
