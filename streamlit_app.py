"""ArchiveLens: a simple web app to search old scanned pages.

Run it with:  streamlit run streamlit_app.py
"""
import os
import sqlite3

import pandas as pd
import streamlit as st

from search import search_archive

DB_PATH = "archivelens.db"

# ---------- Page setup ----------
st.set_page_config(page_title="ArchiveLens", page_icon="📜", layout="wide")

# ---------- Sidebar: about the project ----------
with st.sidebar:
    st.header("📜 About")
    st.write("ArchiveLens turns scanned pages into searchable text.")
    st.markdown("**How it works**")
    st.markdown(
        "1. 🖼️ Clean the scan with OpenCV\n"
        "2. 🔤 Read the text with OCR (Tesseract)\n"
        "3. 🗂️ Save it in a SQLite database\n"
        "4. 🔎 Search it by keyword"
    )
    st.divider()
    st.markdown("**Built by Arora Abir**")
    st.caption("Master of Artificial Intelligence, Memorial University of Newfoundland")
    st.markdown("[GitHub](https://github.com/arora2934/archivelens) · [LinkedIn](https://www.linkedin.com/in/aroraabir)")

# ---------- Header ----------
st.title("📜 ArchiveLens")
st.subheader("Search old newspaper pages in seconds")
st.caption("All documents are fictional samples created for this project.")

# ---------- Three quick numbers ----------
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric("Scanned pages", "5")
with col2:
    with st.container(border=True):
        st.metric("OCR error before cleaning", "14.1%")
with col3:
    with st.container(border=True):
        st.metric("OCR error after cleaning", "3.5%", "-10.6 points", delta_color="inverse")

st.write("")
tab_search, tab_ocr, tab_all = st.tabs(["🔎 Search", "📊 OCR results", "📚 All documents"])

# ---------- Tab 1: Search ----------
with tab_search:
    typed = st.text_input("What are you looking for?", placeholder="Type a word, for example: steamer")
    example = st.pills("Or try an example:", ["steamer", "snow", "books", "fish prices"])
    query = typed or example

    if query:
        results = search_archive(DB_PATH, query, limit=5)
        st.markdown(f"#### {len(results)} result(s) for “{query}”")
        if not results:
            st.info("No pages found. Try another word.")
        for r in results:
            with st.container(border=True):
                st.markdown(f"### {r['source']}")
                st.caption(f"📅 {r['date']}   ·   🏷️ {r['category']}   ·   ⭐ relevance {r['relevance']}")
                st.markdown(f"> {r['snippet']}")
                with st.expander("📄 See the scanned page and the full text"):
                    conn = sqlite3.connect(DB_PATH)
                    row = conn.execute(
                        "SELECT image_path, ocr_text FROM documents WHERE id = ?", (r["id"],)
                    ).fetchone()
                    conn.close()
                    left, right = st.columns(2)
                    left.image(os.path.basename(row[0]), caption="Scanned page")
                    right.text(row[1])
    else:
        st.info("👆 Type a word or click an example to start searching.")

# ---------- Tab 2: OCR results ----------
with tab_ocr:
    st.markdown("#### How accurate was the OCR?")
    st.write("Lower Character Error Rate (CER) is better. Cleaning the images helped most on damaged pages.")
    st.dataframe(pd.read_csv("ocr_results.csv"), hide_index=True, width="stretch")
    st.image("cleaning_example.png", caption="Before and after image cleaning on the most damaged page")

# ---------- Tab 3: All documents ----------
with tab_all:
    st.markdown("#### Everything in the archive")
    conn = sqlite3.connect(DB_PATH)
    docs = pd.read_sql("SELECT id, source, date, category, word_count FROM documents", conn)
    conn.close()
    st.dataframe(docs, hide_index=True, width="stretch")
    st.image("sample_pages.png", caption="The 5 sample pages")

# ---------- Footer ----------
st.divider()
st.caption("Made with Python, OpenCV, Tesseract, SQLite and Streamlit · ArchiveLens by Arora Abir")
