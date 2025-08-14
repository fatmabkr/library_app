import pytest
from models.book import Book
from models.library import Library

def test_book_validation_errors():
    # Title cannot be empty
    with pytest.raises(ValueError):
        Book("", "Jack London", "1111")

    # Author cannot be empty or whitespace
    with pytest.raises(ValueError):
        Book("Martin Eden", "   ", "1111")

    # ISBN must be at least 4 characters long
    with pytest.raises(ValueError):
        Book("Martin Eden", "Jack London", "123")

def test_duplicate_isbn(tmp_path):
    # Create a temporary JSON file for testing
    storage = tmp_path / "dup.json"
    lib = Library(str(storage))

    # First add should succeed
    assert lib.add_book(Book("A Room of One's Own", "Virginia Woolf", "2222")) is True
    # Adding another book with the same ISBN should fail
    assert lib.add_book(Book("Different Title", "Different Author", "2222")) is False

    # There should still be only one book in the library
    books = lib.list_books()
    assert len(books) == 1

    # The book with ISBN "2222" should be the first one we added
    found = lib.find_book("2222")
    assert found is not None
    assert found.title == "A Room of One's Own"
