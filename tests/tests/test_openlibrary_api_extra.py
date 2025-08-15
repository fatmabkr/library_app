import httpx
import respx
from pathlib import Path

from models.library import Library


@respx.mock
def test_add_by_isbn_multiple_authors_join(tmp_path: Path):
    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    isbn = "1111111111111"

    # Book JSON with two authors
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "Multi Author Book",
                "authors": [
                    {"key": "/authors/OL1A"},
                    {"key": "/authors/OL2A"},
                ],
            },
        )
    )
    # Author 1
    respx.get("https://openlibrary.org/authors/OL1A.json").mock(
        return_value=httpx.Response(200, json={"name": "Author One"})
    )
    # Author 2
    respx.get("https://openlibrary.org/authors/OL2A.json").mock(
        return_value=httpx.Response(200, json={"name": "Author Two"})
    )

    added = lib.add_book_by_isbn(isbn)
    assert added is not None
    # Should contain both names joined by comma (order preserved by loop)
    assert added.author == "Author One, Author Two"


@respx.mock
def test_add_by_isbn_by_statement_fallback(tmp_path: Path):
    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    isbn = "2222222222222"

    # No authors array, use by_statement
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "By Statement Only",
                "by_statement": "Somebody Famous",
                "authors": [],  # empty
            },
        )
    )

    added = lib.add_book_by_isbn(isbn)
    assert added is not None
    assert added.title == "By Statement Only"
    assert added.author == "Somebody Famous"
