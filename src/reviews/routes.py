from fastapi import APIRouter, Depends, status
from src.db.models import User
from fastapi.exceptions import HTTPException
from src.auth.dependencies import get_current_user, RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import ReviewCreateModel
from .service import ReviewService


review_router = APIRouter()
review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get('/', dependencies= [user_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    books_reviews = await review_service.get_all_reviews(session)
    return books_reviews


@review_router.get('/{review_uid}', dependencies= [user_role_checker])
async def get_review(review_uid : int,session: AsyncSession = Depends(get_session)):
    book_review = await review_service.get_review(review_uid,session)
    
    if not book_review:
        raise HTTPException(detail = "Review not found", status_code= status.HTTP_404_NOT_FOUND)
    
    return book_review


@review_router.post('/book/{book_uid}')
async def add_book_review(book_uid: int, review_data: ReviewCreateModel, current_user: User = Depends(get_current_user),session:AsyncSession = Depends(get_session)):
    new_review = await review_service.add_review_to_book(
        user_email = current_user.email,
        book_uid = book_uid,
        review_data = review_data,
        session = session 
    )
    return new_review


@review_router.delete('/{review_uid}', dependencies= [user_role_checker], status_code= status.HTTP_204_NO_CONTENT)
async def delete_boook_review(review_uid : int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    await review_service.delete_review_from_book(review_uid= review_uid, user_email= current_user.email, session= session)

    return None