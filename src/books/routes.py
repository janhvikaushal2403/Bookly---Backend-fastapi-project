from urllib import response
from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from src.books import schemas
from src.books.schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from src.db.main import get_session
from src.books.service import BookService
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    print("api working...", flush=True)
    print("user_details = ", token_details, flush=True)
    books = await book_service.get_all_books(session)
    print("success")
    return books


@book_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[role_checker]
)
async def get_user_books_submission(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_user_books(user_uid, session)
    print("success")
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    print("create book api working...")
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    print("success")
    return new_book


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: int,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    print(" get api working")
    book = await book_service.get_a_book(book_uid, session)
    print(" get book")
    if book:
        print("success")
        return book

    else:
        print("no response")
        raise BookNotFound()
    #   raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Book not found")


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: int,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    updated_book = await book_service.update_books(book_uid, book_update_data, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: int,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    print("delete api working....")
    book_to_delete = await book_service.delete_books(book_uid, session)
    print("delete book")
    if book_to_delete is None:
        print("book not found")
        raise BookNotFound()
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    else:
        print("deleted successfully")
        return None
