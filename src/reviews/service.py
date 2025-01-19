from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession


book_service = BookService()
user_service = UserService()

class ReviewService:
    
    async def add_review_to_book(self, user_email:str , book_uid: int, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            book = await book_service.get_a_book(
                book_uid = book_uid, session = session)
            
            user = await user_service.get_user_by_email(
                email= user_email, session= session)
            
            new_review = Review(
                **review_data.model_dump()
            )
            
            # checking if book and user is none or not  
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            new_review.user = user
            new_review.book = book
            
            session.add(new_review)
            await session.commit()
            return new_review
            
        except Exception as e:
            raise HTTPException(
                status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= "Something went wrong....try again")


    async def get_all_reviews(self,session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result  = await session.execute(statement)
        return result.scalars().all()
    

    async def get_review(self, review_uid: int ,session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)

        result  = await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def delete_review_from_book(self, review_uid : int, user_email: str, session: AsyncSession):
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Cannot delete this review")
        
        session.delete(review)
        await session.commit()