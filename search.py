"""Keyword search over the ArchiveLens SQLite database."""
import re
import sqlite3


def to_fts_query(text):
    """Keep only words, quote each one, and use prefix matching (snow* matches snowstorm)."""
    words = re.findall(r"\w+", text.lower())
    return " ".join(f'"{w}"*' for w in words)


def search_archive(db_path, query, limit=5):
    fts_query = to_fts_query(query)
    if not fts_query:
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT d.id, d.source, d.date, d.category,
                  snippet(documents_fts, 1, '[', ']', '...', 12) AS snippet,
                  round(-bm25(documents_fts), 3) AS relevance
           FROM documents_fts JOIN documents d ON d.id = documents_fts.rowid
           WHERE documents_fts MATCH ?
           ORDER BY bm25(documents_fts)
           LIMIT ?""",
        (fts_query, limit),
    ).fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    for r in results:
        r["snippet"] = " ".join(r["snippet"].split())                 # tidy line breaks
    return results


def get_document(db_path, doc_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
