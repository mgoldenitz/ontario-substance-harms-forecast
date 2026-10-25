# Ontario substance harms forecast

How many opioid- and stimulant-related deaths and hospitalizations should Ontario expect from Q2 2026 to Q2 2027, how wide is the uncertainty, and does Ontario's trend follow Canada's?

Status: data profiled, models not yet fit. The project is also MATH59854 (Sheridan College) Group Work 2, due 14 December 2026. The working plan is in [SCOPE.md](SCOPE.md).

## Data

The source is the Public Health Agency of Canada's opioid and stimulant harms data on Health Infobase (https://health-infobase.canada.ca/substance-related-harms/opioids-stimulants/), downloaded 25 October 2026 as `data/raw/SubstanceHarmsData.csv`. The file has 33,250 rows covering deaths, hospitalizations, emergency department visits and EMS responses for Canada and each province and territory, by year and by quarter. 4,543 values are marked "Suppr.".

The series used here are Ontario and Canada overall quarterly counts:

- Opioid toxicity deaths, Q1 2016 to Q1 2026 (41 quarters)
- Stimulant toxicity deaths, Q1 2018 to Q1 2026 (33 quarters)
- Opioid-related poisoning hospitalizations, Q1 2016 to Q1 2026
- Stimulant-related poisoning hospitalizations, Q1 2016 to Q1 2026

None of these Ontario series has a suppressed quarter. Ontario EMS responses start in 2017 and have five suppressed quarters, so they are left out. Annual crude rates per 100,000 are used to compare Ontario with Canada.

Ontario's counts dropped sharply at the end of 2024. Opioid deaths were 581 in Q3 2024, 436 in Q4 2024 and 330 in Q1 2025, and stayed between 327 and 398 a quarter through Q1 2026. Stimulant deaths fell from 569 to 348 over the same three quarters.

## Method

Models are fit on Q1 2016 to Q3 2024 and tested on Q4 2024 to Q1 2026, the six quarters after the drop. A seasonal naive baseline, Holt's exponential smoothing and an ARIMA chosen by AIC are compared on MAE and MAPE. The final forecasts use all quarters, with and without a level-shift term from Q4 2024, and report 80% and 95% prediction intervals. The same forecasts are repeated in Excel and R, and a Power BI report shows them with the forecast visual.

## Files

`scripts/01_load_and_profile.py` reads the raw CSV, lists every Ontario and Canada series with its first and last period and its count of missing values (`data/processed/series_inventory.csv`), and writes the quarterly counts in long form (`data/processed/quarterly_on_ca.csv`).

To run it: `pip install pandas`, then `python scripts/01_load_and_profile.py` from the repository root.

## Limitations

Recent quarters are preliminary and Health Infobase revises earlier quarters with each release, so results depend on the download date. Death and hospitalization counts come from different systems (coroners and medical examiners for deaths, hospital discharge records for hospitalizations), and definitions vary by province. A forecast extends past patterns and cannot anticipate a change in the drug supply or in policy.

## Tools

Python (pandas, statsmodels), R, Excel, Power BI.

## Data licence

Health Infobase data are published under the Open Government Licence - Canada. Code in this repository is under the MIT License.
