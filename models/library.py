import json
from pathlib import Path
from typing import List, Optional
import httpx  # HTTP client for Open Library API

from models.book import Book
from models.abstract_library import AbstractLibrary


class Library(AbstractLibrary):
    
    # Headers for HTTP requests
    _HTTP_HEADERS = {
        "User-Agent": "LibraryApp/1.0 (+https://example.local)",
        "Accept": "application/json",
    }

    def __init__(self, storage_file: str = "library.json") -> None:
        self.storage_path = Path(storage_file)
        self.books: List[Book] = []
        self._ensure_file()
        self.load_books()

    # Helpers 
    def _ensure_file(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]", encoding="utf-8")

    @staticmethod
    def _norm_isbn(s: str) -> str:
        #Remove spaces and dashes from ISBN
        return "".join(ch for ch in s.strip().replace(" ", "") if ch != "-")

    # File operations 
    def load_books(self) -> None:
        #Read JSON file and load it into the books list
        try:
            text = self.storage_path.read_text(encoding="utf-8") or "[]"
            data = json.loads(text)
            if not isinstance(data, list):
                data = []
            self.books = [Book.from_dict(item) for item in data]
        except Exception:
            # If file is broken, reset to empty
            self.books = []
            self.save_books()
        for b in self.books:
             b.isbn = self._norm_isbn(b.isbn)


    def save_books(self) -> None:
        #Save books list to JSON file
        data = [b.to_dict() for b in self.books]
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_book(self, book: Book) -> bool:
        # Always normalize and deduplicate by normalized ISBN
        clean = self._norm_isbn(book.isbn)
        if self.find_book(clean) is not None:
            return False
        book.isbn = clean
        self.books.append(book)
        self.save_books()
        return True



    def list_books(self) -> List[Book]:
        #return a copy of the books list
        return list(self.books)
    


    def find_book(self, isbn: str) -> Optional[Book]:
        # Compare with normalized ISBNs
        n = self._norm_isbn(isbn)
        return next((b for b in self.books if self._norm_isbn(b.isbn) == n), None)



    def remove_book(self, isbn: str) -> bool:
        # Remove using normalized ISBN
        n = self._norm_isbn(isbn)
        before = len(self.books)
        self.books = [b for b in self.books if self._norm_isbn(b.isbn) != n]
        if len(self.books) < before:
            self.save_books()
            return True
        return False


    #  Stage 2: Add by ISBN from Open Library 
    def add_book_by_isbn(self, isbn: str) -> Optional[Book]:
       
        clean_isbn = self._norm_isbn(isbn)

        # If the book is already in the list, return it
        existing = self.find_book(clean_isbn)
        if existing:
            return existing

        try:
            data = self.fetch_book_from_openlibrary(clean_isbn)
            if data is None:
                return None

            # Get title
            title = (data.get("title") or "Unknown Title").strip()

            # Get authors (handle different data formats)
            author_names: List[str] = []
            for a in (data.get("authors") or []):
                key = (
                    a.get("key")
                    or (a.get("author") or {}).get("key")
                )
                if key:
                    name = self._fetch_author_name(key)
                    if name:
                        author_names.append(name)

            # If authors are empty, try by_statement
            if not author_names:
                by_stmt = (data.get("by_statement") or "").strip()
                if by_stmt:
                    author_names = [by_stmt.split(";")[0]]

            author = (", ".join(author_names) if author_names else "Unknown Author").strip()

            # Create the book and add it
            new_book = Book(title=title, author=author, isbn=clean_isbn)
            if self.add_book(new_book):
                return new_book
            return self.find_book(clean_isbn)

        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            return None

    # Open Library helpers 
    def fetch_book_from_openlibrary(self, isbn: str) -> Optional[dict]:
        #Fetch book data by ISBN from Open Library
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        try:
            resp = httpx.get(
                url,
                headers=self._HTTP_HEADERS,
                timeout=10.0,
                follow_redirects=True,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            return None

    def _fetch_author_name(self, author_key: str) -> Optional[str]:
        # Fetch author name from Open Library
        if not author_key.startswith("/authors/"):
            return None

        url = f"https://openlibrary.org{author_key}.json"
        try:
            resp = httpx.get(
                url,
                headers=self._HTTP_HEADERS,
                timeout=10.0,
                follow_redirects=True,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            name = (data.get("name") or "").strip()
            return name or None
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            return None
