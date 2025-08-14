import json
from pathlib import Path

import httpx
import respx

from models.library import Library


@respx.mock
def test_add_by_isbn_success(tmp_path: Path):
    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    # Turkish edition (Metis)
    isbn = "9789753424080"

    # Mock book endpoint (Open Library)
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "Sana Gül Bahçesi Vadetmedim",
                "authors": [{"key": "/authors/OL12345A"}],  
            },
        )
    )
    # Mock author endpoint
    respx.get("https://openlibrary.org/authors/OL12345A.json").mock(
        return_value=httpx.Response(200, json={"name": "Joanne Greenberg"})
    )

    added = lib.add_book_by_isbn(isbn)
    assert added is not None
    assert added.title == "Sana Gül Bahçesi Vadetmedim"
    assert "Joanne Greenberg" in added.author

    data = json.loads(storage.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["isbn"] == isbn


@respx.mock
def test_add_by_isbn_not_found(tmp_path: Path):
    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    bad = "0000000000000"
    respx.get(f"https://openlibrary.org/isbn/{bad}.json").mock(
        return_value=httpx.Response(404)
    )

    added = lib.add_book_by_isbn(bad)
    assert added is None


@respx.mock
def test_add_by_isbn_network_error(tmp_path: Path):
    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    isbn = "9789753424080"
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        side_effect=httpx.ConnectError("boom")
    )

    added = lib.add_book_by_isbn(isbn)
    assert added is None


def test_manual_add_normalizes_and_dedups(tmp_path: Path):
    from models.book import Book

    storage = tmp_path / "lib.json"
    lib = Library(str(storage))

    ok = lib.add_book(Book("X", "Y", "978-975-342-4080"))
    assert ok is True

    # Aynı ISBN farklı formatta: eklenmemeli
    ok2 = lib.add_book(Book("X2", "Y2", "978 9753424080"))
    assert ok2 is False

    # Her formatla bulunabilmeli
    found = lib.find_book("978 975 342 4080")
    assert found is not None
    assert found.title == "X"
