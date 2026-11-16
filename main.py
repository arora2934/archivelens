"""ArchiveLens API: search a small OCR-processed archive."""
from fastapi import FastAPI, HTTPException, Query

from search import get_document, search_archive

DB_PATH = "archivelens.db"
app = FastAPI(title="ArchiveLens API", description="Search OCR text from scanned archive pages.")


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    results = search_archive(DB_PATH, q, limit)
    return {"query": q, "count": len(results), "results": results}


@app.get("/documents/{doc_id}")
def document(doc_id: int):
    doc = get_document(DB_PATH, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
