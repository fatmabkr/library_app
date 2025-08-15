from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional
import httpx

from .abstract_library import AbstractLibrary
from .book import Book

OPENLIB_BASE = "https://openlibrary.org"
HTTP_TIMEOUT = 5.0
HTTP_HEADERS = {
    "User-Agent": "library_app/1.0",
    "Accept": "application/json",
}

def _safe_get_json(url: str) -> Optional[dict]:
    try:
        r = httpx.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT, follow_redirects=True)
    except httpx.RequestError:
        return None
    if r.status_code == 404:
        return None
    try:
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPStatusError, ValueError):
        return None

def _join_authors(names: List[str]) -> str:
    return ", ".join(n for n in names if n) if names else ""

class Library(AbstractLibrary):
    def __init__(self, storage_file: str = "library.json") -> None:
        self.storage_path = Path(storage_file)
        self._books: List[Book] = []
        self._ensure_file()
        self.load_books()

    @property
    def books(self) -> List[Book]:
        return self._books

    @staticmethod
    def _norm_isbn(s: str) -> str:
        s = (s or "").strip()
        digits = [ch for ch in s if ch.isdigit()]
        if s.upper().endswith("X"):
            digits.append("X")
        return "".join(digits)

    def _ensure_file(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]", encoding="utf-8")

    def load_books(self) -> None:
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "[]")
        except Exception:
            raw = []
        out: List[Book] = []
        for item in raw if isinstance(raw, list) else []:
            try:
                if hasattr(Book, "from_dict"):
                    b = Book.from_dict(item)  # type: ignore[attr-defined]
                else:
                    b = Book(
                        title=item.get("title", ""),
                        author=item.get("author", ""),
                        isbn=item.get("isbn", ""),
                    )
                b = Book(title=b.title, author=b.author, isbn=self._norm_isbn(b.isbn))
                out.append(b)
            except Exception:
                pass
        self._books = out

    def save_books(self) -> None:
        data = []
        for b in self._books:
            if hasattr(b, "to_dict"):
                data.append(b.to_dict())  # type: ignore[attr-defined]
            else:
                data.append({"title": b.title, "author": b.author, "isbn": b.isbn})
        self.storage_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_books(self) -> List[Book]:
        return list(self._books)

    def find_book(self, isbn: str) -> Optional[Book]:
        n = self._norm_isbn(isbn)
        return next((b for b in self._books if self._norm_isbn(b.isbn) == n), None)

    def add_book(self, book: Book) -> bool:
        n = self._norm_isbn(book.isbn)
        if not n or self.find_book(n):
            return False
        clean = Book(title=book.title.strip(), author=book.author.strip(), isbn=n)
        self._books.append(clean)
        self.save_books()
        return True

    def remove_book(self, isbn: str) -> bool:
        n = self._norm_isbn(isbn)
        if not n:
            return False
        before = len(self._books)
        self._books = [b for b in self._books if self._norm_isbn(b.isbn) != n]
        removed = len(self._books) != before
        if removed:
            self.save_books()
        return removed

    def add_book_by_isbn(self, isbn: str) -> bool:
        n = self._norm_isbn(isbn)
        if not n or self.find_book(n):
            return False
        book_json = _safe_get_json(f"{OPENLIB_BASE}/isbn/{n}.json")
        if not book_json:
            return False
        title = (book_json.get("title") or "").strip()
        if not title:
            return False
        names: List[str] = []
        alist = book_json.get("authors")
        if isinstance(alist, list):
            for a in alist:
                key = (a or {}).get("key") or (a.get("author") or {}).get("key")
                if not key:
                    continue
                ajson = _safe_get_json(f"{OPENLIB_BASE}{key}.json")
                if ajson and ajson.get("name"):
                    names.append(str(ajson["name"]).strip())
        if not names:
            by_stmt = (book_json.get("by_statement") or "").strip()
            if by_stmt:
                names = [by_stmt.split(";")[0]]
        author = _join_authors(names) or "Unknown Author"
        return self.add_book(Book(title=title, author=author, isbn=n))
