from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware

@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has been stopped")

version = "v1"

app = FastAPI(
    title= "Bookly",
    description= "A rest API for a book review web service",
    version= version,
    # lifespan= life_span
)

register_all_errors(app)

register_middleware(app)


app.include_router(book_router, prefix = "/api/{version}/books", tags = ['books'])
app.include_router(auth_router, prefix = "/api/{version}/auth", tags = ['auth'])
app.include_router(review_router, prefix = "/api/{version}/review", tags = ['reviews'])
app.include_router(tags_router, prefix = "/api/{version}/tags", tags = ['tags'])



# deleted main.py file

# @app.get('/')
# async def read_root():
#     return {"message" : "Hello World!"}

# @app.get('/greet{name}')
# async def greet(name:str):
#     return {"message": f"Hello {name}"} 
