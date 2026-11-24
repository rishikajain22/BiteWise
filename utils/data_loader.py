"""Load and validate the BiteWise food database."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.nutrition_calculator import NUTRIENT_COLUMNS

REQUIRED_COLUMNS = (
    "food_id",
    "food_name",
    "category",
    "brand",
    "serving_size_g",
    "serving_label",
    "calories",
    "protein",
    "carbohydrates",
    "fat",
    "sugar",
    "fibre",
    "sodium",
    "data_quality",
    "source_note",
    "image_url",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = PROJECT_ROOT / "data" / "food_database.csv"

CATEGORY_FALLBACK_IMAGES = {
    "Burgers": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
    "Pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
    "Fries": "https://images.unsplash.com/photo-1576107232684-1279f390859f?auto=format&fit=crop&w=900&q=80",
    "Sandwiches": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=900&q=80",
    "Wraps": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=900&q=80",
    "Fried Chicken": "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?auto=format&fit=crop&w=900&q=80",
    "Beverages": "https://images.unsplash.com/photo-1544145945-f90425316c8c?auto=format&fit=crop&w=900&q=80",
    "Desserts": "https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=900&q=80",
    "Indian Fast Food": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=80",
}


class FoodDatabaseError(Exception):
    """Raised when the food catalogue cannot be loaded or validated."""


def load_food_database(csv_path: Path | str | None = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else DEFAULT_CSV
    if not path.exists():
        raise FoodDatabaseError(f"Food database not found at {path}")

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 — surface a student-friendly error
        raise FoodDatabaseError(f"Could not read the food database: {exc}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise FoodDatabaseError(f"Database is missing columns: {', '.join(missing)}")

    df = df.copy()
    df["food_id"] = df["food_id"].astype(str).str.strip()
    df["food_name"] = df["food_name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["brand"] = df["brand"].astype(str).str.strip()
    df["data_quality"] = df["data_quality"].astype(str).str.strip()

    numeric_cols = ("serving_size_g",) + NUTRIENT_COLUMNS
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["food_id", "food_name", "serving_size_g", "calories"])
    df = df[df["serving_size_g"] > 0]
    df = df.drop_duplicates(subset=["food_id"])
    df["image_url"] = df.apply(_resolve_image, axis=1)
    df = df.sort_values(["category", "food_name"]).reset_index(drop=True)
    if df.empty:
        raise FoodDatabaseError("The food database is empty after validation.")
    return df


def _resolve_image(row: pd.Series) -> str:
    url = str(row.get("image_url") or "").strip()
    if url.startswith("http"):
        return url
    return CATEGORY_FALLBACK_IMAGES.get(str(row.get("category")), CATEGORY_FALLBACK_IMAGES["Burgers"])


def get_food_by_id(df: pd.DataFrame, food_id: str) -> pd.Series | None:
    match = df[df["food_id"] == str(food_id)]
    if match.empty:
        return None
    return match.iloc[0]


def search_foods(df: pd.DataFrame, query: str) -> pd.DataFrame:
    text = (query or "").strip().lower()
    if not text:
        return df.copy()
    mask = (
        df["food_name"].str.lower().str.contains(text, na=False)
        | df["category"].str.lower().str.contains(text, na=False)
        | df["brand"].str.lower().str.contains(text, na=False)
    )
    return df.loc[mask].copy()


def unique_sorted(df: pd.DataFrame, column: str) -> list[str]:
    return sorted(df[column].dropna().astype(str).unique().tolist())
