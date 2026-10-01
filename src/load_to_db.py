"""
Load the joined life expectancy / IMD dataset into SQLite.

Reads:  data/processed/life_expectancy_imd_joined.csv, sql/schema.sql
Writes: db/health_inequalities.sqlite
"""

import sqlite3
from pathlib import Path

import pandas as pd

JOINED_PATH = Path("data/processed/life_expectancy_imd_joined.csv")
SCHEMA_PATH = Path("sql/schema.sql")
DB_PATH = Path("db/health_inequalities.sqlite")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    df = pd.read_csv(JOINED_PATH)
    df = df.rename(columns={"Female": "female_life_expectancy", "Male": "male_life_expectancy"})
    df.to_sql("life_expectancy_imd", conn, if_exists="replace", index=False)

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM life_expectancy_imd").fetchone()[0]
    print(f"Loaded {count} rows into {DB_PATH}")
    conn.close()


if __name__ == "__main__":
    main()