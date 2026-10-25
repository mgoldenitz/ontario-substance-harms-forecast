"""Load the Health Infobase substance harms CSV and profile the Ontario and Canada series.

Input: data/raw/SubstanceHarmsData.csv, downloaded from
https://health-infobase.canada.ca/src/doc/SRHD/SubstanceHarmsData.csv
Output: data/processed/series_inventory.csv and data/processed/quarterly_on_ca.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "SubstanceHarmsData.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW, dtype=str)
print(f"{len(df):,} rows, columns: {list(df.columns)}")

# Values can carry suppression markers; keep the raw text and a numeric copy
df["Value_num"] = pd.to_numeric(df["Value"].str.replace(",", ""), errors="coerce")
suppressed = df.loc[df["Value_num"].isna(), "Value"].value_counts()
print("\nNon-numeric values (suppressed or missing):")
print(suppressed.head(10))

for col in ["Substance", "Source", "Specific_Measure", "Time_Period", "Unit"]:
    print(f"\n{col}:")
    print(df[col].value_counts())

# Which series exist for Ontario and Canada, and how far back each goes
keys = ["Substance", "Source", "Specific_Measure", "Region", "Time_Period", "Unit"]
overall = df[
    df["Region"].isin(["Ontario", "Canada"])
    & df["Aggregator"].isna()
    & df["Disaggregator"].isna()
]
inventory = (
    overall.groupby(keys)
    .agg(first=("Year_Quarter", "min"), last=("Year_Quarter", "max"),
         periods=("Year_Quarter", "nunique"), missing=("Value_num", lambda s: s.isna().sum()))
    .reset_index()
)
inventory.to_csv(OUT / "series_inventory.csv", index=False)
print("\nOntario and Canada overall series:")
print(inventory.to_string(index=False))

# Quarterly counts in long form, one row per series per quarter
quarterly = overall[(overall["Time_Period"] == "By quarter") & (overall["Unit"] == "Number")]
quarterly = quarterly[keys + ["Year_Quarter", "Value", "Value_num"]]
quarterly.to_csv(OUT / "quarterly_on_ca.csv", index=False)
print(f"\nWrote {len(quarterly):,} quarterly rows to {OUT / 'quarterly_on_ca.csv'}")
