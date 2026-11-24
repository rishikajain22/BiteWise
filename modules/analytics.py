"""Nutrition Analytics dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ui import PLOTLY_COLORS, page_header, style_figure


def render(df: pd.DataFrame) -> None:
    page_header(
        "Module 06",
        "Nutrition Analytics",
        "Catalogue-level charts plus, if you built a combo, a live meal overlay.",
    )

    cat = df.groupby("category", as_index=False).agg(
        items=("food_id", "count"),
        avg_calories=("calories", "mean"),
        avg_protein=("protein", "mean"),
        avg_fat=("fat", "mean"),
        avg_carbs=("carbohydrates", "mean"),
        avg_sugar=("sugar", "mean"),
        avg_sodium=("sodium", "mean"),
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cat.sort_values("avg_calories", ascending=False), x="category", y="avg_calories", color="category",
                     color_discrete_sequence=PLOTLY_COLORS)
        style_figure(fig, title="Average listed-serving calories by category", showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = px.pie(cat, names="category", values="items", hole=0.5)
        style_figure(fig, title="Foods in the database")
        st.plotly_chart(fig, width="stretch")

    fig = px.scatter(
        df,
        x="calories",
        y="protein",
        color="category",
        size="fat",
        hover_name="food_name",
        color_discrete_sequence=PLOTLY_COLORS,
    )
    style_figure(fig, title="Protein vs calories (bubble size = fat)")
    st.plotly_chart(fig, width="stretch")

    fig = px.box(df, x="category", y="calories", color="category", color_discrete_sequence=PLOTLY_COLORS)
    style_figure(fig, title="Calorie spread by category", showlegend=False)
    st.plotly_chart(fig, width="stretch")

    quality = df["data_quality"].value_counts().reset_index()
    quality.columns = ["Data quality", "Count"]
    fig = px.bar(quality, x="Data quality", y="Count", color="Data quality", color_discrete_sequence=PLOTLY_COLORS)
    style_figure(fig, title="Verified generic vs illustrative rows", showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.markdown("### Category nutrient table")
    show = cat.copy()
    for col in show.columns:
        if col.startswith("avg_"):
            show[col] = show[col].round(1)
    st.dataframe(show, width="stretch")

    totals = st.session_state.get("meal_totals")
    breakdown = st.session_state.get("meal_breakdown")
    if totals and isinstance(breakdown, pd.DataFrame) and not breakdown.empty:
        st.markdown("### Current combo overlay")
        mcols = st.columns(4)
        mcols[0].metric("Combo kcal", f"{totals['calories']:.0f}")
        mcols[1].metric("Protein", f"{totals['protein']:.1f} g")
        mcols[2].metric("Fat", f"{totals['fat']:.1f} g")
        mcols[3].metric("Sodium", f"{totals['sodium']:.0f} mg")
        fig = px.bar(breakdown, x="Food", y="Calories", color="Food", color_discrete_sequence=PLOTLY_COLORS)
        style_figure(fig, title="Calories contributed by each combo item", showlegend=False)
        st.plotly_chart(fig, width="stretch")
    else:
        st.caption("Build a combo in Build Your Combo to overlay a live meal summary here.")
