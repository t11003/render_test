from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Pydantic Models
class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    published_year: Optional[int] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None

class Book(BookBase):
    id: int

# In-memory database
books_db = {
    1: {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien", "description": "A fantasy novel.", "published_year": 1937},
    2: {"id": 2, "title": "1984", "author": "George Orwell", "description": "A dystopian social science fiction novel.", "published_year": 1949}
}

@app.get("/")
def read_root():
    return {"message": "Morning"}

@app.get("/hello")
def read_hello():
    return {"message": "Hello"}

@app.get("/api")
def read_api(name: str = "Guest"):
    return {
        "status": "success",
        "message": f"Welcome to the new API endpoint, {name}!",
        "data": {
            "version": "1.0.0",
            "features": ["FastAPI", "Uvicorn", "Render"]
        }
    }

# CRUD Endpoints for Books

# 1. Create a Book
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_id = max(books_db.keys(), default=0) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "published_year": book.published_year
    }
    books_db[new_id] = new_book
    return new_book

# 2. Read All Books (with optional search)
@app.get("/books", response_model=List[Book])
def read_books(author: Optional[str] = None, title: Optional[str] = None):
    results = list(books_db.values())
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]
    return results

# 3. Read a Specific Book by ID
@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book

# 4. Update a Book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate):
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    # Update fields if provided
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        book[key] = value
        
    books_db[book_id] = book
    return book

# 5. Delete a Book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    del books_db[book_id]
    return
