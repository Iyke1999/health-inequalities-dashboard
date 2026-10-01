"""
Statistical analysis: correlation, regression, and deprivation-quintile
life expectancy gap.

Reads:  db/health_inequalities.sqlite
Writes: outputs/results.csv, outputs/quintile_summary.csv
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DB_PATH = Path("db/health_inequalities.sqlite")
OUT_DIR = Path("outputs")


def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM life_expectancy_imd", conn)
    conn.close()
    df["avg_life_expectancy"] = df[["female_life_expectancy", "male_life_expectancy"]].mean(axis=1)
    return df


def correlation_and_regression(df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for metric in ["avg_life_expectancy", "female_life_expectancy", "male_life_expectancy"]:
        r, p = stats.pearsonr(df["imd_avg_score"], df[metric])
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df["imd_avg_score"], df[metric]
        )
        results.append({
            "metric": metric,
            "pearson_r": r,
            "pearson_p": p,
            "regression_slope": slope,   # years of LE per 1-unit increase in IMD score
            "regression_intercept": intercept,
            "r_squared": r_value ** 2,
            "n": len(df),
        })
    return pd.DataFrame(results)


def quintile_gap(df: pd.DataFrame) -> pd.DataFrame:
    # Quintile 1 = least deprived (lowest IMD score), Quintile 5 = most deprived
    df = df.copy()
    df["imd_quintile"] = pd.qcut(df["imd_avg_score"], 5, labels=[1, 2, 3, 4, 5])

    summary = df.groupby("imd_quintile", observed=True).agg(
        n_local_authorities=("area_code", "count"),
        avg_imd_score=("imd_avg_score", "mean"),
        avg_life_expectancy=("avg_life_expectancy", "mean"),
        avg_female_le=("female_life_expectancy", "mean"),
        avg_male_le=("male_life_expectancy", "mean"),
    ).reset_index()

    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()

    reg = correlation_and_regression(df)
    reg.to_csv(OUT_DIR / "results.csv", index=False)
    print("=== Correlation & Regression ===")
    print(reg.to_string(index=False))

    quintiles = quintile_gap(df)
    quintiles.to_csv(OUT_DIR / "quintile_summary.csv", index=False)
    print("\n=== Life Expectancy by Deprivation Quintile ===")
    print(quintiles.to_string(index=False))

    gap = (
        quintiles.loc[quintiles["imd_quintile"] == 1, "avg_life_expectancy"].values[0]
        - quintiles.loc[quintiles["imd_quintile"] == 5, "avg_life_expectancy"].values[0]
    )
    print(f"\nHEADLINE: Life expectancy gap between least and most deprived quintile: {gap:.1f} years")


if __name__ == "__main__":
    main()