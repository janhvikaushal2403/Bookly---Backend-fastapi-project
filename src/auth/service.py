from src.db.models import User
from .schemas import UserCreateModel, UserModel
from .utils import generate_hash_passord
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


# 2 things we gona do if user exists throw error , if not create user account

class UserService:

    async def get_user_by_email(self,email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        return user

    # check user exists
    async def user_exists(self, email:str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        if user is None:
            return False
        else:
            return True

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(
            **user_data_dict
        )
        new_user.password = generate_hash_passord(user_data_dict['password'])
        # adding user role
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        # return new_user
        return UserModel(
        uid=new_user.uid,
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )

    async def update_user(self,user: User, user_data: dict, session: AsyncSession):

        for k, v in user_data.items():
            setattr(user, k,v)

        await session.commit()
        return user


    # async def delete_users(self,user_uid: str, session: AsyncSession):
    #     user_to_delete = await self.get_user_by_email(user_uid, session)

    #     if user_to_delete is not None:
    #         await session.delete(user_to_delete)
    #         await session.commit()

    #     else:
    #         return None
