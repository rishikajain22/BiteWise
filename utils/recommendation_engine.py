"""Rule-based BiteWise Intelligence engine (not a trained ML model)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from utils.nutrition_calculator import NUTRIENT_COLUMNS, _as_float, scale_nutrients

GOALS = {
    "lower_sugar": {
        "label": "Lower sugar",
        "column": "sugar",
        "direction": "lower",
        "why": "lower sugar per comparable serving",
    },
    "lower_sodium": {
        "label": "Lower sodium",
        "column": "sodium",
        "direction": "lower",
        "why": "lower sodium per comparable serving",
    },
    "lower_fat": {
        "label": "Lower fat",
        "column": "fat",
        "direction": "lower",
        "why": "less fat per comparable serving",
    },
    "higher_protein": {
        "label": "Higher protein",
        "column": "protein",
        "direction": "higher",
        "why": "more protein per comparable serving",
    },
    "lower_calories": {
        "label": "Lower calories",
        "column": "calories",
        "direction": "lower",
        "why": "fewer calories per comparable serving",
    },
}


def _per_100g(row: pd.Series) -> dict[str, float]:
    return scale_nutrients(row, 100.0)


def _score_candidate(original: dict[str, float], candidate: dict[str, float], goal_key: str) -> float:
    spec = GOALS[goal_key]
    column = spec["column"]
    original_value = _as_float(original.get(column))
    candidate_value = _as_float(candidate.get(column))
    calorie_gap = abs(_as_float(candidate.get("calories")) - _as_float(original.get("calories")))

    if spec["direction"] == "lower":
        if candidate_value >= original_value:
            return -1.0
        improvement = original_value - candidate_value
    else:
        if candidate_value <= original_value:
            return -1.0
        improvement = candidate_value - original_value

    # Prefer a real improvement without drifting too far in calories.
    return float(improvement) - 0.02 * calorie_gap


def explain_recommendation(
    original_row: pd.Series,
    candidate_row: pd.Series,
    original_n: dict[str, float],
    candidate_n: dict[str, float],
    goal_key: str,
    same_category: bool,
) -> str:
    spec = GOALS[goal_key]
    column = spec["column"]
    unit = "mg" if column == "sodium" else ("kcal" if column == "calories" else "g")
    delta = _as_float(candidate_n.get(column)) - _as_float(original_n.get(column))
    direction = "less" if delta < 0 else "more"
    scope = "the same category" if same_category else "the wider catalogue"
    return (
        f"{candidate_row['food_name']} is suggested from {scope} because it has "
        f"{abs(delta):.1f} {unit} {direction} {spec['label'].lower()} than "
        f"{original_row['food_name']} when both are compared per 100 g. "
        "This is a transparent rule, not a trained machine-learning model."
    )


def recommend_alternatives(
    df: pd.DataFrame,
    food_id: str,
    goal_key: str,
    limit: int = 5,
    prefer_same_category: bool = True,
) -> list[dict[str, Any]]:
    if goal_key not in GOALS:
        raise ValueError(f"Unknown recommendation goal: {goal_key}")

    match = df[df["food_id"] == str(food_id)]
    if match.empty:
        return []
    original_row = match.iloc[0]
    original_n = _per_100g(original_row)
    pool = df[df["food_id"] != str(food_id)].copy()

    ranked: list[dict[str, Any]] = []
    for _, candidate_row in pool.iterrows():
        candidate_n = _per_100g(candidate_row)
        same_category = candidate_row["category"] == original_row["category"]
        score = _score_candidate(original_n, candidate_n, goal_key)
        if prefer_same_category and same_category:
            score += 8.0
        if score < 0:
            continue
        ranked.append(
            {
                "row": candidate_row,
                "per_100g": candidate_n,
                "score": score,
                "same_category": bool(same_category),
                "explanation": explain_recommendation(
                    original_row, candidate_row, original_n, candidate_n, goal_key, bool(same_category)
                ),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]


def nutrient_delta_rows(original_n: dict[str, float], alternative_n: dict[str, float]) -> pd.DataFrame:
    rows = []
    for col in NUTRIENT_COLUMNS:
        left = _as_float(original_n.get(col))
        right = _as_float(alternative_n.get(col))
        rows.append(
            {
                "Nutrient": col.replace("_", " ").title(),
                "Original (per 100 g)": round(left, 2),
                "Alternative (per 100 g)": round(right, 2),
                "Difference": round(right - left, 2),
            }
        )
    return pd.DataFrame(rows)
