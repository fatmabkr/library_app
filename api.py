# api.py
from __future__ import annotations

import re
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from models.book import Book
from models.library import Library
import httpx
from fastapi import HTTPException

def fetch_by_isbn_or_search(isbn: str) -> dict:
    base = "https://openlibrary.org"
   
    r = httpx.get(f"{base}/isbn/{isbn}.json", timeout=10)
    if r.status_code == 200:
        return r.json()
    if r.status_code != 404:
        r.raise_for_status()

    sr = httpx.get(f"{base}/search.json", params={"isbn": isbn}, timeout=10)
    sr.raise_for_status()
    doc = sr.json()
    if doc.get("num_found", 0) > 0:
        
        cand = doc["docs"][0].get("isbn", []) or doc["docs"][0].get("isbn13", [])
        for alt in cand:
            rr = httpx.get(f"{base}/isbn/{alt}.json", timeout=10)
            if rr.status_code == 200:
                return rr.json()

    raise HTTPException(status_code=404, detail="Book not found on Open Library.")



#  Small helpers 

def to_dict(book: Book) -> dict:
    """Convert Book object to a simple dict."""
    return {"title": book.title, "author": book.author, "isbn": book.isbn}


def normalize_isbn(text: str) -> str:
    """Remove spaces and symbols, make uppercase."""
    return "".join(ch for ch in text if ch.isalnum()).upper()


# Only numbers or X are allowed in ISBN
ISBN_ALLOWED = re.compile(r"[0-9Xx]+")


def safe_load(lib: Library) -> None:
    """Load books from JSON file using Library.load_books()."""
    try:
        lib.load_books()
    except Exception:
        # If file is missing or broken, ignore for now
        pass


def safe_save(lib: Library) -> None:
    """Save books to JSON file using Library.save_books()."""
    try:
        lib.save_books()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {e}")


# Request / Response models 

class ISBNRequest(BaseModel):
    """Body model for adding a book by ISBN."""
    isbn: str = Field(..., examples=["9780140449266"])


class BookResponse(BaseModel):
    """Response model for a single book."""
    title: str
    author: str
    isbn: str


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


#  Open Library client

async def fetch_openlibrary(isbn: str) -> dict:
    """Get book data from Open Library by ISBN."""
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 404:
                raise HTTPException(status_code=404, detail="Book not found on Open Library.")
            r.raise_for_status()
            book_json = r.json()

            title = book_json.get("title") or "Unknown"

            # Try to read author name
            author_name = "Unknown"
            authors = book_json.get("authors") or []
            author_key = None
            if authors and isinstance(authors[0], dict):
                # Could be {"key": "/authors/OL..."} or {"author": {"key": ...}}
                author_key = authors[0].get("key") or (
                    isinstance(authors[0].get("author"), dict) and authors[0]["author"].get("key")
                )

            if author_key:
                a = await client.get(f"https://openlibrary.org{author_key}.json")
                if a.status_code == 200:
                    author_name = (a.json() or {}).get("name") or "Unknown"

            return {"title": title, "author": author_name, "isbn": isbn}

    except httpx.RequestError as e:
        # Network/DNS/timeout problem
        raise HTTPException(status_code=502, detail=f"Open Library request failed: {e}")
    except httpx.HTTPStatusError as e:
        # Non-2xx from the server
        raise HTTPException(status_code=502, detail=f"Open Library returned error: {e.response.status_code}")


# FastAPI app

app = FastAPI(title="Library API", version="1.0.0")

# Single Library instance kept in memory
library_store = Library()
safe_load(library_store)


#  Endpoints

@app.get("/books", response_model=List[BookResponse])
def list_books() -> List[BookResponse]:
    """Return all saved books."""
    return [BookResponse(**to_dict(b)) for b in library_store.books]


@app.post("/books", response_model=BookResponse, status_code=201)
async def add_book(request: ISBNRequest) -> BookResponse:
    """Add a new book by ISBN (fetch from Open Library)."""
    raw = request.isbn.strip()
    if not raw:
        raise HTTPException(status_code=400, detail="ISBN cannot be empty.")

    normalized = normalize_isbn(raw)
    if not ISBN_ALLOWED.fullmatch(normalized):
        raise HTTPException(status_code=422, detail="Invalid ISBN format.")

    # Get book info from Open Library
    data = await fetch_openlibrary(normalized)

    # Add to library (dedupe by ISBN)
    new_book = Book(title=data["title"], author=data["author"], isbn=data["isbn"])
    added = library_store.add_book(new_book)
    if not added:
        raise HTTPException(status_code=409, detail="This ISBN already exists.")

    # Save to file
    safe_save(library_store)
    return BookResponse(**data)


@app.delete("/books/{isbn}", response_model=MessageResponse)
def delete_book(isbn: str) -> MessageResponse:
    """Delete a book by ISBN."""
    normalized = normalize_isbn(isbn)

    removed = library_store.remove_book(normalized)
    if not removed:
        raise HTTPException(status_code=404, detail="Book to delete not found.")

    # Save to file
    safe_save(library_store)
    return MessageResponse(message=f"{normalized} deleted.")
