"""
Download raw source files for the health inequalities dashboard.

Writes: data/raw/life_expectancy.xlsx, data/raw/imd_lad_summaries.xlsx,
        data/raw/sources.md (provenance record)
"""

from datetime import date
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")

SOURCES = {
    "life_expectancy.xlsx": {
        "url": (
            "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/"
            "healthandsocialcare/healthandlifeexpectancies/datasets/"
            "lifeexpectancyforlocalareasoftheuk/between2001to2003and2022to2024/"
            "lifeexpectancylocalareas.xlsx"
        ),
        "title": "Life expectancy for local areas of the UK (2001-03 to 2022-24)",
        "publisher": "Office for National Statistics (ONS)",
        "release_date": "2025-12-10",
        "page": (
            "https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/"
            "healthandlifeexpectancies/datasets/lifeexpectancyforlocalareasoftheuk"
        ),
    },
    "imd_lad_summaries.xlsx": {
        "url": (
            "https://assets.publishing.service.gov.uk/media/6917412ebc34c86ce4e6e7fc/"
            "File_10_-_IoD2025_Local_Authority_District_Summaries__lower-tier__v2.xlsx"
        ),
        "title": "English Indices of Deprivation 2025 — File 10: Local Authority District summaries (lower tier)",
        "publisher": "Ministry of Housing, Communities and Local Government (MHCLG)",
        "release_date": "2025-11-17",  # v2, corrected release
        "page": "https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025",
    },
}


def download(filename: str, meta: dict):
    out_path = RAW_DIR / filename
    if out_path.exists():
        print(f"Skipping {filename} (already downloaded)")
        return

    print(f"Downloading {filename}...")
    response = requests.get(meta["url"], stream=True)
    response.raise_for_status()

    with open(out_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"  Saved {out_path} ({out_path.stat().st_size / 1_048_576:.1f} MB)")


def write_sources_md():
    lines = ["# Data Sources", "", f"_Fetched: {date.today().isoformat()}_", ""]
    for filename, meta in SOURCES.items():
        lines += [
            f"## {meta['title']}",
            f"- **File:** `data/raw/{filename}`",
            f"- **Publisher:** {meta['publisher']}",
            f"- **Release date:** {meta['release_date']}",
            f"- **Source page:** {meta['page']}",
            f"- **Direct download:** {meta['url']}",
            "",
        ]
    (RAW_DIR / "sources.md").write_text("\n".join(lines))
    print("Wrote data/raw/sources.md")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for filename, meta in SOURCES.items():
        download(filename, meta)
    write_sources_md()


if __name__ == "__main__":
    main()