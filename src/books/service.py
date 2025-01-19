from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel, Book
from sqlmodel import select, desc
from src.db.models import Book
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()

    # function for get all books of user which logged in
    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.execute(statement)
        return result.scalars().all()

    async def get_a_book(self, book_uid: int, session: AsyncSession):
        #  Fetch the ORM model
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)
        book = result.scalar_one_or_none()
        print(type(book))
        # If book exists, convert it to a Pydantic model and return
        if book:
            return book
        # Return the Pydantic model directly
        #       return Book(
        #             uid=book.uid,  # Dot notation since it's an ORM object
        #             title=book.title,
        #             author=book.author,
        #             publisher=book.publisher,
        #             published_date=book.published_date,
        #             page_count=book.page_count,
        #             language=book.language,
        #             created_at=book.created_at,
        #             updated_at=book.updated_at
        # )
        return None

    # if book is not None else None

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        # new_book.published_date = datetime.strptime(book_data_dict['published_date'], "%Y-%m-%d")
        # adding user_uid
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_books(
        self, book_uid: int, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_a_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update

    async def delete_books(self, book_uid: int, session: AsyncSession):
        book_to_delete = await self.get_a_book(book_uid, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()

        else:
            return None
