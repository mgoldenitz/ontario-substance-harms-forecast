"""Compare Ontario with Canada using annual crude rates per 100,000.

2026 is left out because the file only has January to March for that year.
Output: results/ontario_vs_canada_rates.csv, images/ontario_vs_canada_rates.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "raw" / "SubstanceHarmsData.csv", dtype=str)

rates = df[
    (df.Specific_Measure == "Overall numbers")
    & (df.Time_Period == "By year")
    & (df.Unit == "Crude rate")
    & df.Region.isin(["Ontario", "Canada"])
    & df.Source.isin(["Deaths", "Hospitalizations"])
    & df.Year_Quarter.str.fullmatch(r"\d{4}")
    & (df.Year_Quarter != "2026")
].copy()
rates["year"] = rates.Year_Quarter.astype(int)
rates["rate"] = pd.to_numeric(rates.Value, errors="coerce")

wide = rates.pivot_table(index=["Substance", "Source", "year"], columns="Region", values="rate").reset_index()
wide["ontario_minus_canada"] = (wide.Ontario - wide.Canada).round(1)
wide["ontario_pct_of_canada"] = (wide.Ontario / wide.Canada * 100).round(0)
wide.to_csv(ROOT / "results" / "ontario_vs_canada_rates.csv", index=False)
print(wide.to_string(index=False))

panels = [("Opioids", "Deaths"), ("Stimulants", "Deaths"),
          ("Opioids", "Hospitalizations"), ("Stimulants", "Hospitalizations")]
fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True)
for ax, (sub, src) in zip(axes.flat, panels):
    d = wide[(wide.Substance == sub) & (wide.Source == src)]
    ax.plot(d.year, d.Canada, color="#888888", lw=1.6, marker="o", ms=3, label="Canada")
    ax.plot(d.year, d.Ontario, color="#1f77b4", lw=1.6, marker="o", ms=3, label="Ontario")
    ax.set_title(f"{sub[:-1]} {src.lower()}", fontsize=10)
    ax.set_ylim(bottom=0)
axes[0, 0].set_ylabel("Rate per 100,000")
axes[1, 0].set_ylabel("Rate per 100,000")
axes[0, 0].legend(frameon=False, fontsize=8)
fig.suptitle("Ontario and Canada, annual crude rates, 2016 to 2025")
fig.tight_layout()
fig.savefig(ROOT / "images" / "ontario_vs_canada_rates.png", dpi=150)
