"""Food Face-Off comparison module."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.nutrition_calculator import NUTRIENT_COLUMNS, scale_nutrients
from utils.ui import PLOTLY_COLORS, page_header, style_figure


def render(df: pd.DataFrame) -> None:
    page_header(
        "Module 03",
        "Food Face-Off",
        "Pick two or three items. Same 100 g lens. Clear differences. A plain-English verdict.",
    )

    count = st.radio("How many foods?", [2, 3], horizontal=True, index=0)
    names = df["food_name"].tolist()

    picks = []
    cols = st.columns(count)
    defaults = names[:count]
    for i, col in enumerate(cols):
        with col:
            choice = st.selectbox(f"Food {i + 1}", names, index=names.index(defaults[i]), key=f"faceoff_{i}")
            picks.append(choice)

    if len(set(picks)) < count:
        st.warning("Choose distinct foods so the comparison has contrast.")
        return

    rows = [df[df["food_name"] == name].iloc[0] for name in picks]
    scaled = [scale_nutrients(row, 100.0) for row in rows]

    card_cols = st.columns(count)
    for col, row, nut in zip(card_cols, rows, scaled):
        with col:
            st.markdown(
                f"""
                <div class="bw-card bw-food-card">
                    <div class="bw-food-photo" style="background-image:url('{row["image_url"]}')"></div>
                    <div class="bw-food-body">
                        <p class="bw-kicker">{row["category"]}</p>
                        <h3>{row["food_name"]}</h3>
                        <p class="bw-muted">Compared at 100 g · {row["data_quality"]}</p>
                        <div class="bw-chip-row">
                            <div class="bw-chip"><span>Calories</span><strong>{nut["calories"]:.0f}</strong></div>
                            <div class="bw-chip"><span>Protein</span><strong>{nut["protein"]:.1f} g</strong></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    long_rows = []
    for row, nut in zip(rows, scaled):
        for col in NUTRIENT_COLUMNS:
            long_rows.append({"Food": row["food_name"], "Nutrient": col.title(), "Value": nut[col]})
    long_df = pd.DataFrame(long_rows)

    fig = px.bar(long_df, x="Nutrient", y="Value", color="Food", barmode="group", color_discrete_sequence=PLOTLY_COLORS)
    style_figure(fig, title="Side-by-side nutrients per 100 g")
    st.plotly_chart(fig, width="stretch")

    radar_df = long_df[long_df["Nutrient"] != "Calories"]
    fig_line = px.line(radar_df, x="Nutrient", y="Value", color="Food", markers=True, color_discrete_sequence=PLOTLY_COLORS)
    style_figure(fig_line, title="Profile shape (per 100 g)")
    st.plotly_chart(fig_line, width="stretch")

    table = pd.DataFrame({row["food_name"]: [scaled[i][c] for c in NUTRIENT_COLUMNS] for i, row in enumerate(rows)})
    table.index = [c.title() for c in NUTRIENT_COLUMNS]
    if count == 2:
        table["Difference (B − A)"] = table.iloc[:, 1] - table.iloc[:, 0]
    st.dataframe(table.round(2), width="stretch")

    lightest = min(range(count), key=lambda i: scaled[i]["calories"])
    protein_pick = max(range(count), key=lambda i: scaled[i]["protein"])
    saltiest = max(range(count), key=lambda i: scaled[i]["sodium"])
    sweetest = max(range(count), key=lambda i: scaled[i]["sugar"])

    st.markdown(
        f"""
        <div class="bw-verdict">
            <p class="bw-kicker">Verdict</p>
            <h3>{rows[lightest]["food_name"]} is the lighter calorie choice per 100 g.</h3>
            <p>
                {rows[protein_pick]["food_name"]} leads on protein
                ({scaled[protein_pick]["protein"]:.1f} g).
                {rows[saltiest]["food_name"]} is highest in sodium
                ({scaled[saltiest]["sodium"]:.0f} mg).
                {rows[sweetest]["food_name"]} is highest in sugar
                ({scaled[sweetest]["sugar"]:.1f} g).
                Numbers are scaled to 100 g so portion size does not hide the difference.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
