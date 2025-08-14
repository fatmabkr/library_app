from models.library import Library
from models.book import Book

def test_remove(tmp_path):
    storage = tmp_path / "remove.json"
    lib = Library(str(storage))

    # Add and then remove a book
    lib.add_book(Book("Thus Spoke Zarathustra", "Friedrich Nietzsche", "3333"))
    assert lib.remove_book("3333") is True

    # Removing again should return False
    assert lib.remove_book("3333") is False
