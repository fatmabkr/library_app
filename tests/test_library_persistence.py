from models.library import Library
from models.book import Book

def test_persistence(tmp_path):
    storage = tmp_path / "persist.json"

    # First library instance: add books and save
    lib1 = Library(str(storage))
    lib1.add_book(Book("Martin Eden", "Jack London", "1111"))
    lib1.add_book(Book("A Room of One's Own", "Virginia Woolf", "2222"))

    # Create a new library instance using the same file
    lib2 = Library(str(storage))

    # The books should still be there
    books = lib2.list_books()
    isbns = {b.isbn for b in books}
    assert "1111" in isbns
    assert "2222" in isbns
