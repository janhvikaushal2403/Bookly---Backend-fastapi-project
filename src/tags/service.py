from fastapi.exceptions import HTTPException
from src.books.service import BookService
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Tag
from sqlmodel import select, desc
from .schemas import TagCreateModel, TagAddModel
from src.errors import BookNotFound, TagAlreadyExists, TagNotFound


book_service = BookService()
server_error = HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Something went wrong")


class TagService:

    # async def get_all_book_tags(self, session: AsyncSession):
    #     statement = select(Tag).order_by(desc(Tag.created_at))
    #     print("working")
    #     print(statement)
    #     result = await session.execute(statement)

    #     return result.scalars().all()

    async def get_tags(self, session: AsyncSession):
        """Get all tags"""

        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.execute(statement)

        return result.scalars().all()
    

    async def get_tag_by_uid(self, tag_uid: int, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.execute(statement)

        return result.scalar_one_or_none()
    
    # adding tag to book
    async def add_tag_to_books(self, book_uid: int, tag_data: TagAddModel, session: AsyncSession):
        book = await book_service.get_a_book(book_uid = book_uid, session = session)

        if not book:
            raise BookNotFound()
            # raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Book not found")
        
        for tag_item in tag_data.tags:
            result = await session.execute(select(Tag).where(Tag.name == tag_item.name))

            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name = tag_item.name)

            book.tags.append(tag)
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book
    
    # creating tag
    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.execute(statement)
        tag = result.scalar_one_or_none()

        if tag:
            raise TagAlreadyExists()
            # raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Tag already exists")
        
        new_tag = Tag(name = tag_data.name)
        session.add(new_tag)
        await session.commit()
        return new_tag
    

    async def update_tag(self,tag_uid, tag_update_data: TagCreateModel, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)
        update_data_dict = tag_update_data.model_dump()

        for k,v in update_data_dict.items():
            setattr(tag, k, v)

            await session.commit()
            await session.refresh(tag)

        return tag
    

    async def delete_tag(self, tag_uid: int, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()
            # raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "tag does not exist")
        
        await session.delete(tag)
        await session.commit()