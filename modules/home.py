"""Home dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ui import page_header


HERO_IMAGE = "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=1400&q=80"

NAV_CARDS = [
    ("Nutrition Analyzer", "Scale any item and read the full nutrient panel."),
    ("Food Face-Off", "Put two or three items on the same table."),
    ("Build Your Combo", "Stack a meal and watch the totals move."),
    ("BiteWise Intelligence", "Rule-based swaps for sugar, sodium, fat or protein."),
    ("Nutrition Analytics", "See the catalogue as charts, not just rows."),
    ("Food Explorer", "Filter, sort and browse the full menu."),
]


def render(df: pd.DataFrame) -> None:
    verified = int(df["data_quality"].str.contains("Verified", case=False, na=False).sum())
    illustrative = len(df) - verified
    categories = df["category"].nunique()
    avg_cal = df["calories"].mean()

    st.markdown(
        f"""
        <div class="bw-hero">
            <div class="bw-hero-copy">
                <p class="bw-kicker">BiteWise</p>
                <h1>Your cravings.<br>Your calories.<br>Your smarter choices.</h1>
                <p>
                    A fast-food nutrition studio for exploring calories, comparing items,
                    building combos, and spotting nutritionally different alternatives —
                    without pretending a machine-learning model is doing the thinking.
                </p>
                <div class="bw-stat-row">
                    <div class="bw-stat"><span>Foods</span><strong>{len(df)}</strong></div>
                    <div class="bw-stat"><span>Categories</span><strong>{categories}</strong></div>
                    <div class="bw-stat"><span>Verified generic</span><strong>{verified}</strong></div>
                    <div class="bw-stat"><span>Avg kcal / listed serving</span><strong>{avg_cal:.0f}</strong></div>
                </div>
            </div>
            <div class="bw-hero-visual" style="background-image:url('{HERO_IMAGE}')"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<p class='bw-muted'>{illustrative} items use illustrative typical values. "
        "Brand-specific lab facts are not invented. Open any food card to see the data-quality note.</p>",
        unsafe_allow_html=True,
    )

    page_header("Start here", "Move through the kitchen", "Six tools. One catalogue. Same design language.")

    cols = st.columns(3)
    for i, (title, blurb) in enumerate(NAV_CARDS):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="bw-nav-card">
                    <p class="bw-kicker">Module 0{i + 2}</p>
                    <h3>{title}</h3>
                    <p class="bw-muted">{blurb}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {title}", key=f"home_nav_{i}", width="stretch"):
                st.session_state.page = title
                st.rerun()

    st.markdown("### Featured plates")
    featured = df.sample(n=min(4, len(df)), random_state=7)
    fcols = st.columns(4)
    for col, (_, row) in zip(fcols, featured.iterrows()):
        with col:
            st.markdown(
                f"""
                <div class="bw-card bw-food-card">
                    <div class="bw-food-photo" style="background-image:url('{row["image_url"]}')"></div>
                    <div class="bw-food-body">
                        <p class="bw-kicker">{row["category"]}</p>
                        <h3>{row["food_name"]}</h3>
                        <p class="bw-muted">{row["calories"]:.0f} kcal · {row["protein"]:.1f} g protein</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Popular categories")
    counts = df.groupby("category").size().sort_values(ascending=False)
    cat_cols = st.columns(min(5, len(counts)))
    for col, (name, count) in zip(cat_cols, counts.items()):
        with col:
            st.markdown(
                f"<div class='bw-stat'><span>{name}</span><strong>{int(count)}</strong></div>",
                unsafe_allow_html=True,
            )
