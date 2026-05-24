import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from pandas import json_normalize
import warnings

warnings.filterwarnings("ignore")

# =========================================================
# API KEY
# =========================================================

API_KEY = "patCytbSzwwY9ZZhgner"


# =========================================================
# API URL & HEADERS
# =========================================================

url = "https://api.electricitymaps.com/v4/electricity-mix/past-range"

headers = {
    "auth-token": API_KEY
}

# =========================================================
# DEFINE COUNTRIES
# =========================================================

params_list = [
    {
        "zone": "FR",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    },
    {
        "zone": "ES",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    },
    {
        "zone": "DE",
        "start": "2026-01-01T00:00:00.000Z",
        "end": "2026-04-01T00:00:00.000Z",
        "temporalGranularity": "daily"
    }
]

COUNTRY_NAMES = {
    "FR": "France",
    "ES": "Spain",
    "DE": "Germany"
}

# =========================================================
# LOAD API DATA
# =========================================================

all_dfs = []

for params in params_list:
    zone = params["zone"]
    print(f"\nLoading data for {zone} ({COUNTRY_NAMES[zone]})...")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"  [HTTP Error] {e} — Skipping {zone}")
        continue
    except requests.exceptions.RequestException as e:
        print(f"  [Connection Error] {e} — Skipping {zone}")
        continue

    raw = response.json()

    # FIX: The API returns {"data": [...]} — normalize the nested list, not the wrapper
    records = raw.get("data", [])
    if not records:
        print(f"  No data received for {zone}.")
        continue

    # FIX: json_normalize on the list of records; nested dicts become dotted columns
    df = json_normalize(records)

    # Add country identifier
    df["country"] = zone
    df["country_name"] = COUNTRY_NAMES[zone]

    # Parse datetime
    df["datetime"] = pd.to_datetime(df["datetime"])

    # -------------------------------------------------------
    # FIX: Select only columns that actually exist in the df
    # -------------------------------------------------------
    desired_cols = [
        "datetime", "country", "country_name",
        "mix.wind",
        "mix.solar",
        "mix.hydro",
        "mix.nuclear",
        "mix.coal",
        "mix.gas",
        "mix.biomass",
        "mix.geothermal",
        "mix.oil",
        "mix.unknown",
        "mix.battery storage.charge",
        "mix.battery storage.discharge",
        "mix.hydro storage.charge",
        "mix.hydro storage.discharge",
        "mix.flows.imports",
        "mix.flows.exports",
    ]

    # Keep only the columns that exist (API schema may vary)
    available_cols = [c for c in desired_cols if c in df.columns]
    wind_df = df[available_cols].copy()

    # Rename for convenience
    rename_map = {
        "mix.wind":                      "wind_mw",
        "mix.solar":                     "solar_mw",
        "mix.hydro":                     "hydro_mw",
        "mix.nuclear":                   "nuclear_mw",
        "mix.coal":                      "coal_mw",
        "mix.gas":                       "gas_mw",
        "mix.biomass":                   "biomass_mw",
        "mix.geothermal":                "geothermal_mw",
        "mix.oil":                       "oil_mw",
        "mix.unknown":                   "unknown_mw",
        "mix.battery storage.charge":    "battery_charge_mw",
        "mix.battery storage.discharge": "battery_discharge_mw",
        "mix.hydro storage.charge":      "hydro_charge_mw",
        "mix.hydro storage.discharge":   "hydro_discharge_mw",
        "mix.flows.imports":             "import_mw",
        "mix.flows.exports":             "export_mw",
    }
    wind_df.rename(columns={k: v for k, v in rename_map.items() if k in wind_df.columns}, inplace=True)

    # Drop rows with no wind data
    if "wind_mw" not in wind_df.columns:
        print(f"  [WARNING] 'wind_mw' column not found for {zone} after renaming.")
        print(f"            Available columns: {list(wind_df.columns)}")
        print(f"            Check the [DEBUG] output above and update the rename_map.")
        continue

    wind_df = wind_df.dropna(subset=["wind_mw"])

    print(f"  {len(wind_df)} data points loaded.")
    all_dfs.append(wind_df)

# =========================================================
# MERGE ALL COUNTRIES
# =========================================================

if not all_dfs:
    raise RuntimeError("No data loaded. Please check your API key and connection.")

final_df = pd.concat(all_dfs, ignore_index=True)
final_df.sort_values(["country", "datetime"], inplace=True)

# =========================================================
# DISPLAY OPTIONS
# =========================================================

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:,.1f}".format)

# =========================================================
# DATAFRAME OVERVIEW
# =========================================================

print("\n" + "=" * 50)
print("DATAFRAME INFO")
print("=" * 50)
print(final_df.info())

print("\n" + "=" * 50)
print("FIRST 10 ROWS")
print("=" * 50)
print(final_df.head(10).to_string())

print("\n" + "=" * 50)
print("MISSING VALUES")
print("=" * 50)
print(final_df.isnull().sum())

# =========================================================
# WIND GENERATION ANALYSIS
# =========================================================

print("\n" + "=" * 50)
print("WIND GENERATION ANALYSIS (MW)")
print("=" * 50)

wind_stats = final_df.groupby(["country", "country_name"])["wind_mw"].agg(
    Mean="mean",
    Median="median",
    Std="std",
    Min="min",
    Max="max",
    Total="sum"
).round(1)

print("\nStatistics by Country:\n")
print(wind_stats.to_string())

# Month-by-month breakdown
if "datetime" in final_df.columns:
    final_df["month"] = final_df["datetime"].dt.to_period("M")
    monthly = final_df.groupby(["country_name", "month"])["wind_mw"].mean().round(1)
    print("\n\nMonthly Average Wind Generation (MW):\n")
    print(monthly.to_string())

# Wind share of total production (if other sources available)
production_cols = [c for c in ["wind_mw", "solar_mw", "hydro_mw", "nuclear_mw", "coal_mw", "gas_mw", "biomass_mw", "geothermal_mw", "oil_mw"] if c in final_df.columns]
if len(production_cols) > 1:
    for col in production_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors="coerce")
        final_df["total_production_mw"] = final_df[production_cols].sum(axis=1, min_count=1)
        final_df["wind_share_pct"] = (
            pd.to_numeric(final_df["wind_mw"], errors="coerce") /
            pd.to_numeric(final_df["total_production_mw"], errors="coerce") * 100
    ).round(2)
    wind_share = final_df.groupby("country_name")["wind_share_pct"].mean().round(2)
    print("\n\nAverage Wind Share of Total Production (%):\n")
    print(wind_share.to_string())

# =========================================================
# TOP & BOTTOM WIND DAYS
# =========================================================

print("\n" + "=" * 50)
print("TOP 10 WIND GENERATION DAYS")
print("=" * 50)

top_days = final_df.sort_values("wind_mw", ascending=False)[
    ["datetime", "country_name", "wind_mw"]
].head(10).copy()
top_days["datetime"] = top_days["datetime"].dt.date
print(top_days.to_string(index=False))

print("\n" + "=" * 50)
print("BOTTOM 10 WIND GENERATION DAYS (lowest production)")
print("=" * 50)

bottom_days = final_df.sort_values("wind_mw", ascending=True)[
    ["datetime", "country_name", "wind_mw"]
].head(10).copy()
bottom_days["datetime"] = bottom_days["datetime"].dt.date
print(bottom_days.to_string(index=False))

# =========================================================
# VISUALIZATION
# =========================================================

colors = {"FR": "#2563EB", "ES": "#DC2626", "DE": "#16A34A"}
country_labels = {"FR": "France", "ES": "Spain", "DE": "Germany"}

fig, axes = plt.subplots(3, 1, figsize=(16, 18))
fig.suptitle(
    "Wind Energy Generation Analysis — Q1 2026\nFrance · Spain · Germany",
    fontsize=16, fontweight="bold", y=0.98
)

# -------------------------------------------------------
# Plot 1: Wind Generation Over Time (line)
# -------------------------------------------------------
ax1 = axes[0]
for country in final_df["country"].unique():
    subset = final_df[final_df["country"] == country].copy()
    ax1.plot(
        subset["datetime"],
        subset["wind_mw"],
        label=country_labels.get(country, country),
        color=colors.get(country, "grey"),
        linewidth=2.0,
        alpha=0.9
    )
    # 7-day rolling mean
    subset = subset.set_index("datetime").sort_index()
    rolling = subset["wind_mw"].rolling("7D").mean()
    ax1.plot(
        rolling.index,
        rolling.values,
        color=colors.get(country, "grey"),
        linewidth=1.2,
        linestyle="--",
        alpha=0.5
    )

ax1.set_title("Daily Wind Generation (MW) with 7-Day Rolling Average (dashed)", fontsize=12)
ax1.set_ylabel("Wind Generation (MW)")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha="right")
ax1.legend(fontsize=10)
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

# -------------------------------------------------------
# Plot 2: Monthly Average Bar Chart
# -------------------------------------------------------
ax2 = axes[1]
if "month" in final_df.columns:
    monthly_pivot = (
        final_df.groupby(["month", "country"])["wind_mw"]
        .mean()
        .unstack("country")
    )
    months = [str(m) for m in monthly_pivot.index]
    x = range(len(months))
    width = 0.25
    for i, country in enumerate(monthly_pivot.columns):
        ax2.bar(
            [xi + i * width for xi in x],
            monthly_pivot[country],
            width=width,
            label=country_labels.get(country, country),
            color=colors.get(country, "grey"),
            alpha=0.85,
            edgecolor="white"
        )
    ax2.set_xticks([xi + width for xi in x])
    ax2.set_xticklabels(months)
    ax2.set_title("Monthly Average Wind Generation per Country (MW)", fontsize=12)
    ax2.set_ylabel("Avg Wind Generation (MW)")
    ax2.legend(fontsize=10)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

# -------------------------------------------------------
# Plot 3: Wind Share of Total Production (area chart)
# -------------------------------------------------------
ax3 = axes[2]
if "wind_share_pct" in final_df.columns:
    for country in final_df["country"].unique():
        subset = final_df[final_df["country"] == country].sort_values("datetime")
        ax3.fill_between(
            subset["datetime"],
            subset["wind_share_pct"],
            alpha=0.25,
            color=colors.get(country, "grey")
        )
        ax3.plot(
            subset["datetime"],
            subset["wind_share_pct"],
            label=country_labels.get(country, country),
            color=colors.get(country, "grey"),
            linewidth=2.0
        )
    ax3.set_title("Wind Share of Total Production (%)", fontsize=12)
    ax3.set_ylabel("Wind Share (%)")
    ax3.set_ylim(0, 100)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax3.legend(fontsize=10)
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
else:
    # Fallback: boxplot of wind distribution per country
    data_for_box = [
        final_df[final_df["country"] == c]["wind_mw"].dropna().values
        for c in final_df["country"].unique()
    ]
    ax3.boxplot(
        data_for_box,
        labels=[country_labels.get(c, c) for c in final_df["country"].unique()],
        patch_artist=True,
        boxprops=dict(facecolor="lightblue", color="navy"),
        medianprops=dict(color="red", linewidth=2)
    )
    ax3.set_title("Wind Generation Distribution by Country (MW)", fontsize=12)
    ax3.set_ylabel("Wind Generation (MW)")
    ax3.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("wind_analysis_Q1_2026.png", dpi=150, bbox_inches="tight")
print("\nPlot saved as: wind_analysis_Q1_2026.png")
plt.show()

# =========================================================
# EXPORT DATA (CSV)
# =========================================================

final_df.to_csv("wind_data_Q1_2026.csv", index=False)
print("Data exported as: wind_data_Q1_2026.csv")

print("\n[Done] Analysis complete.")