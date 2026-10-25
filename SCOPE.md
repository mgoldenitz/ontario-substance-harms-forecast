# Ontario substance harms forecast: scope

Draft, updated 25 October 2026 after profiling the data. This is a working plan for the project. It is not the README.

## Question

How many opioid- and stimulant-related deaths and hospitalizations should Ontario expect over the next four to six quarters, how wide is the uncertainty, and does Ontario's trend follow Canada's?

## Data

The main source is the Public Health Agency of Canada's opioid and stimulant harms data on Health Infobase (health-infobase.canada.ca/substance-related-harms/opioids-stimulants), downloaded 25 October 2026 as SubstanceHarmsData.csv (33,250 rows). Columns are Substance, Source, Specific_Measure, Region, PRUID, Time_Period, Year_Quarter, Aggregator, Disaggregator, Unit and Value. Sources are deaths, hospitalizations, emergency department visits and EMS responses. 4,543 values are marked "Suppr.".

For Ontario and Canada, the overall quarterly counts run from Q1 2016 to Q1 2026 (41 quarters) for opioid deaths, opioid hospitalizations, stimulant hospitalizations and both ED series. Stimulant deaths start in Q1 2018 (33 quarters). None of these Ontario series has a suppressed quarter. Ontario EMS starts in 2017 and has five suppressed quarters, so it is out of scope. Annual crude rates per 100,000 exist for every series except Canada's ED visits.

The Ontario series have a sharp break at the end of 2024. Opioid deaths were 581 in Q3 2024, 436 in Q4 2024 and 330 in Q1 2025, then 327 to 398 a quarter through Q1 2026. Stimulant deaths went from 569 to 348 over the same three quarters. Opioid hospitalizations fell less, from 540 to 389. Canada fell too: opioid deaths were 1,867 in Q1 2024 and 1,354 in Q1 2026. Before relying on the last few quarters, I should read the data notes for which quarters are preliminary and likely to be revised.

The Canadian Substance Use Survey public-use microdata file is for context only (for example, the share of Ontario respondents reporting past-year use of a stimulant). Any figure taken from it will be a weighted percentage, and cells with small unweighted counts will not be reported.

## Series to forecast

Four Ontario quarterly counts: opioid toxicity deaths, stimulant toxicity deaths, opioid-related poisoning hospitalizations and stimulant-related poisoning hospitalizations. Canada gets the same four series for comparison. Annual crude rates per 100,000 put Ontario and Canada on one scale, since raw counts differ by an order of magnitude. Which of the four series have a full, unsuppressed quarterly history will be settled once the file is profiled; the definitions and coverage notes for each source (deaths from coroners and medical examiners, hospitalizations from hospital discharge data) also need to be read before committing to them.

## Method

1. Profile the file and build a clean quarterly table for Ontario and Canada (script 01).
2. Plot each series and mark the structural breaks the write-up has to explain, such as the jump in 2020.
3. Hold out the last six quarters (Q4 2024 to Q1 2026). Fit on Q1 2016 to Q3 2024. This holdout starts at the break, so it tests how badly each model misses a sudden drop.
4. Compare a seasonal naive baseline, Holt's linear exponential smoothing and a small ARIMA chosen by AIC. Score each on the holdout with MAE and MAPE.
5. Refit on all 41 quarters (33 for stimulant deaths) twice: once as is, and once as an ARIMA with a level-shift dummy from Q4 2024. Forecast Q2 2026 to Q2 2027 with 80% and 95% prediction intervals and report both.
6. Repeat the forecast in Excel (Forecast Sheet, which uses FORECAST.ETS and gives a confidence interval) and in R (forecast or fable package) so the project shows all three tools.
7. Build a Power BI page with the forecast visual on the Ontario series and a Canada comparison page.

The break is the main finding the project has to handle. A model fit through Q3 2024 will over-forecast the holdout, and the write-up should say by how much and why the level-shift model is or is not better.

## Portfolio deliverables

A GitHub repo (ontario-substance-harms-forecast) with a README covering question, data, method, findings, limitations and tools; one forecast chart as the screenshot; a 150-word LinkedIn post; a resume bullet with the holdout error and the forecast range.

## Limitations to state

Counts are the most recent release and earlier quarters get revised. Forecasts extrapolate the past and cannot anticipate a change in the drug supply or in policy. Hospitalization and death definitions differ by source and province, so Ontario versus Canada comparisons use rates and the same source only.
