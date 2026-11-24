# BiteWise — Viva Preparation

## 1. Project overview

BiteWise is a **Fast Food Nutrition & Calorie Analyzer**. Users explore a 65-item catalogue, scale servings, compare foods, build a combo meal, and receive **rule-based** alternatives. The stack is Python, Streamlit, Pandas, NumPy and Plotly. Storage is CSV, not a remote database.

**Problem:** Fast food is easy to order and hard to compare honestly.  
**Approach:** One validated table, linear serving maths, visual comparison, transparent ranking.  
**Non-claim:** BiteWise Intelligence is **not** a trained AI/ML model.

## 2. Architecture

| Layer | Role |
| --- | --- |
| `app.py` | Page config, sidebar navigation, CSS, data load, dispatch |
| `modules/` | One render function per screen |
| `utils/data_loader.py` | Read CSV, validate columns, search |
| `utils/nutrition_calculator.py` | Serving scale, totals, macro calories, insights |
| `utils/recommendation_engine.py` | Goal-based ranking per 100 g |
| `utils/ui.py` | Shared cards, Plotly theme |
| `data/food_database.csv` | Catalogue |
| `assets/styles.css` | Design system |

Navigation is stored in `st.session_state.page`. The meal list lives in `st.session_state.meal_items`.

## 3. Python concepts used

- Modules and packages (`modules`, `utils`)
- Functions, type hints, dictionaries, lists
- Exceptions (`FoodDatabaseError`, `ValueError`)
- File paths with `pathlib`
- List/dict comprehensions
- `if __name__` is not required because Streamlit executes `app.py` as a script; `main()` is called at import time by Streamlit’s runner
- Session state as in-memory UI memory
- Pandas DataFrames and `groupby`
- NumPy `isnan` checks
- Plotly Express charts
- Linear scaling (ratio maths)

## 4. Module explanations

**Home** — Catalogue counts, verified vs illustrative split, featured sample, shortcuts that set `session_state.page`.

**Nutrition Analyzer** — Search + selectbox + gram slider. `scale_nutrients(row, grams)` multiplies every nutrient by `grams / serving_size_g`. Charts and insights use the scaled dict.

**Food Face-Off** — Two or three distinct foods scaled to **100 g** so large servings cannot look “worse” only because they are bigger. Grouped bar + line profile + verdict (lowest calories, highest protein/sodium/sugar).

**Build Your Combo** — Append `{food_id, servings}` to a list. Remove by index. Reset clears the list. Totals use `sum_nutrients`.

**BiteWise Intelligence** — For a goal column, candidates must be strictly better per 100 g. Score = improvement − small calorie-distance penalty. Same-category bonus is optional. Explanations are generated strings.

**Nutrition Analytics** — Category averages, pie of counts, scatter (protein vs calories, size = fat), box plot of calories, data-quality bar. If a combo exists, overlay its totals.

**Food Explorer** — Text search, multiselect category/brand, sort keys, cards, “Analyze this” jumps to the analyzer.

## 5. Library usage

**Pandas:** `read_csv`, `to_numeric`, filters with boolean masks, `groupby().agg()`, `sort_values`, `melt` for chart-ready tables, `drop_duplicates`.

**NumPy:** Safe float conversion; reject NaN so empty CSV cells do not crash the slider maths.

**Streamlit:** `st.set_page_config`, sidebar buttons, `st.slider`, `st.selectbox`, `st.number_input`, `st.metric`, `st.plotly_chart`, `st.dataframe`, `st.session_state`, `st.rerun`, `unsafe_allow_html` for the design system.

**Plotly:** Pie (macro split), grouped bar (face-off), line (profile), scatter, box. Layout uses transparent paper, lime colourway, cream typography.

## 6. Important formulas

Serving scale:

```
factor = chosen_grams / serving_size_g
scaled[n] = listed[n] * factor
```

Atwater-style macro calories (approximate):

```
kcal_protein = protein_g * 4
kcal_carb    = carbohydrates_g * 4
kcal_fat     = fat_g * 9
```

Fibre and sugar are **subsets of carbohydrates**, not extra calories on top.

Protein density example: `100 * protein / calories` → grams per 100 kcal.

Recommendation (lower sugar): keep candidates with `sugar_per_100g < original`; rank by how much lower, minus `0.02 * |calorie gap|`.

## 7. Data quality (say this clearly)

Some rows are **verified generic USDA-style** values. Many Indian QSR and cafe items are **illustrative typical values**. We did **not** fabricate McDonald’s / KFC official panels. Images are Unsplash URLs with CSS fallbacks.

## 8. Limitations

- Linear scaling ignores cooking loss and non-linear sauces
- Catalogue is a teaching set (~65 rows), not a complete market
- Sodium is milligrams; others grams; calories kcal
- No user accounts, no medical advice
- Charts need a browser; headless CI would need extra tooling

## 9. Thirty viva questions and answers

**Q1. What is BiteWise?**  
A student-built Streamlit app that analyzes fast-food nutrition from a CSV catalogue.

**Q2. Why Streamlit instead of Flask + HTML?**  
Streamlit is Python-native: widgets, charts and session state without a JavaScript frontend. That matches a 2nd-year Python lab.

**Q3. How is the project structured?**  
`app.py` routes; `modules` render pages; `utils` hold data, maths and UI; `data` holds CSV.

**Q4. How many foods and which categories?**  
65 foods: burgers, pizza, fries, sandwiches, wraps, fried chicken, beverages, desserts, Indian fast food.

**Q5. How do you load data?**  
`pandas.read_csv`, then required-column checks, numeric coercion, drop invalid rows.

**Q6. What if the CSV is missing?**  
`FoodDatabaseError` is raised and Streamlit shows `st.error` instead of crashing blank.

**Q7. How does serving-size calculation work?**  
Linear proportion from the listed gram serving. Doubling grams doubles every nutrient.

**Q8. Why grams, not “1 burger” only?**  
Grams are a common unit. Servings still exist in the meal builder as multipliers of the listed portion.

**Q9. Are sugar and fibre added on top of carbs?**  
No. They are part of total carbohydrate. Macro calories use protein, total carbs and fat.

**Q10. Why compare Face-Off at 100 g?**  
To compare composition fairly when listed servings differ (a 50 g samosa vs a 350 g thali).

**Q11. What is session_state?**  
A dictionary Streamlit keeps for the user session. We store current page, meal lines, analyzer selection and meal totals.

**Q12. How do you add/remove combo items?**  
Append a dict; remove by index; `st.rerun()` redraws.

**Q13. Is Intelligence machine learning?**  
No. It is ranking with explicit rules and a score function.

**Q14. How do you find a lower-sugar alternative?**  
Scale both foods to 100 g; keep lower sugar; prefer same category; penalise large calorie drift.

**Q15. Why per 100 g in recommendations?**  
Otherwise a tiny dessert always “wins” lower calories against a full meal.

**Q16. Which Pandas aggregations appear in Analytics?**  
`groupby("category").agg` for counts and averages; `value_counts` for data quality.

**Q17. What Plotly charts are used?**  
Pie, bar, line, scatter, box.

**Q18. How did you restyle Streamlit?**  
Custom CSS: hide toolbar, charcoal background, lime accent, Fraunces headings, card radii, button hover.

**Q19. How are images handled if Unsplash fails?**  
CSS background + empty-frame fallback class; category default URLs in the loader.

**Q20. What is NumPy used for?**  
Safe numeric conversion and NaN detection in the calculator.

**Q21. Difference between verified and illustrative data?**  
Verified ≈ published generic composition. Illustrative ≈ typical ranges for demo, labelled in `source_note`.

**Q22. Why not scrape restaurant sites?**  
Ethics, ToS, brittle HTML, and the brief forbids inventing brand facts.

**Q23. How do insights work?**  
Thresholds: e.g. sodium ≥ 800 mg, sugar ≥ 20 g, protein ≥ 20 g, plus data-quality reminder.

**Q24. How is the verdict in Face-Off computed?**  
`min`/`max` over scaled calorie, protein, sodium and sugar lists.

**Q25. Can the user sort the explorer?**  
Yes: calories, protein, fat, sugar, sodium, fibre, name.

**Q26. What happens on invalid slider input?**  
The slider is bounded; calculator still raises `ValueError` if grams ≤ 0.

**Q27. How would you add a database later?**  
Keep the same DataFrame contract; swap `read_csv` for SQL/`pd.read_sql`. Modules would not need a rewrite.

**Q28. Time and space complexity of recommendations?**  
One pass over ~65 rows, O(n) per query. Fine for this size; for thousands, precompute per-100 g columns.

**Q29. What is a design system here?**  
Shared colour tokens, type, cards, chips, Plotly layout helper so every page looks like one product.

**Q30. What would you add next (without claiming ML)?**  
User-entered custom foods, RDA comparison bars, export meal CSV, tighter USDA FDC IDs per verified row.

**Q31. Why Plotly not Matplotlib?**  
Interactive hover and Streamlit-native `st.plotly_chart`; Matplotlib is static unless extra widgets are added.

**Q32. How do you prevent duplicate food IDs?**  
`drop_duplicates(subset=["food_id"])` after load.

**Q33. What is `st.rerun()` for?**  
After changing session_state (navigation, add/remove meal) Streamlit must rerun the script from the top.

**Q34. Are calories always 4P+4C+9F?**  
Atwater is an estimate. Listed `calories` come from the table (USDA or typical). Charts of “calories from macros” can differ slightly from listed kcal because of fibre, alcohol (none here), rounding and data sources.

**Q35. What did you learn?**  
Modular Python, DataFrame pipelines, honest data labelling, and that a polished UI is still just functions over a table.
