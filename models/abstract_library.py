from abc import ABC, abstractmethod
from typing import List, Optional
from models.book import Book
from typing import Optional

class AbstractLibrary(ABC):
    @abstractmethod
    def add_book(self, book: Book) -> bool:
        pass

    @abstractmethod
    def remove_book(self, isbn: str) -> bool:
        pass

    @abstractmethod
    def list_books(self) -> List[Book]:
        pass

    @abstractmethod
    def find_book(self, isbn: str) -> Optional[Book]:
        pass

    @abstractmethod
    def save_books(self) -> None:
        pass

    @abstractmethod
    def load_books(self) -> None:
        pass

    @abstractmethod
    def add_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """Fetch by ISBN from Open Library, add to storage, return Book or None if not found/error."""
        pass
