"""Shared Streamlit UI helpers and the BiteWise design system."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from utils.nutrition_calculator import UNITS

ASSETS = Path(__file__).resolve().parent.parent / "assets"
STYLES = ASSETS / "styles.css"

LIME = "#C8F542"
CREAM = "#F4F1EA"
MUTED = "#A8A29E"
CARD = "#1C1C1F"

PLOTLY_COLORS = ["#C8F542", "#E8B86D", "#7DD3C0", "#F4F1EA", "#FF8A7A", "#B9A0FF"]


def inject_css() -> None:
    css = STYLES.read_text(encoding="utf-8") if STYLES.exists() else ""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def plotly_layout(**extra) -> dict:
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=CREAM, family="DM Sans, sans-serif", size=13),
        colorway=PLOTLY_COLORS,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#111113", font_color=CREAM),
    )
    layout.update(extra)
    return layout


def style_figure(fig: go.Figure, **layout_kwargs) -> go.Figure:
    fig.update_layout(**plotly_layout(**layout_kwargs))
    fig.update_xaxes(gridcolor="rgba(244,241,234,0.08)", zerolinecolor="rgba(244,241,234,0.12)")
    fig.update_yaxes(gridcolor="rgba(244,241,234,0.08)", zerolinecolor="rgba(244,241,234,0.12)")
    return fig


def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="bw-page-header">
            <p class="bw-kicker">{kicker}</p>
            <h1>{title}</h1>
            <p class="bw-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_chip(label: str, value: str) -> str:
    return f'<div class="bw-chip"><span>{label}</span><strong>{value}</strong></div>'


def food_card_html(row, nutrients: dict | None = None, compact: bool = False) -> str:
    n = nutrients or {}
    calories = n.get("calories", row["calories"])
    protein = n.get("protein", row["protein"])
    quality = str(row.get("data_quality", ""))
    badge = "Verified generic" if "verified" in quality.lower() else "Illustrative"
    height = "160px" if compact else "210px"
    return f"""
    <div class="bw-card bw-food-card">
        <div class="bw-food-photo" style="height:{height};background-image:url('{row["image_url"]}')"></div>
        <div class="bw-food-body">
            <p class="bw-kicker">{row["category"]} · {badge}</p>
            <h3>{row["food_name"]}</h3>
            <p class="bw-muted">{row["brand"]} · {row["serving_label"]}</p>
            <div class="bw-chip-row">
                {metric_chip("Calories", f"{calories:.0f} kcal")}
                {metric_chip("Protein", f"{protein:.1f} g")}
            </div>
        </div>
    </div>
    """


def image_with_fallback(url: str, alt: str, height: int = 220) -> None:
    st.markdown(
        f"""
        <div class="bw-photo-frame" style="height:{height}px;">
            <img src="{url}" alt="{alt}" onerror="this.style.display='none'; this.parentNode.classList.add('fallback');" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_nutrient(name: str, value: float) -> str:
    unit = UNITS.get(name, "")
    if name == "calories":
        return f"{value:.0f} {unit}"
    if name == "sodium":
        return f"{value:.0f} {unit}"
    return f"{value:.1f} {unit}"
