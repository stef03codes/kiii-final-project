from typing import Optional
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

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
collection = db["books"]

class Book(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None

class BookInDB(Book):
    id: str

def book_helper(book) -> dict:
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "isbn": book.get("isbn")
    }

@app.get("/books", response_model=list[BookInDB])
async def get_books():
    books = await collection.find().to_list(100)
    return [book_helper(book) for book in books]

@app.post("/books/add", response_model=BookInDB)
async def add_book(book: Book):
    result = await collection.insert_one(book.model_dump())
    new_book = await collection.find_one({"_id": result.inserted_id})
    return book_helper(new_book)

@app.delete("/books/delete/{book_id}")
async def delete_book(book_id: str):
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
