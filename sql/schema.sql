CREATE TABLE IF NOT EXISTS life_expectancy_imd (
    area_code TEXT PRIMARY KEY,
    area_name TEXT NOT NULL,
    female_life_expectancy REAL,
    male_life_expectancy REAL,
    imd_avg_rank REAL,
    imd_avg_score REAL,
    imd_rank_of_avg_score INTEGER,
    imd_prop_most_deprived_decile REAL
);