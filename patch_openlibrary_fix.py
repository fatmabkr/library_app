import re, sys, pathlib

p = pathlib.Path("models/library.py")
src = p.read_text(encoding="utf-8")

if "import httpx" not in src:
    src = re.sub(r"^(from\b[^\n]*\n|import\b[^\n]*\n)+",
                 lambda m: m.group(0) + "import httpx\nfrom typing import List, Optional\n",
                 src, count=1, flags=re.M)

helpers = """
OPENLIB_BASE = "https://openlibrary.org"

def _safe_get_json(url: str) -> Optional[dict]:
    try:
        resp = httpx.get(url, timeout=10)
    except httpx.RequestError:
        return None
    if resp.status_code == 404:
        return None
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        return None
    try:
        return resp.json()
    except ValueError:
        return None

def _join_authors(authors: List[str]) -> str:
    return ", ".join([a for a in authors if a]) if authors else ""
""".strip() + "\n"

if "OPENLIB_BASE = " not in src:
    src = re.sub(r"\n(class\s+Library\b)",
                 "\n" + helpers + r"\n\1",
                 src, count=1, flags=re.S)

new_method = r'''
    def add_book_by_isbn(self, isbn: str) -> bool:
        norm = self._norm_isbn(isbn)
        if not norm or len(norm) < 4:
            return False
        if self.find_book(norm) is not None:
            return False
        book_json = _safe_get_json(f"{OPENLIB_BASE}/isbn/{norm}.json")
        if not book_json:
            return False
        title = (book_json.get("title") or "").strip()
        authors_out: List[str] = []
        alist = book_json.get("authors")
        if isinstance(alist, list):
            for a in alist:
                key = (a or {}).get("key")
                if not key:
                    continue
                ajson = _safe_get_json(f"{OPENLIB_BASE}{key}.json")
                if ajson and ajson.get("name"):
                    authors_out.append(str(ajson["name"]).strip())
        if not authors_out:
            by_stmt = book_json.get("by_statement")
            if by_stmt:
                authors_out.append(str(by_stmt).strip())
        author_final = _join_authors(authors_out) or "Unknown"
        if not title:
            return False
        new_book = Book(title=title, author=author_final, isbn=norm)
        self.add_book(new_book)
        return True
'''.strip("\n")

pattern = re.compile(
    r"(class\s+Library\b.*?)(\n\s*def\s+add_book_by_isbn\s*\([^\)]*\)\s*:[\s\S]*?)(\n\s*def\s+|\n\s*@|\n\s*#|$)",
    re.S
)
m = pattern.search(src)
if not m:
    print("add_book_by_isbn bulunamadı", file=sys.stderr)
    sys.exit(1)

indent = re.search(r"\n(\s*)def\s+add_book_by_isbn", m.group(2)).group(1)
indented_new = "\n" + "\n".join((indent + line if line.strip() else line) for line in new_method.splitlines()) + "\n"
src = src[:m.start(2)] + indented_new + src[m.start(3):]

p.write_text(src, encoding="utf-8")
print("models/library.py güncellendi.")
