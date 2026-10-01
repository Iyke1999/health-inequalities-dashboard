# Methods

## Research Question
What is the relationship between area-level deprivation and life expectancy across local authorities in England, and how large is the life expectancy gap between the most and least deprived areas?

## Motivation
Health inequalities linked to deprivation are one of the most consistently documented patterns in UK public health data. This project builds a reproducible, version-controlled pipeline to quantify that relationship
directly from primary ONS and government deprivation data, rather than citing secondary summaries.

## Data Sources
1. **Life expectancy**: ONS, *Life expectancy for local areas of the UK:between 2001 to 2003 and 2022 to 2024*, released 10 December 2025. Local-authority-level life expectancy at birth, by sex.
2. **Deprivation**: MHCLG, *English Indices of Deprivation 2025 (IoD25)*, File 10 — Local Authority District summaries (lower tier), published 30 October 2025, updated 17 November 2025 (v2).

Full source URLs and release dates are recorded in `data/raw/sources.md`, generated at fetch time.

## Important Data-Availability Caveat
ONS has confirmed, via a published Freedom of Information response, that it does not produce life expectancy estimates broken down by deprivation decile *within* each local authority — only at national (England) level,
or as plain life expectancy per local authority with no internal deprivation split. This project uses the standard workaround: joining local-authority-level life expectancy with local-authority-level average
deprivation score, then analysing the relationship *across* local authorities rather than *within* them.

## Pipeline
1. **Fetch** (`src/fetch_data.py`) — downloads both source files directly from ONS and gov.uk, with provenance recorded in `data/raw/sources.md`
2. **Inspect** (`src/inspect_raw.py`) — probes raw spreadsheet structure (sheet names, header row positions) before parsing, since both are multi-sheet government spreadsheets with non-trivial layouts
3. **Parse & join** (`src/parse_health_data.py`) — filters life expectancy data to England, local-authority level, at-birth estimates for the latest period (2022–24); joins to IMD average score on local authority
   code
4. **Load** (`src/load_to_db.py`) — loads the joined table into SQLite (`db/health_inequalities.sqlite`)
5. **Analyze** (`src/analyze.py`) — Pearson correlation, linear regression, and a deprivation-quintile life expectancy comparison
6. **Visualize** — Power BI dashboard (`dashboard/`) built from the processed CSV outputs

## Match Rate
292 of 296 lower-tier local authorities in the IMD2025 dataset matched to life expectancy data. The 4 unmatched cases split into two distinct causes:
- Most of the 23 total unmatched *life-expectancy-side* codes are **upper-tier county councils** (e.g. Cambridgeshire, Lancashire), which ONS lists as "Local Areas" but which IMD File 10 — being lower-tier only — does not summarise directly; these counties are represented in IMD  only via their constituent district councils
- A small remainder (2 `E08` codes) reflects a minor local authority boundary/reorganisation mismatch between the two datasets' reference years, not investigated further given the small effect on the overall sample

## Results Summary
- **Pearson correlation**: r = -0.86 (p < 0.001) between IMD average score and average life expectancy at birth across 292 local authorities; deprivation explains approximately 74% of the variance (R² = 0.74)
- **Quintile gap**: average life expectancy falls from 83.4 years in the least deprived quintile of local authorities to 79.5 years in the most deprived quintile — a **3.9-year gap**
- **Sex difference**: the deprivation-linked gap is larger for men (4.4 years, R² = 0.78) than for women (3.5 years, R² = 0.65), consistent with the wider UK health inequalities literature

## Limitations
- **Cross-sectional, not causal**: this analysis establishes a strong association, not a causal mechanism — deprivation score is itself a composite of income, employment, health, education, crime, housing, and
  living environment domains, several of which plausibly both cause and result from poor health outcomes
- **Ecological inference**: local-authority-level correlation does not imply the same relationship holds for individuals within an area (the ecological fallacy) — some genuinely deprived individuals live in
  low-IMD-score areas and vice versa
- **Match rate**: 4 local authorities excluded due to boundary/tier mismatches between the two source datasets (see "Match Rate" above)
- **Single time period**: this analysis uses the latest available period (2022–24) only; both source files contain historical trend data back to 2001–03 (life expectancy) that could support a longitudinal analysis
- **No within-local-authority breakdown**: as noted above, ONS does not publish life expectancy by deprivation decile within local authorities, so this analysis cannot speak to inequality *within* a single area

## Future Work / At Scale
- **Longitudinal analysis**: both datasets contain 20+ years of trend data — tracking whether the deprivation gap has widened or narrowed since 2001–03 would be a natural extension
- **Regional breakdown**: joining an ONS local-authority-to-region lookup would allow testing whether the deprivation/life-expectancy relationship holds uniformly across England or varies by region
- **Domain-level analysis**: IMD25 provides 7 separate deprivation domains (income, employment, health, education, crime, barriers, living environment) beyond the composite score used here — decomposing which domain(s) correlate most strongly with life expectancy would be a more granular and policy-relevant finding
- **Upper-tier reconciliation**: resolving the 23 unmatched upper-tier county codes via File 11 (upper-tier IMD summaries) would allow full coverage of all English local authorities