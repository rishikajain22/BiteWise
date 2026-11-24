"""BiteWise Intelligence — rule-based recommendations."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nutrition_calculator import scale_nutrients
from utils.recommendation_engine import GOALS, nutrient_delta_rows, recommend_alternatives
from utils.ui import PLOTLY_COLORS, page_header, style_figure


def render(df: pd.DataFrame) -> None:
    page_header(
        "Module 05",
        "BiteWise Intelligence",
        "Transparent Python rules. No trained model. Alternatives scored per 100 g so serving size does not cheat.",
    )

    st.markdown(
        "<div class='bw-insight'>This engine compares nutrients with simple ranking rules. "
        "It is <strong>not</strong> machine learning and does not claim to be.</div>",
        unsafe_allow_html=True,
    )

    names = df["food_name"].tolist()
    food_name = st.selectbox("Starting food", names)
    goal_labels = {spec["label"]: key for key, spec in GOALS.items()}
    goal_label = st.selectbox("What should improve?", list(goal_labels.keys()))
    prefer_category = st.toggle("Prefer the same category", value=True)
    goal_key = goal_labels[goal_label]

    original = df[df["food_name"] == food_name].iloc[0]
    results = recommend_alternatives(
        df, str(original["food_id"]), goal_key, limit=5, prefer_same_category=prefer_category
    )

    orig_n = scale_nutrients(original, 100.0)
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("#### Original")
        st.markdown(
            f"""
            <div class="bw-card bw-food-card">
                <div class="bw-food-photo" style="background-image:url('{original["image_url"]}')"></div>
                <div class="bw-food-body">
                    <h3>{original["food_name"]}</h3>
                    <p class="bw-muted">{original["category"]} · per 100 g</p>
                    <p class="bw-muted">{orig_n["calories"]:.0f} kcal · {orig_n["protein"]:.1f} g protein · {orig_n["sugar"]:.1f} g sugar</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("#### Alternatives")
        if not results:
            st.warning("No candidate beat the original on that goal. Try another food or turn off category preference.")
            return
        for item in results:
            row = item["row"]
            n = item["per_100g"]
            st.markdown(
                f"""
                <div class="bw-card" style="padding:14px 16px;margin-bottom:10px;">
                    <p class="bw-kicker">{"Same category" if item["same_category"] else "Other category"} · score {item["score"]:.1f}</p>
                    <h3 style="margin:0 0 6px;">{row["food_name"]}</h3>
                    <p class="bw-muted">{n["calories"]:.0f} kcal · P {n["protein"]:.1f} g · F {n["fat"]:.1f} g · sugar {n["sugar"]:.1f} g · Na {n["sodium"]:.0f} mg</p>
                    <p>{item["explanation"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    best = results[0]
    alt_row = best["row"]
    delta = nutrient_delta_rows(orig_n, best["per_100g"])
    st.markdown(f"### Close-up: {original['food_name']} vs {alt_row['food_name']}")
    st.dataframe(delta, width="stretch")

    melt = delta.melt(id_vars=["Nutrient"], value_vars=["Original (per 100 g)", "Alternative (per 100 g)"],
                      var_name="Item", value_name="Value")
    fig = px.bar(melt, x="Nutrient", y="Value", color="Item", barmode="group", color_discrete_sequence=PLOTLY_COLORS)
    style_figure(fig, title="Original vs top alternative (per 100 g)")
    st.plotly_chart(fig, width="stretch")
