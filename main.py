import os
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Database URL configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./books.db")

# Convert legacy postgres:// to postgresql:// for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine arguments
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Database Model
class DBBook(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    published_year = Column(Integer, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed initial mock data if empty
def seed_mock_data():
    db = SessionLocal()
    try:
        if db.query(DBBook).count() == 0:
            mock_books = [
                DBBook(title="The Hobbit", author="J.R.R. Tolkien", description="A fantasy novel.", published_year=1937),
                DBBook(title="1984", author="George Orwell", description="A dystopian social science fiction novel.", published_year=1949)
            ]
            db.add_all(mock_books)
            db.commit()
    finally:
        db.close()

seed_mock_data()

app = FastAPI()

# Pydantic Schemas
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

    class Config:
        from_attributes = True

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# CRUD Endpoints for Books using Database

# 1. Create a Book
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = DBBook(
        title=book.title,
        author=book.author,
        description=book.description,
        published_year=book.published_year
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# 2. Read All Books (with optional search)
@app.get("/books", response_model=List[Book])
def read_books(author: Optional[str] = None, title: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DBBook)
    if author:
        query = query.filter(DBBook.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(DBBook.title.ilike(f"%{title}%"))
    return query.all()

# 3. Read a Specific Book by ID
@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(DBBook).filter(DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return db_book

# 4. Update a Book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(DBBook).filter(DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    # Update fields if provided
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
        
    db.commit()
    db.refresh(db_book)
    return db_book

# 5. Delete a Book
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(DBBook).filter(DBBook.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    db.delete(db_book)
    db.commit()
    return

