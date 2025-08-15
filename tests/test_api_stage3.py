# tests/test_api_stage3.py


import httpx
import respx
from fastapi.testclient import TestClient

# Import FastAPI app from your api.py
from api import app

client = TestClient(app)


def test_openapi_available():
    # We check if the API docs (OpenAPI) is reachable.
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()  # Should contain endpoint paths


def test_get_books_returns_list():
    # GET /books should return 200 and a JSON list.
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@respx.mock
def test_post_books_adds_using_openlibrary_and_then_get_shows_it():
    # We will add a book by ISBN.
    # We mock Open Library responses, so the test does not call the real internet.
    isbn = "9999999999999"

    # Mock book JSON from Open Library
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "API Stage 3 Book",
                "authors": [{"key": "/authors/OL1A"}],
            },
        )
    )
    # Mock author JSON (name)
    respx.get("https://openlibrary.org/authors/OL1A.json").mock(
        return_value=httpx.Response(200, json={"name": "Test Author"})
    )

    # Call POST /books with the ISBN
    rp = client.post("/books", json={"isbn": isbn})
    assert rp.status_code in (200, 201)

    body = rp.json()
    # The API should return the book we added
    assert body["title"] == "API Stage 3 Book"
    assert body["author"] == "Test Author"
    assert body["isbn"] == isbn

    # Now GET /books should show this ISBN in the list
    rg = client.get("/books")
    assert rg.status_code == 200
    items = rg.json()
    assert any(b["isbn"] == isbn for b in items)


@respx.mock
def test_delete_book_then_absent_in_list():
    # Add a book first (also with mocked Open Library)
    isbn = "8888888888888"

    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "Deletable Book",
                "authors": [{"key": "/authors/OL2A"}],
            },
        )
    )
    respx.get("https://openlibrary.org/authors/OL2A.json").mock(
        return_value=httpx.Response(200, json={"name": "Gone Author"})
    )

    # Add via POST
    add_r = client.post("/books", json={"isbn": isbn})
    assert add_r.status_code in (200, 201)

    # Delete via DELETE
    del_r = client.delete(f"/books/{isbn}")
    assert del_r.status_code in (200, 204)

    # After delete, GET /books should not show this ISBN
    rg = client.get("/books")
    assert rg.status_code == 200
    assert not any(b["isbn"] == isbn for b in rg.json())
