"""Food Explorer catalogue."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import search_foods
from utils.ui import page_header


SORT_OPTIONS = {
    "Name": ("food_name", True),
    "Calories (low to high)": ("calories", True),
    "Calories (high to low)": ("calories", False),
    "Protein (high to low)": ("protein", False),
    "Fat (low to high)": ("fat", True),
    "Sugar (low to high)": ("sugar", True),
    "Sodium (low to high)": ("sodium", True),
    "Fibre (high to low)": ("fibre", False),
}


def render(df: pd.DataFrame) -> None:
    page_header(
        "Module 07",
        "Food Explorer",
        "Search, filter by category and brand, then sort the catalogue like a menu board.",
    )

    query = st.text_input("Search", placeholder="Name, category, or brand")
    c1, c2, c3 = st.columns(3)
    with c1:
        categories = st.multiselect("Category", sorted(df["category"].unique()))
    with c2:
        brands = st.multiselect("Brand / source", sorted(df["brand"].unique()))
    with c3:
        sort_label = st.selectbox("Sort", list(SORT_OPTIONS.keys()))

    view = search_foods(df, query)
    if categories:
        view = view[view["category"].isin(categories)]
    if brands:
        view = view[view["brand"].isin(brands)]

    col, ascending = SORT_OPTIONS[sort_label]
    view = view.sort_values(col, ascending=ascending)

    st.caption(f"{len(view)} foods in view.")
    if view.empty:
        st.warning("Nothing matches those filters.")
        return

    rows = list(view.iterrows())
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        chunk = rows[i : i + 3]
        for col, (_, row) in zip(cols, chunk):
            with col:
                quality = "Verified generic" if "verified" in str(row["data_quality"]).lower() else "Illustrative"
                st.markdown(
                    f"""
                    <div class="bw-card bw-food-card">
                        <div class="bw-food-photo" style="background-image:url('{row["image_url"]}')"></div>
                        <div class="bw-food-body">
                            <p class="bw-kicker">{row["category"]} · {quality}</p>
                            <h3>{row["food_name"]}</h3>
                            <p class="bw-muted">{row["brand"]}</p>
                            <p class="bw-muted">{row["serving_label"]}</p>
                            <div class="bw-chip-row">
                                <div class="bw-chip"><span>Calories</span><strong>{row["calories"]:.0f}</strong></div>
                                <div class="bw-chip"><span>Protein</span><strong>{row["protein"]:.1f} g</strong></div>
                            </div>
                            <p class="bw-muted" style="margin-top:10px;">
                                Fat {row["fat"]:.1f} g · Sugar {row["sugar"]:.1f} g · Na {row["sodium"]:.0f} mg
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Analyze this", key=f"ex_{row['food_id']}", width="stretch"):
                    st.session_state.analyzer_food = row["food_name"]
                    st.session_state.page = "Nutrition Analyzer"
                    st.rerun()
