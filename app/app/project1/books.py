from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import JSON

app = FastAPI()

BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]

class BookModel(BaseModel):
    title: str
    author: str
    category: str

@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_author}")
async def get_one_book(book_author: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_author.casefold():
            return book

@app.get("/books/{book_author}/")
async def read_category_by_query(book_author:str,
                                 category: str)-> list[dict[str, str]]:
    book_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold()\
            and book.get('title').casefold() == book_author.casefold():
            book_to_return.append(book)
    return book_to_return

@app.post("/books/create_book")
async def create_book(book: BookModel)->list[BookModel]:
    BOOKS.append(book)
    return BOOKS

@app.put("/books/update_book", response_model= BookModel)
async def update_book(update_book: BookModel)-> BookModel | JSONResponse:
    for index, book in enumerate(BOOKS):
        if book.get('title').casefold() == update_book.get('title').casefold():
            BOOKS[index] = update_book
            return update_book
    return JSONResponse("Don't find any book with that title", 404)

@app.delete("/books/delete/{book_title}", response_model=BookModel)
async def delete_book(book_title: str)-> JSONResponse | BookModel:
    for index, book in enumerate(BOOKS):
        if book.get('title').casefold() == book_title.casefold():
            return BookModel(**BOOKS.pop(index))
    return JSONResponse("Don't find any book with that title", 404)

@app.get("/books/{author}/all", response_model=list[BookModel])
async def get_author_books(author: str)-> list[BookModel]:
    books_ = []
    for index, book in enumerate(BOOKS):
        if book.get('author').casefold() == author.casefold():
            books_.append(BookModel(**book))
    return books_