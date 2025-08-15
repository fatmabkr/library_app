"""
Stage 3 (FastAPI) tests – B1 English comments.
We test OpenAPI, GET/POST/DELETE, and POST uses Open Library (mocked).
"""
import httpx
import respx
from fastapi.testclient import TestClient
from api import app  # import FastAPI app

client = TestClient(app)

def test_smoke():
    # Simple sanity check so pytest sees at least one test.
    assert True

def test_openapi_available():
    # OpenAPI spec should be reachable.
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()

def test_get_books_returns_list():
    # GET /books returns 200 and a JSON list.
    r = client.get("/books")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@respx.mock
def test_post_books_adds_using_openlibrary_and_then_get_shows_it():
    # Add a new book with a fresh ISBN (mocked Open Library).
    isbn = "9999999999999"
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(200, json={
            "title": "API Stage 3 Book",
            "authors": [{"key": "/authors/OL1A"}],
        })
    )
    respx.get("https://openlibrary.org/authors/OL1A.json").mock(
        return_value=httpx.Response(200, json={"name": "Test Author"})
    )
    rp = client.post("/books", json={"isbn": isbn})
    assert rp.status_code in (200, 201)
    body = rp.json()
    assert body["title"] == "API Stage 3 Book"
    assert body["author"] == "Test Author"
    assert body["isbn"] == isbn

    rg = client.get("/books")
    assert rg.status_code == 200
    assert any(b["isbn"] == isbn for b in rg.json())

@respx.mock
def test_delete_book_then_absent_in_list():
    # Add then delete (all mocked).
    isbn = "8888888888888"
    respx.get(f"https://openlibrary.org/isbn/{isbn}.json").mock(
        return_value=httpx.Response(200, json={
            "title": "Deletable Book",
            "authors": [{"key": "/authors/OL2A"}],
        })
    )
    respx.get("https://openlibrary.org/authors/OL2A.json").mock(
        return_value=httpx.Response(200, json={"name": "Gone Author"})
    )
    add_r = client.post("/books", json={"isbn": isbn})
    assert add_r.status_code in (200, 201)

    del_r = client.delete(f"/books/{isbn}")
    assert del_r.status_code in (200, 204)

    rg = client.get("/books")
    assert rg.status_code == 200
    assert not any(b["isbn"] == isbn for b in rg.json())
