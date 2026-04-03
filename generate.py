import pandas as pd
import json, re, os

df = pd.read_csv("books.csv")

books = []
for _, row in df.iterrows():
    isbn = str(row.get("ISBN/UID", "")).strip()
    if isbn in ["nan", "None", ""]:
        isbn = ""
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    cover = (
        f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-M.jpg"
        if isbn_clean and len(isbn_clean) >= 10 else ""
    )

    def clean(val):
        s = str(val)
        return "" if s == "nan" else s

    last_read = clean(row.get("Last Date Read", ""))
    year = last_read[:4] if last_read and last_read[:4].isdigit() else ""

    books.append({
        "t": clean(row.get("Title", "")),
        "a": clean(row.get("Authors", "")),
        "c": cover,
        "r": clean(row.get("Star Rating", "")),
        "s": clean(row.get("Read Status", "")),
        "g": clean(row.get("Tags", "")),
        "f": clean(row.get("Format", "")),
        "y": year,
        "date_read": last_read,
        "isbn": isbn_clean,
    })

books_json = json.dumps(books, ensure_ascii=False)

by_year = {}
top_authors = {}
for b in books:
    if b["s"] == "read" and b["y"]:
        by_year[b["y"]] = by_year.get(b["y"], 0) + 1
    if b["s"] == "read" and b["a"]:
        for a in b["a"].split(","):
            a = a.strip()
            if a and len(a) > 2:
                top_authors[a] = top_authors.get(a, 0) + 1

by_year_json = json.dumps(sorted(by_year.items()), ensure_ascii=False)
top_authors_json = json.dumps(sorted(top_authors.items(), key=lambda x: -x[1])[:12], ensure_ascii=False)
years = sorted(set(b["y"] for b in books if b["y"]))

# Read the current index.html template (itself) and replace the BOOKS data
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace BOOKS array
html = re.sub(r'const BOOKS = \[.*?\];', f'const BOOKS = {books_json};', html, flags=re.DOTALL)
html = re.sub(r'const BY_YEAR_DATA = \[.*?\];', f'const BY_YEAR_DATA = {by_year_json};', html, flags=re.DOTALL)
html = re.sub(r'const TOP_AUTHORS_DATA = \[.*?\];', f'const TOP_AUTHORS_DATA = {top_authors_json};', html, flags=re.DOTALL)

# Update year options in selects
def rebuild_year_options(html, years):
    opts = '\n'.join(f'        <option value="{y}">{y}</option>' for y in years)
    # Replace between the two fixed markers
    html = re.sub(
        r'(<option value="">Toutes les années</option>\n)(.*?)(\n      </select>)',
        lambda m: m.group(1) + opts + m.group(3),
        html, flags=re.DOTALL
    )
    return html

html = rebuild_year_options(html, years)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ index.html mis à jour avec {len(books)} livres depuis books.csv")
