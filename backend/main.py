from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

class Book(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None

class BookInDB(Book):
    id: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["books-appdb"]

def book_helper(doc) -> BookInDB:
    """Convert MongoDB document to BookInDB schema"""
    return BookInDB(
        id=str(doc["_id"]),
        title=doc["title"],
        author=doc["author"],
        isbn=doc.get("isbn")
    )

@app.get("/books", response_model=list[BookInDB])
async def list_books():
    books = []
    cursor = db.items.find({})
    async for doc in cursor:
        books.append(book_helper(doc))
    return books


@app.post("/books/add", response_model=BookInDB)
async def add_book(book: Book):
    doc = book.model_dump()
    result = await db.items.insert_one(doc)
    new_doc = await db.items.find_one({"_id": result.inserted_id})
    return book_helper(new_doc)

@app.delete("/books/delete/{book_id}")
async def delete_book(book_id: str):
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    result = await db.items.delete_one({"_id": obj_id})

    if result.deleted_count == 1:
        return result
    else:
        raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
