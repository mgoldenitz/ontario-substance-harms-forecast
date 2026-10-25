"""Write powerbi/powerbi_quarterly.csv: one long table for Power BI.

Rows hold Ontario and Canada actual quarterly counts and the Python ARIMA forecasts
(both variants) for Ontario, with 80% and 95% interval bounds on forecast rows.
Input: data/processed/quarterly_on_ca.csv, results/forecasts.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi"
OUT.mkdir(exist_ok=True)

NAMES = {
    ("Opioids", "Deaths"): "Opioid deaths",
    ("Stimulants", "Deaths"): "Stimulant deaths",
    ("Opioids", "Hospitalizations"): "Opioid hospitalizations",
    ("Stimulants", "Hospitalizations"): "Stimulant hospitalizations",
}


def quarter_start(label):
    p = pd.Period(label.replace(" ", ""), freq="Q")
    return p.start_time.date()


q = pd.read_csv(ROOT / "data" / "processed" / "quarterly_on_ca.csv")
q["key"] = list(zip(q.Substance, q.Source))
q = q[q.key.isin(NAMES) & q.Value_num.notna()]
actual = pd.DataFrame({
    "series": q.key.map(NAMES),
    "region": q.Region,
    "quarter": q.Year_Quarter,
    "row_type": "Actual",
    "variant": "",
    "value": q.Value_num,
})

f = pd.read_csv(ROOT / "results" / "forecasts.csv")
f["series"] = f.series.str.replace("_", " ").str.capitalize()
forecast = pd.DataFrame({
    "series": f.series,
    "region": "Ontario",
    "quarter": f.quarter.str.replace("Q", " Q"),
    "row_type": "Forecast",
    "variant": f.variant,
    "value": f.forecast,
    "lo80": f.lo80, "hi80": f.hi80, "lo95": f.lo95, "hi95": f.hi95,
})

out = pd.concat([actual, forecast], ignore_index=True)
out["quarter_start"] = out.quarter.map(quarter_start)
out = out[["series", "region", "quarter", "quarter_start", "row_type", "variant",
           "value", "lo80", "hi80", "lo95", "hi95"]]
out.sort_values(["series", "region", "row_type", "variant", "quarter_start"]).to_csv(
    OUT / "powerbi_quarterly.csv", index=False)
print(out.groupby(["series", "region", "row_type"]).size())
