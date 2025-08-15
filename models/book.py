from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    isbn: str  # unique id
    
    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty.")
        if not self.author.strip():
            raise ValueError("Author cannot be empty.")
        if not self.isbn.strip() or len(self.isbn.strip()) < 4:
            raise ValueError("ISBN must be at least 4 characters long.")


 # _ _str_ _ method tells Python how to show the book as text when we use print()
 # "self" means " "this object itself" . It lets us access the attributes of the current object
    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
# f - string allows us to easily put variables into a string

    def to_dict(self) -> dict: #This method changes the Book object into a Python dictionary - key value pairs
 #This is useful when saving data to a Json file.
        return {"title": self.title, "author": self.author, "isbn": self.isbn}

    @classmethod # This method creates a new Book object from a dictionary -useful when reading from JSON
    def from_dict(cls, data: dict) -> "Book":
        return cls(title=data["title"], author=data["author"], isbn=data["isbn"])
