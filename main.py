from models.book import Book
from models.library import Library


def menu():
    print(" \n----  LIBRARY MENU  ---- ")
    print(" 1) Add Book by ISBN (Auto)")
    print(" 2) Remove Book ")
    print(" 3) ListBooks ")
    print(" 4) Find Book ")
    print(" 5) Add Book (Manual) ")
    print(" 6) Exit ")


def main():
    # Create a Library object and connect it to the "library.json" file
    lib = Library("library.json")

    # This loop will keep showing the menu until the user chooses Exit
    while True:
        menu()
        choice = input("Your choice : ").strip()

        if choice == "1":
            isbn = input("ISBN: ").strip()
            book = lib.add_book_by_isbn(isbn)
            if book:
                print(f"✅ Added: {book}")
            else:
                print("❗ Book not found or network error.")


        elif choice == "2":
            isbn = input(" ISBN to remove : ").strip()
            ok = lib.remove_book(isbn)
            print("Book removed." if ok else "ISBN Not Found.")

        elif choice == "3":
            books = lib.list_books()
            if not books:
                print("No books in the library :(")
            else:
                for bookItem in books:
                    print(bookItem)

        elif choice == "4":
            isbn = input(" ISBN to search: ").strip()
            book = lib.find_book(isbn)
            print(book if book else "Book not found.")

        elif choice == "5":
            try:
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                isbn = input("ISBN: ").strip()
                added = lib.add_book(Book(title, author, isbn))
                print("Book added." if added else "This ISBN already exists.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "6":
            print("GoodBye :)")
            break


        else:
            # If the user writes sth not in 1-6
            print("Invalid choice, please try again.")



# This part starts the program only if we run this file directly
if __name__ == "__main__":
    main()
