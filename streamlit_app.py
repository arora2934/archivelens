"""ArchiveLens web app: a simple search page for the archive.

Run it with:  streamlit run streamlit_app.py
"""
import os
import sqlite3

import pandas as pd
import streamlit as st

from search import search_archive

DB_PATH = "archivelens.db"

# ---------- Page title ----------
st.set_page_config(page_title="ArchiveLens", page_icon="🔎", layout="wide")
st.title("🔎 ArchiveLens")
st.write("Search old scanned newspaper pages. The pages were read with OCR and stored in a searchable database.")
st.caption("All documents are fictional samples created for this project.")

# ---------- Three quick numbers ----------
col1, col2, col3 = st.columns(3)
col1.metric("Scanned pages", "5")
col2.metric("OCR error before cleaning", "14.1%")
col3.metric("OCR error after cleaning", "3.5%", "-10.6 points", delta_color="inverse")

tab_search, tab_ocr, tab_all = st.tabs(["🔎 Search", "📊 OCR results", "📚 All documents"])

# ---------- Tab 1: Search ----------
with tab_search:
    query = st.text_input("Type a word to search", placeholder="Try: steamer, snow, books, fish prices")
    if query:
        results = search_archive(DB_PATH, query, limit=5)
        st.write(f"**{len(results)} result(s)** for '{query}'")
        if not results:
            st.info("No pages found. Try another word.")
        for r in results:
            with st.container(border=True):
                st.subheader(f"{r['source']} ({r['date']})")
                st.write(f"Category: {r['category']}  |  Relevance: {r['relevance']}")
                st.write(r["snippet"])
                with st.expander("Show the scanned page and the full OCR text"):
                    conn = sqlite3.connect(DB_PATH)
                    row = conn.execute(
                        "SELECT image_path, ocr_text FROM documents WHERE id = ?", (r["id"],)
                    ).fetchone()
                    conn.close()
                    left, right = st.columns(2)
                    left.image(os.path.basename(row[0]), caption="Scanned page")
                    right.text(row[1])

# ---------- Tab 2: OCR results ----------
with tab_ocr:
    st.write("How accurate was OCR? Lower Character Error Rate (CER) is better.")
    st.dataframe(pd.read_csv("ocr_results.csv"), hide_index=True)
    st.image("cleaning_example.png", caption="Image cleaning with OpenCV on the most damaged page")

# ---------- Tab 3: All documents ----------
with tab_all:
    conn = sqlite3.connect(DB_PATH)
    docs = pd.read_sql("SELECT id, source, date, category, word_count FROM documents", conn)
    conn.close()
    st.dataframe(docs, hide_index=True)
    st.image("sample_pages.png", caption="The 5 sample pages")
