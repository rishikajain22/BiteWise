"""Build Your Combo meal builder."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import get_food_by_id
from utils.nutrition_calculator import NUTRIENT_COLUMNS, macro_calories, scale_by_servings, sum_nutrients
from utils.ui import format_nutrient, page_header, style_figure


def _init_meal() -> None:
    if "meal_items" not in st.session_state:
        st.session_state.meal_items = []


def render(df: pd.DataFrame) -> None:
    _init_meal()
    page_header(
        "Module 04",
        "Build Your Combo",
        "Add items, set quantities, and keep a running nutritional total in session state.",
    )

    names = df["food_name"].tolist()
    add_col, qty_col, btn_col = st.columns([2.2, 0.8, 0.8])
    with add_col:
        choice = st.selectbox("Add a food", names)
    with qty_col:
        qty = st.number_input("Servings", min_value=0.25, max_value=8.0, value=1.0, step=0.25)
    with btn_col:
        st.write("")
        st.write("")
        if st.button("Add to combo", type="primary", width="stretch"):
            food_id = str(df[df["food_name"] == choice].iloc[0]["food_id"])
            st.session_state.meal_items.append({"food_id": food_id, "servings": float(qty)})
            st.rerun()

    if st.button("Reset meal"):
        st.session_state.meal_items = []
        st.rerun()

    items = st.session_state.meal_items
    if not items:
        st.info("Your combo is empty. Add a burger, a side, and a drink to see the meal maths.")
        return

    scaled_list = []
    display_rows = []
    remove_index = None

    for idx, item in enumerate(items):
        row = get_food_by_id(df, item["food_id"])
        if row is None:
            continue
        try:
            nutrients = scale_by_servings(row, item["servings"])
        except ValueError as exc:
            st.error(str(exc))
            continue
        scaled_list.append(nutrients)
        display_rows.append((idx, row, item["servings"], nutrients))

    for idx, row, servings, nutrients in display_rows:
        c1, c2, c3 = st.columns([2.4, 1.4, 0.6])
        with c1:
            st.markdown(
                f"""
                <div class="bw-card" style="padding:14px 16px;margin-bottom:8px;">
                    <p class="bw-kicker">{row["category"]}</p>
                    <h3 style="margin:0;">{row["food_name"]}</h3>
                    <p class="bw-muted">{servings:g} × {row["serving_label"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.metric("Calories in this item", format_nutrient("calories", nutrients["calories"]))
        with c3:
            if st.button("Remove", key=f"rm_{idx}"):
                remove_index = idx

    if remove_index is not None:
        st.session_state.meal_items.pop(remove_index)
        st.rerun()

    totals = sum_nutrients(scaled_list)
    st.markdown("### Meal totals")
    tcols = st.columns(4)
    tcols[0].metric("Calories", format_nutrient("calories", totals["calories"]))
    tcols[1].metric("Protein", format_nutrient("protein", totals["protein"]))
    tcols[2].metric("Carbs", format_nutrient("carbohydrates", totals["carbohydrates"]))
    tcols[3].metric("Fat", format_nutrient("fat", totals["fat"]))
    tcols2 = st.columns(3)
    tcols2[0].metric("Sugar", format_nutrient("sugar", totals["sugar"]))
    tcols2[1].metric("Fibre", format_nutrient("fibre", totals["fibre"]))
    tcols2[2].metric("Sodium", format_nutrient("sodium", totals["sodium"]))

    macros = macro_calories(totals)
    pie = px.pie(
        names=["Protein", "Carbohydrates", "Fat"],
        values=[macros["protein"], macros["carbohydrates"], macros["fat"]],
        hole=0.55,
    )
    style_figure(pie, title="Combo calorie composition")
    st.plotly_chart(pie, width="stretch")

    breakdown = pd.DataFrame(
        [
            {
                "Food": row["food_name"],
                "Servings": servings,
                **{col.title(): nutrients[col] for col in NUTRIENT_COLUMNS},
            }
            for _, row, servings, nutrients in display_rows
        ]
    )
    st.dataframe(breakdown, width="stretch")

    st.session_state.meal_totals = totals
    st.session_state.meal_breakdown = breakdown
