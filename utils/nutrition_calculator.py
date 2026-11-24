"""Dynamic nutrition calculations based on serving size."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

NUTRIENT_COLUMNS = (
    "calories",
    "protein",
    "carbohydrates",
    "fat",
    "sugar",
    "fibre",
    "sodium",
)

UNITS = {
    "calories": "kcal",
    "protein": "g",
    "carbohydrates": "g",
    "fat": "g",
    "sugar": "g",
    "fibre": "g",
    "sodium": "mg",
}

KCAL_PER_GRAM = {"protein": 4.0, "carbohydrates": 4.0, "fat": 9.0}


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(number):
        return default
    return number


def scale_nutrients(row: Mapping[str, Any] | pd.Series, grams: float) -> dict[str, float]:
    """Scale a food row from its listed serving to an arbitrary gram weight."""
    if grams <= 0:
        raise ValueError("Serving size must be greater than zero grams.")

    base_grams = _as_float(row.get("serving_size_g"), 0.0)
    if base_grams <= 0:
        raise ValueError("The food record has an invalid base serving size.")

    factor = grams / base_grams
    scaled = {col: round(_as_float(row.get(col)) * factor, 2) for col in NUTRIENT_COLUMNS}
    scaled["serving_size_g"] = round(grams, 1)
    return scaled


def scale_by_servings(row: Mapping[str, Any] | pd.Series, servings: float) -> dict[str, float]:
    """Scale a food row by a multiplier of its listed serving."""
    if servings <= 0:
        raise ValueError("Quantity must be greater than zero.")
    grams = _as_float(row.get("serving_size_g")) * servings
    return scale_nutrients(row, grams)


def sum_nutrients(items: list[dict[str, float]]) -> dict[str, float]:
    totals = {col: 0.0 for col in NUTRIENT_COLUMNS}
    totals["serving_size_g"] = 0.0
    for item in items:
        for key in totals:
            totals[key] += _as_float(item.get(key))
    return {key: round(value, 2) for key, value in totals.items()}


def macro_calories(nutrients: Mapping[str, float]) -> dict[str, float]:
    protein_kcal = _as_float(nutrients.get("protein")) * KCAL_PER_GRAM["protein"]
    carb_kcal = _as_float(nutrients.get("carbohydrates")) * KCAL_PER_GRAM["carbohydrates"]
    fat_kcal = _as_float(nutrients.get("fat")) * KCAL_PER_GRAM["fat"]
    total = protein_kcal + carb_kcal + fat_kcal
    if total <= 0:
        return {"protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "total": 0.0}
    return {
        "protein": round(protein_kcal, 1),
        "carbohydrates": round(carb_kcal, 1),
        "fat": round(fat_kcal, 1),
        "total": round(total, 1),
        "protein_pct": round(100 * protein_kcal / total, 1),
        "carbohydrates_pct": round(100 * carb_kcal / total, 1),
        "fat_pct": round(100 * fat_kcal / total, 1),
    }


def nutrient_density(nutrients: Mapping[str, float], nutrient: str) -> float:
    """Grams (or mg) of a nutrient per 100 kcal."""
    calories = _as_float(nutrients.get("calories"))
    if calories <= 0:
        return 0.0
    return round(100.0 * _as_float(nutrients.get(nutrient)) / calories, 2)


def difference_table(left: Mapping[str, float], right: Mapping[str, float]) -> dict[str, float]:
    return {col: round(_as_float(right.get(col)) - _as_float(left.get(col)), 2) for col in NUTRIENT_COLUMNS}


def nutritional_insights(row: Mapping[str, Any], nutrients: Mapping[str, float]) -> list[str]:
    """Short, rule-based insights for the current serving."""
    notes: list[str] = []
    calories = _as_float(nutrients.get("calories"))
    protein = _as_float(nutrients.get("protein"))
    fat = _as_float(nutrients.get("fat"))
    sugar = _as_float(nutrients.get("sugar"))
    fibre = _as_float(nutrients.get("fibre"))
    sodium = _as_float(nutrients.get("sodium"))
    carbs = _as_float(nutrients.get("carbohydrates"))
    grams = _as_float(nutrients.get("serving_size_g")) or _as_float(row.get("serving_size_g"))

    if calories >= 500:
        notes.append("This serving is calorie-dense. Pair it with a lighter side if you are managing intake.")
    elif calories <= 150:
        notes.append("This is a relatively light option by calorie count.")

    if protein >= 20:
        notes.append("Protein is substantial for a fast-food item, which can help satiety.")
    elif protein < 8 and calories >= 200:
        notes.append("Protein is modest relative to the calorie load.")

    if sugar >= 20:
        notes.append("Sugar is high in this serving. Consider a lower-sugar drink or dessert swap.")
    if sodium >= 800:
        notes.append("Sodium is high. Balance the rest of the meal with lower-sodium choices.")
    elif sodium <= 200 and grams >= 80:
        notes.append("Sodium is relatively modest for this portion size.")

    if fibre >= 5:
        notes.append("Fibre is a plus compared with many fast-food items.")
    if fat >= 25:
        notes.append("Fat contributes a large share of the calories in this serving.")

    macros = macro_calories(nutrients)
    if macros.get("carbohydrates_pct", 0) >= 60 and carbs >= 40:
        notes.append("Carbohydrates dominate the calorie mix.")
    if macros.get("fat_pct", 0) >= 50:
        notes.append("More than half of the usable calories come from fat.")

    quality = str(row.get("data_quality", ""))
    if "illustrative" in quality.lower():
        notes.append("Values for this item are illustrative typical figures, not a branded lab analysis.")

    if not notes:
        notes.append("A moderate profile. Compare it with an alternative in Food Face-Off if you want a tighter fit.")
    return notes[:5]
