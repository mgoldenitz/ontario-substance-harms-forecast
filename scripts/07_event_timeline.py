"""Ontario quarterly deaths with dated policy and drug-supply events drawn on the chart.

The events are annotations only. They are not inputs to any model.

Input: data/processed/quarterly_on_ca.csv (from 01_load_and_profile.py)
       data/events.csv (dates, sources and links found through Google News)
Output: images/event_timeline.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
START = pd.Period("2022Q1", freq="Q")
DROP = pd.Period("2024Q4", freq="Q")


def ontario_deaths(q, substance):
    s = q[(q.Substance == substance) & (q.Source == "Deaths") & (q.Region == "Ontario")]
    s = s.set_index("period")["Value_num"].sort_index()
    return s[s.index >= START]


q = pd.read_csv(ROOT / "data" / "processed" / "quarterly_on_ca.csv")
q["period"] = pd.PeriodIndex(q["Year_Quarter"].str.replace(" ", ""), freq="Q")
events = pd.read_csv(ROOT / "data" / "events.csv", parse_dates=["date"])

fig, ax = plt.subplots(figsize=(10, 5))
for substance, word, colour in [("Opioids", "Opioid", "#d62728"), ("Stimulants", "Stimulant", "#1f77b4")]:
    s = ontario_deaths(q, substance)
    ax.plot(s.index.to_timestamp(), s.to_numpy(), color=colour, lw=1.8, marker="o", ms=3,
            label=f"{word} deaths")
last = s.index[-1].to_timestamp(how="end")
assert events["date"].between(START.to_timestamp(), last).all(), "event outside chart range"

ax.axvspan(DROP.to_timestamp(), last, color="grey", alpha=0.08, label="Drop from Q4 2024")
top = ax.get_ylim()[1]
for i, row in enumerate(events.itertuples(), start=1):
    ax.axvline(row.date, color="black", lw=0.8, ls=":")
    # day 1 marks a monthly value, so show only the month
    when = f"{row.date:%b %Y}" if row.date.day == 1 else f"{row.date:%d %b %Y}"
    ax.annotate(f"{i}. {row.short_label}\n{when}",(row.date, top * (0.97 - 0.09 * (i - 1))),
                xytext=(4, 0), textcoords="offset points", fontsize=8, va="top")

ax.set_title("Ontario opioid and stimulant deaths per quarter, with policy and drug-supply events")
ax.set_ylabel("Deaths per quarter")
ax.set_xlabel("Each point is drawn at the start of its quarter")
ax.set_ylim(bottom=0)
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig(ROOT / "images" / "event_timeline.png", dpi=150)
print(events[["date", "short_label", "source"]].to_string(index=False))
