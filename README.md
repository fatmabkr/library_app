# 📚 library_app – Python 202 Bootcamp Project ✨

A modular, object-oriented Python application for managing a personal library.  
Developed as part of the **Global AI Hub Python 202 Bootcamp**, this project demonstrates:
1. Object-Oriented Programming (OOP) with **Abstract Base Classes**.
2. Integration with the **Open Library Books API** for data enrichment.
3. Building and serving a REST API with **FastAPI**.

**library_app** evolves from a simple terminal-based book manager into an enriched application 
that integrates external data sources and finally exposes its functionality as a REST API.

## Stage 1 – OOP Terminal Application
- Created `Book` and `Library` classes.
- Defined an `AbstractLibrary` **abstract base class** to enforce a consistent interface.
- Implemented file persistence with `library.json`.

## Stage 2 – External API Integration
- Integrated **Open Library Books API**:
  - Fetches book title and authors by ISBN.
  - Handles missing data and network errors.
- Normalized ISBNs (spaces/dashes removed).
- Prevented duplicate entries.
- Added `httpx` to `requirements.txt`.

## Stage 3 – FastAPI Web Service
- Developed REST endpoints:
  - `GET /books` – List all stored books.
  - `POST /books` – Add book by ISBN (fetch details via API).
  - `DELETE /books/{isbn}` – Remove book by ISBN.
 Create a REST API with **FastAPI**.


## Features
- Abstract Base Class enforcing consistent design.
- Manual & automatic book addition via ISBN.
- ISBN normalization for consistent storage.
- Persistent JSON storage.
- API integration with error handling.
- REST API endpoints using FastAPI.
- Comprehensive test coverage with pytest.
### Data is saved in a **JSON file** so it stays after you close the program.  
Tests are written with **pytest**.

## Project Structure
- library_app/
   * main.py                     # Terminal interface (Stage 1 & 2)
   * api.py                      # FastAPI app (Stage 3)
   * library.json                # Persistent storage (JSON)
   * requirements.txt            # Dependencies
   * pytest.ini                  # Pytest configuration
   *  __init__.py

- models/
   * __init__.py
   * abstract_library.py     # Abstract Base Class
   * book.py                 # Book entity
   * library.py              # Library implementation

- tests/
    * __init__.py
    * test_api_stage3.py              # Tests FastAPI endpoints
    * test_library_add_find.py        # Tests book addition & find
    * test_library_persistence.py     # Tests JSON save/load
    * test_library_remove_list.py     # Tests book removal & list
    * test_openlibrary_api.py         # Tests API integration
    * test_openlibrary_api_extra.py   # Extra API tests
    * test_validation.py              # Tests validation rules

## Installation ✨
- Clone the Repository:
git clone https://github.com/<your-username>/library_app.git
cd library_app

## Create virtual environment & install packages
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt


# Usage ✨
- Terminal Application (Stages 1 & 2)
     python3 main.py
  
## Menu
1) Add Book by ISBN (Auto)
2) Remove Book
3) List Books
4) Find Book
5) Add Book (Manual)
6) Exit
   
#API Server (Stage 3)
uvicorn api:app --reload
API Docs:
Swagger UI → http://127.0.0.1:8000/docs
ReDoc → http://127.0.0.1:8000/redoc

## API Endpoints
-GET /books — Returns all books.
-POST /books — Add book by ISBN.
Example body
{
  "isbn": "978-0321765723"
}
-DELETE /books/{isbn} — Delete a book by ISBN.

# Testing✨
- Run All Tests 
python3 -m pytest -v
Test files:
test_library_add_file.py — Add book
test_library_persistence.py — Save/load JSON
test_library_removal.py — Remove book
test_openlibrary_api_extra.py — API integration
test_api_stage3.py — API endpoints
test_validation.py — Validation rules

# requirements.txt
httpx>=0.27
pytest>=8.0
respx>=0.21
fastapi>=0.115
uvicorn>=0.30
pydantic>=2.8
