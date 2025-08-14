from models.library import Library
from models.book import Book

def test_add_and_find(tmp_path):
    storage = tmp_path / "add_find.json"
    lib = Library(str(storage))

    # Add one book
    b = Book("Martin Eden", "Jack London", "1111")
    assert lib.add_book(b) is True

    # Cannot add the same ISBN again
    assert lib.add_book(Book("Martin Eden", "Jack London", "1111")) is False

    # Find by ISBN
    found = lib.find_book("1111")
    assert found is not None
    assert found.title == "Martin Eden"

    # Not found case
    assert lib.find_book("9999") is None
