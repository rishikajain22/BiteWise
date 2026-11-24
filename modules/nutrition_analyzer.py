"""Nutrition Analyzer module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nutrition_calculator import (
    NUTRIENT_COLUMNS,
    UNITS,
    macro_calories,
    nutritional_insights,
    scale_nutrients,
)
from utils.ui import format_nutrient, page_header, style_figure


def render(df: pd.DataFrame) -> None:
    page_header(
        "Module 02",
        "Nutrition Analyzer",
        "Search an item, change the grams, and watch every nutrient recalculate.",
    )

    query = st.text_input("Search foods", placeholder="Try paneer, pizza, fries, cola…")
    filtered = df.copy()
    if query.strip():
        q = query.strip().lower()
        filtered = df[
            df["food_name"].str.lower().str.contains(q, na=False)
            | df["category"].str.lower().str.contains(q, na=False)
        ]
    if filtered.empty:
        st.warning("No foods matched that search. Clear the box to see the full list.")
        return

    names = filtered["food_name"].tolist()
    default_name = st.session_state.get("analyzer_food", names[0])
    if default_name not in names:
        default_name = names[0]
    selected_name = st.selectbox("Select a food", names, index=names.index(default_name))
    st.session_state.analyzer_food = selected_name
    row = filtered[filtered["food_name"] == selected_name].iloc[0]

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="bw-card bw-food-card">
                <div class="bw-food-photo" style="height:240px;background-image:url('{row["image_url"]}')"></div>
                <div class="bw-food-body">
                    <span class="bw-badge">{row["data_quality"]}</span>
                    <p class="bw-kicker" style="margin-top:10px;">{row["category"]} · {row["brand"]}</p>
                    <h3>{row["food_name"]}</h3>
                    <p class="bw-muted">{row["source_note"]}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        base = float(row["serving_size_g"])
        grams = st.slider(
            "Serving size (grams)",
            min_value=20,
            max_value=int(max(400, base * 3)),
            value=int(base),
            step=5,
            help="All nutrients scale linearly from the listed serving.",
        )
        try:
            nutrients = scale_nutrients(row, float(grams))
        except ValueError as exc:
            st.error(str(exc))
            return

        factor = grams / base
        st.caption(f"Listed serving: {row['serving_label']} ({base:.0f} g). Scale factor: ×{factor:.2f}.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Calories", format_nutrient("calories", nutrients["calories"]))
        m2.metric("Protein", format_nutrient("protein", nutrients["protein"]))
        m3.metric("Carbs", format_nutrient("carbohydrates", nutrients["carbohydrates"]))
        m4.metric("Fat", format_nutrient("fat", nutrients["fat"]))
        m5, m6, m7 = st.columns(3)
        m5.metric("Sugar", format_nutrient("sugar", nutrients["sugar"]))
        m6.metric("Fibre", format_nutrient("fibre", nutrients["fibre"]))
        m7.metric("Sodium", format_nutrient("sodium", nutrients["sodium"]))

    macros = macro_calories(nutrients)
    chart_df = pd.DataFrame(
        {
            "Macro": ["Protein", "Carbohydrates", "Fat"],
            "Calories": [macros["protein"], macros["carbohydrates"], macros["fat"]],
        }
    )
    fig = px.pie(chart_df, names="Macro", values="Calories", hole=0.58)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    style_figure(fig, title="Calories from protein, carbs and fat")
    st.plotly_chart(fig, width="stretch")

    bar_df = pd.DataFrame(
        {
            "Nutrient": [col.title() for col in NUTRIENT_COLUMNS if col != "calories"],
            "Amount": [nutrients[col] for col in NUTRIENT_COLUMNS if col != "calories"],
            "Unit": [UNITS[col] for col in NUTRIENT_COLUMNS if col != "calories"],
        }
    )
    fig_bar = px.bar(bar_df, x="Nutrient", y="Amount", color="Nutrient")
    style_figure(fig_bar, title="Nutrient amounts at the selected serving", showlegend=False)
    st.plotly_chart(fig_bar, width="stretch")

    st.markdown("### Insights")
    for note in nutritional_insights(row, nutrients):
        st.markdown(f"<div class='bw-insight'>{note}</div>", unsafe_allow_html=True)
