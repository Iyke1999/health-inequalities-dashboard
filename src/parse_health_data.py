"""
Parse ONS life expectancy and MHCLG IMD local authority data into a joined,
analysis-ready table.

Reads:  data/raw/life_expectancy.xlsx (Sheet '1'), data/raw/imd_lad_summaries.xlsx (Sheet 'IMD')
Writes: data/processed/life_expectancy_imd_joined.csv
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

LE_PATH = RAW_DIR / "life_expectancy.xlsx"
IMD_PATH = RAW_DIR / "imd_lad_summaries.xlsx"
OUT_PATH = OUT_DIR / "life_expectancy_imd_joined.csv"

LATEST_PERIOD = "2022 to 2024"
BIRTH_AGE_GROUP = "<1"  # life expectancy at birth


def load_life_expectancy() -> pd.DataFrame:
    df = pd.read_excel(LE_PATH, sheet_name="1", header=5)
    print(f"Loaded {len(df)} raw rows from life_expectancy.xlsx")
    print("Unique Sex values:", sorted(df["Sex"].dropna().unique().tolist()))
    print("Unique Area type values:", sorted(df["Area type"].dropna().unique().tolist()))

    df = df[
        (df["Country"] == "England")
        & (df["Area type"] == "Local Areas")
        & (df["Age group"] == BIRTH_AGE_GROUP)
        & (df["Period"] == LATEST_PERIOD)
    ].copy()

    print(f"Filtered to {len(df)} rows (England, Local Areas, at birth, {LATEST_PERIOD})")
    return df


def load_imd() -> pd.DataFrame:
    df = pd.read_excel(IMD_PATH, sheet_name="IMD")
    df = df.rename(columns={
        "Local Authority District code (2024)": "area_code",
        "Local Authority District name (2024)": "area_name",
        "IMD - Average rank ": "imd_avg_rank",
        "IMD - Average score ": "imd_avg_score",
        "IMD - Rank of average score ": "imd_rank_of_avg_score",
        "IMD - Proportion of LSOAs in most deprived 10% nationally ": "imd_prop_most_deprived_decile",
    })
    print(f"Loaded {len(df)} IMD local authority rows")
    return df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    le = load_life_expectancy()
    imd = load_imd()

    # Pivot so each Sex category (Male/Female/Persons - whatever actually exists)
    # becomes its own column
    le_pivot = le.pivot_table(
        index=["Area code", "Area name"],
        columns="Sex",
        values="Life expectancy",
    ).reset_index()
    le_pivot.columns.name = None
    le_pivot = le_pivot.rename(columns={"Area code": "area_code", "Area name": "area_name"})

    merged = le_pivot.merge(
        imd[["area_code", "imd_avg_rank", "imd_avg_score",
             "imd_rank_of_avg_score", "imd_prop_most_deprived_decile"]],
        on="area_code",
        how="inner",
    )

    print(f"\nJoined dataset: {len(merged)} local authorities matched")
    unmatched = set(le_pivot["area_code"]) - set(imd["area_code"])
    if unmatched:
        print(f"NOTE: {len(unmatched)} area codes in life expectancy data had no IMD match "
              f"(expected for City of London / Isles of Scilly, which IMD excludes): "
              f"{sorted(unmatched)[:10]}")

    merged.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()