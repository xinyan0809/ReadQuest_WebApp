import requests

def search_books(query):
    response = requests.get(
        "https://openlibrary.org/search.json",
        params={
            "q": query,
            "fields": "key,title,author_name,cover_i,number_of_pages_median,first_publish_year",
            "limit": 10
        }
    )
    response.raise_for_status()

    books = []
    
    for doc in response.json().get("docs", []):
        cover_image = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg" if doc.get("cover_i") else None
        books.append({
            "ol_key": doc.get("key", ""),
            "title": doc.get("title", "Unknown Title"),
            "author": ", ".join(doc.get("author_name", ["Unknown Author"])),
            "pages": doc.get("number_of_pages_median") or 0,
            "year": doc.get("first_publish_year", None),
            "cover_image": cover_image,
        })
    return books