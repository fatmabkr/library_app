# 📚 library_app – Python 202 Bootcamp Project

A modular, object-oriented Python application for managing a personal library.  
Developed as part of the **Global AI Hub Python 202 Bootcamp**, this project demonstrates:
1. Object-Oriented Programming (OOP) with **Abstract Base Classes**.
2. Integration with the **Open Library Books API** for data enrichment.
3. Building and serving a REST API with **FastAPI**.

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [Project Goals](#project-goals)
3. [Stages Overview](#stages-overview)
4. [Abstract Base Class Design](#abstract-base-class-design)
5. [Features](#features)
6. [Installation](#installation)
7. [Project Structure](#project-structure)
8. [Usage](#usage)
9. [Testing](#testing)
10. [API Documentation (Stage 3)](#api-documentation-stage-3)
11. [Future Improvements](#future-improvements)

---

## 📌 Introduction
**library_app** evolves from a simple terminal-based book manager into an enriched application that integrates external data sources and finally exposes its functionality as a REST API.

The project emphasizes:
- **Clean architecture** and code reusability.
- **Persistent storage** using JSON.
- **Robust testing** with `pytest`.
- **API-driven development**.

---

## 🎯 Project Goals
- Implement **OOP principles** using an **Abstract Base Class** to enforce method contracts.
- Provide core library operations: add, remove, list, find books.
- Enrich data automatically using **Open Library Books API**.
- Expose all operations through a **FastAPI**-powered REST API.

---

## 🛠 Stages Overview

### **Stage 1 – OOP Terminal Application**
- Created `Book` and `Library` classes.
- Defined an `AbstractLibrary` **abstract base class** to enforce a consistent interface for all library implementations.
- Implemented file persistence with `library.json`.

### **Stage 2 – External API Integration**
- Integrated **Open Library Books API**:
  - Fetches book title and authors by ISBN.
  - Handles missing data and network errors.
- Normalized ISBNs (spaces/dashes removed).
- Prevented duplicate entries.
- Added `httpx` to `requirements.txt`.

### **Stage 3 – FastAPI Web Service**
- Developed REST endpoints:
  - `GET /books` – Return all stored books.
  - `POST /books` – Add book by ISBN (fetching details via API).
  - `DELETE /books/{isbn}` – Remove book by ISBN.
- Used **Pydantic** models for request/response validation.
- Hosted with `uvicorn`.

---

## 🧩 Abstract Base Class Design
The **`AbstractLibrary`** class in `models/abstract_library.py` defines the *contract* for any library implementation.  
It ensures the following methods are implemented:

```python
@abstractmethod
def add_book(self, book: Book) -> bool: pass

@abstractmethod
def remove_book(self, isbn: str) -> bool: pass

@abstractmethod
def list_books(self) -> List[Book]: pass

@abstractmethod
def find_book(self, isbn: str) -> Optional[Book]: pass

@abstractmethod
def save_books(self) -> None: pass

@abstractmethod
def load_books(self) -> None: pass

@abstractmethod
def add_book_by_isbn(self, isbn: str) -> Optional[Book]: pass
This design:
Guarantees that all required operations are available in any subclass.
Improves code maintainability and scalability.
Allows for easy future replacement of the storage backend (e.g., switch from JSON to SQL).
✨ Features
Abstract Base Class enforcing consistent design.
Manual and automatic book addition via ISBN.
ISBN normalization for consistent storage.
Persistent JSON storage.
API integration with error handling.
REST API endpoints using FastAPI.
Comprehensive test coverage with pytest.
📥 Installation
1. Clone the Repository
git clone https://github.com/<your-username>/library_app.git
cd library_app
2. Install Dependencies
python3 -m pip install -r requirements.txt
📂 Project Structure
library_app/
├── main.py                 # Terminal interface (Stage 1 & 2)
├── api.py                  # FastAPI app (Stage 3)
├── library.json            # Persistent storage
├── requirements.txt        # Dependencies
├── pytest.ini              # Pytest config
├── __init__.py
│
├── models/
│   ├── abstract_library.py # Abstract Base Class
│   ├── book.py             # Book entity
│   └── library.py          # Library implementation
│
└── tests/
    ├── test_library_add_file.py       # Tests book addition
    ├── test_library_persistence.py    # Tests JSON persistence
    ├── test_library_removal.py        # Tests book removal
    ├── test_openlibrary_api_extra.py  # Tests API integration
    ├── test_validation.py             # Tests input validation
💻 Usage
Terminal Application (Stages 1 & 2)
python3 main.py
Menu:
1) Add Book by ISBN (Auto)
2) Remove Book
3) List Books
4) Find Book
5) Add Book (Manual)
6) Exit
API Server (Stage 3)
uvicorn api:app --reload
Then open:
http://127.0.0.1:8000/docs
🧪 Testing
Run All Tests
python3 -m pytest -v
Test Coverage:
test_library_add_file.py → Verifies book addition logic.
test_library_persistence.py → Confirms JSON read/write works.
test_library_removal.py → Ensures books can be removed.
test_openlibrary_api_extra.py → Tests API fetching logic.
test_validation.py → Checks validation rules.
📜 API Documentation (Stage 3)
POST /books
Request body:
{
  "isbn": "9780140449112"
}
Response (success):
{
  "title": "The Odyssey",
  "author": "Όμηρος",
  "isbn": "9780140449112"
}
🚀 Future Improvements
ISBN-10 to ISBN-13 conversion.
SQLite or PostgreSQL backend.
PUT endpoint for updating book details.
Frontend consuming the API.
Docker containerization.

