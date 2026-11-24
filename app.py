"""BiteWise — Fast Food Nutrition & Calorie Analyzer."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules import analytics, food_comparison, food_explorer, home, meal_builder, nutrition_analyzer, recommendations
from utils.data_loader import FoodDatabaseError, load_food_database
from utils.ui import inject_css

st.set_page_config(
    page_title="BiteWise — Nutrition Studio",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Home": home.render,
    "Nutrition Analyzer": nutrition_analyzer.render,
    "Food Face-Off": food_comparison.render,
    "Build Your Combo": meal_builder.render,
    "BiteWise Intelligence": recommendations.render,
    "Nutrition Analytics": analytics.render,
    "Food Explorer": food_explorer.render,
}

LOGO = Path(__file__).resolve().parent / "assets" / "logo.png"



def main() -> None:
    inject_css()

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    st.markdown("## BiteWise")
    st.caption("Your cravings. Your calories. Your smarter choices.")

    selected_page = st.radio(
        "Navigate to",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state.page),
        horizontal=True,
        key="main_navigation",
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.divider()

    try:
        df = load_food_database()
    except FoodDatabaseError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Unexpected error while loading data: {exc}")
        st.stop()

    page = st.session_state.get("page", "Home")
    render = PAGES.get(page, home.render)
    render(df)


main()

