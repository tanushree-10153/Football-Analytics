# ⚽ Football Player Performance Analytics Dashboard

> **Portfolio project** — An interactive football (soccer) analytics dashboard built with Python,
> Streamlit, Pandas, NumPy, and Plotly.

---

## ⚠️ Synthetic Data Disclaimer

**All player statistics in this project are computer-generated and entirely fictitious.**
They do not represent real players, clubs, competitions, or any real-world football results.
The dataset is clearly labelled as synthetic inside the app and in the data generator.

---

## Features

| Feature | Details |
|---|---|
| **Overview Page** | KPI cards (players, goals, assists, minutes, avg rating), top scorers bar chart, rating histogram, stacked goal-contribution chart |
| **Player Analysis** | Side-by-side player comparison with stat cards + grouped bar chart, Goals vs Assists scatter, Shots vs Goals bubble chart |
| **Team Analysis** | Grouped goals/assists bar, squad-size bar, average-rating bar, team summary table |
| **Position Analysis** | Rating & goals box plots, multi-axis radar chart, stacked goal-contribution bar |
| **Sidebar Filters** | Cascading Season → Team → Position → Player filters |
| **Stats Table** | Searchable, sortable player stats table on every page |
| **CSV Export** | One-click download of the currently filtered dataset |
| **Dark UI** | Professional pitch-green theme with `plotly_dark` charts |

---

## Project Structure

```
Football/
├── app.py                  # Main Streamlit application (all pages + logic)
├── football_players.csv    # Synthetic player dataset (120 rows, 19 columns)
├── generate_data.py        # Dataset generator (run once to recreate the CSV)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Dataset Schema

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique player ID |
| `player_name` | str | Synthetic full name |
| `team` | str | Club name (10 synthetic clubs) |
| `position` | str | GK / DEF / MID / FWD |
| `season` | str | 2021-22 / 2022-23 / 2023-24 |
| `age` | int | 18–38 |
| `matches_played` | int | 5–38 |
| `minutes_played` | int | Derived from matches |
| `goals` | int | Position-weighted |
| `assists` | int | Position-weighted |
| `shots` | int | Correlated with goals |
| `shots_on_target` | int | Subset of shots |
| `passes` | int | Position-weighted |
| `key_passes` | int | Subset of passes |
| `tackles` | int | Position-weighted |
| `interceptions` | int | Position-weighted |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–3 |
| `rating` | float | 5.0–9.5, contribution-weighted |

Derived metrics added at load time (not stored in CSV):
`goals_per_90`, `assists_per_90`, `shot_accuracy_pct`, `goal_conversion_pct`, `goal_contributions`

---

## Prerequisites

- Python **3.10** or newer
- `pip` (comes with Python)

---

## Local Setup & Run

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-dashboard.git
cd football-dashboard

# 2. (Optional) Create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Regenerate the dataset
python generate_data.py

# 5. Launch the dashboard
streamlit run app.py
```

The app opens automatically in your browser at **http://localhost:8501**.

---

## Deploy to Streamlit Community Cloud (Free)

1. Push this repository to a **public GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** → select your repo → set **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit installs dependencies from `requirements.txt` automatically.
5. Your dashboard is live at `https://<your-app>.streamlit.app`.

> **Note:** `football_players.csv` must be committed to the repo so the deployed app can read it.

---

## KPI Calculations

All KPIs are computed live from the filtered DataFrame — nothing is hardcoded.

| KPI | Formula |
|---|---|
| Total Players | `df['player_id'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Average Rating | `df['rating'].mean()` |

---

## Technology Stack

| Package | Version (min) | Purpose |
|---|---|---|
| `streamlit` | 1.32 | Web app framework |
| `pandas` | 2.0 | Data manipulation |
| `numpy` | 1.26 | Numerical generation |
| `plotly` | 5.20 | Interactive charts |

---

## Licence

This project is released under the **MIT Licence** — free to use, modify, and distribute.
