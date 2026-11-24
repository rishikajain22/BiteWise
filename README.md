# BiteWise

**Your cravings. Your calories. Your smarter choices.**

BiteWise is a Python + Streamlit food-tech studio for exploring fast-food nutrition, comparing items, building combos, and generating **rule-based** alternatives. It is a complete lab project, not a trained machine-learning product.

## Features

1. **Home** — branding, catalogue stats, featured foods, module shortcuts  
2. **Nutrition Analyzer** — search, serving-size slider, live nutrient maths, Plotly charts, insights  
3. **Food Face-Off** — 2 or 3 foods compared per 100 g with charts and a verdict  
4. **Build Your Combo** — add / quantity / remove / reset using `st.session_state`  
5. **BiteWise Intelligence** — transparent ranking rules (lower sugar, sodium, fat; higher protein)  
6. **Nutrition Analytics** — category charts, scatter, box plots, optional combo overlay  
7. **Food Explorer** — search, category and brand filters, sorting, food cards  

## Data honesty

`data/food_database.csv` holds **65** items across burgers, pizza, fries, sandwiches, wraps, fried chicken, beverages, desserts and Indian fast food.

| `data_quality` | Meaning |
| --- | --- |
| Verified generic | Generic (not branded) values aligned with published USDA-style food composition figures |
| Illustrative typical values | Kitchen/QSR-range estimates used so the app can be demonstrated. **Not** invented brand lab facts |

Every row includes `source_note`. Do not treat illustrative rows as a specific restaurant’s official panel.

Columns: `food_id`, `food_name`, `category`, `brand`, `serving_size_g`, `serving_label`, `calories`, `protein`, `carbohydrates`, `fat`, `sugar`, `fibre`, `sodium`, `data_quality`, `source_note`, `image_url`.

Nutrient amounts are **per listed serving**. The analyzer and meal builder scale them linearly:

`scaled = listed_value × (chosen_grams / serving_size_g)`

## Setup

Python 3.12+ (the project also runs on newer CPython).

```bash
cd BiteWise
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

Regenerate the CSV after editing `scripts/build_database.py`:

```bash
python scripts/build_database.py
```

## Architecture

```
BiteWise/
├── app.py
├── requirements.txt
├── README.md
├── VIVA_PREPARATION.md
├── data/food_database.csv
├── modules/          # one file per screen
├── utils/            # load, calculate, recommend, UI
├── assets/           # CSS, logo, images
└── scripts/          # database builder
```

## Tech

- **Streamlit** — layout, widgets, session state, theming override  
- **Pandas** — CSV load, filters, groupby analytics  
- **NumPy** — numeric safety in scaling  
- **Plotly** — interactive pie, bar, line, scatter, box charts  
- **Custom CSS** — charcoal surfaces, lime accent, Fraunces + DM Sans  

## Academic note

Recommendations are **if/else and scoring functions**, not a fitted model. State that clearly in a viva.
