from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status
from pydantic import BaseModel, Field


app = FastAPI()


class Book(BaseModel):
    id: Optional[int] = Field(default=None, title='id not needed')
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    class Config:
        json_schema_extra = {
            'example': {
                'title': "A new book",
                'author': 'Some X',
                'description': 'Should be good, no?',
                'rating': 5,
                "published_date": 2000
            }
        }

BOOKS = [
    Book(id=1, title="Computer Science Pro", author="Some X",
         description="A book of science", rating=4, published_date=2023),
    Book(id=2, title="Be fast with FastAPI", author="Some X",
         description="A great book", rating=4, published_date=2022),
    Book(id=3, title="Master endpoints", author="Some X",
        description="A good book", rating=4, published_date=2021),
    Book(id=4, title="HP1", author="Author 1",
        description="Book Description", rating=3, published_date=2022),
    Book(id=5, title="HP2", author="Author 2",
        description="Book Description", rating=2, published_date=2023),
    Book(id=6, title="HP3", author="Author 3",
        description="Book Description", rating=1, published_date=2023),
]

@app.get("/books", response_model=list[Book], status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get('/books/{book_id}', response_model=Book, status_code=status.HTTP_200_OK)
async def read_book(book_id: int  = Path(gt=0))-> Book:
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404 ,detail="Don't find any book with this id")

@app.get("/books/by_rating/", response_model=list[Book], status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6))->list[Book]:
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.put("/books/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: Book):
    book_changed = False
    for index, book_ in enumerate(BOOKS):
        if book_.id == book.id:
            BOOKS[index] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404 ,detail="Item not found")
    
@app.delete("/books/{book_id}", response_model=Book)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for index, book_ in enumerate(BOOKS):
        if book_.id == book_id:
            BOOKS.pop(index)
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404 ,detail="Item not found")
    

@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: Book):
    new_book = find_book_id(book_request)
    BOOKS.append(new_book)
    return new_book

@app.get("/books/by_date/", response_model=list[Book], status_code=status.HTTP_200_OK)
async def get_by_date(published_date: int = Query(gt=1999, lt=2031))-> list[Book]:
    books_ = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_.append(book)
    return books_

def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book