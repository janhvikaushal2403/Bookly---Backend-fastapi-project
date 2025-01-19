from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from .service import TagService
from .schemas import TagModel, TagCreateModel, TagAddModel
from src.books.schemas import Book
from typing import List
from src.auth.dependencies import RoleChecker
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession


tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


# @tags_router.get('/', response_model = List[TagModel] ,dependencies= [user_role_checker])
# async def get_all_tags(session: AsyncSession = Depends(get_session)):
#     tags = await tag_service.get_all_book_tags(session)

#     return tags

@tags_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_tags(session)

    return tags

@tags_router.post('/', response_model= TagModel, status_code= status.HTTP_201_CREATED, dependencies= [user_role_checker])
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)

    return tag_added


@tags_router.post('/book/{book_uid}/tags', response_model= Book, dependencies = [user_role_checker])
async def add_tags_to_book(book_uid: int, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)) -> Book:
    book_with_tag = await tag_service.add_tag_to_books(book_uid= book_uid, tag_data= tag_data,session= session)

    return book_with_tag


@tags_router.put('/{tag_uid}', response_model= TagModel, dependencies= [user_role_checker])
async def update_book_tag(tag_uid : int, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session)) -> TagModel:
    updated_tag = await tag_service.update_tag(tag_uid=tag_uid, tag_update_data= tag_update_data, session= session)

    return updated_tag


@tags_router.delete('/{tag_uid}', status_code= status.HTTP_204_NO_CONTENT, dependencies= [user_role_checker])
async def delete_tags(tag_uid: int, session: AsyncSession = Depends(get_session)) -> None:
    deleted_tag = await tag_service.delete_tag(tag_uid, session)
    # if deleted_tag is not None:
    #    print("tag not found")
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tag not found")
    
    # else:
    #    print("deleted successfully")
    return None
    
