# Power BI page: steps

These steps build two report pages from `powerbi/powerbi_quarterly.csv` and `results/ontario_vs_canada_rates.csv`. The first page shows Ontario's actual counts with the ARIMA forecast and its intervals. The second compares Ontario with Canada. A third, optional page uses Power BI's own forecast feature so it can be compared with the Python model.

## Load the data

1. Get data > Text/CSV > `powerbi/powerbi_quarterly.csv` > Transform Data.
2. In Power Query, set `quarter_start` to Date, `value`, `lo80`, `hi80`, `lo95` and `hi95` to Decimal number, and the rest to Text. Close & Apply.
3. Get data > Text/CSV > `results/ontario_vs_canada_rates.csv`. Set `year` to Whole number and `Canada`, `Ontario`, `ontario_minus_canada` and `ontario_pct_of_canada` to Decimal number.
4. Select `quarter_start` in the Data pane and turn off the auto date hierarchy for it (or turn off Auto date/time under File > Options > Current file > Data load), so the axis is a continuous date.

## Measures

Create these in the `powerbi_quarterly` table:

```
Actual = CALCULATE(SUM(powerbi_quarterly[value]), powerbi_quarterly[row_type] = "Actual")
Forecast = CALCULATE(SUM(powerbi_quarterly[value]), powerbi_quarterly[row_type] = "Forecast")
Low 95 = SUM(powerbi_quarterly[lo95])
High 95 = SUM(powerbi_quarterly[hi95])
Low 80 = SUM(powerbi_quarterly[lo80])
High 80 = SUM(powerbi_quarterly[hi80])
Last actual = 
    VAR maxActualDate = CALCULATE(MAX(powerbi_quarterly[quarter_start]), powerbi_quarterly[row_type] = "Actual")
    RETURN CALCULATE([Actual], powerbi_quarterly[quarter_start] = maxActualDate)
```

## Page 1: Ontario forecast

1. Add a slicer for `series` (single select).
2. Add page-level filters: `region` is Ontario, and `variant` is "(Blank)" or "Level shift from 2024 Q4". Actual rows have a blank variant, so both boxes need to be ticked. Tick "No level shift" instead to see the other model.
3. Add a line chart. X-axis: `quarter_start` (type Continuous). Y-axis: Actual, Forecast, Low 95 and High 95. Format Low 95 and High 95 as thin dashed grey lines.
4. Add a card with Last actual and a card with Forecast filtered to 2027 Q2.
5. Add a text box: "ARIMA fit in Python on Q1 2016 to Q1 2026 (stimulant deaths from Q1 2018). Dashed lines are the 95% prediction interval. Source: Health Infobase, downloaded 25 October 2026."

## Page 2: Ontario vs Canada

1. Line chart from `ontario_vs_canada_rates`: X-axis `year`, Y-axis `Ontario` and `Canada`, with a slicer on `Substance` and `Source`.
2. Table with year, Ontario, Canada and ontario_pct_of_canada.
3. Text box: "Annual crude rates per 100,000. 2026 is left out because only January to March is available. Canada includes Ontario."

## Page 3 (optional): Power BI's built-in forecast

1. Line chart with X-axis `quarter_start` (Continuous) and Y-axis Actual only; filter `region` to Ontario and `series` to one series. The Forecast option appears only when the chart has a single measure and no legend.
2. Analytics pane > Forecast > Add. Units: Points. Forecast length: 5. Confidence interval: 95%. Seasonality: 4.
3. Set Ignore last to 6 to see what Power BI's model would have predicted for the holdout quarters (Q4 2024 to Q1 2026), then set it back to 0 for the real forecast.
4. Power BI uses its own exponential smoothing model, so its numbers will differ from the Python ARIMA and from Excel's FORECAST.ETS.

Save the report as `powerbi/ontario_substance_harms.pbix` and export page 1 as a PNG to `images/powerbi_forecast.png` for the README.
