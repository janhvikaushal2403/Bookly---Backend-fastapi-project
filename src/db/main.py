from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config

engine = AsyncEngine(
    create_engine(
    url = Config.DATABASE_URL,
    # echo = True  disabling it after creating middleware coz we no more need it
))

async def init_db() -> None:
    async with engine.begin() as conn:
        from src.db.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)
        # statement = text("SELECT 'hello';")

        # result = await conn.execute(statement)
        # print(result.all())

AsyncSessionLocal = sessionmaker(
    bind= engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get a session
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# async def get_session() -> AsyncSession:
#     Session = sessionmaker(
#         bind = AsyncEngine,
#         class_= AsyncSession,
#         expire_on_commit = False
#     )
#     async with Session() as session:
#         yield session