"""Holdout comparison and forecasts for four Ontario quarterly series.

Train: first quarter to 2024 Q3. Test: 2024 Q4 to 2026 Q1 (6 quarters).
Models: seasonal naive (m = 4), Holt with damped trend, ARIMA chosen by AIC.
Final forecasts: ARIMA refit on all quarters, with and without a level-shift
dummy from 2024 Q4, for 2026 Q2 to 2027 Q2 with 80% and 95% intervals.

Input: data/processed/quarterly_on_ca.csv (from 01_load_and_profile.py)
Output: results/holdout_metrics.csv, results/holdout_predictions.csv,
        results/forecasts.csv, images/holdout_<series>.png, images/forecast_<series>.png
"""
import itertools
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
IMAGES = ROOT / "images"
RESULTS.mkdir(exist_ok=True)
IMAGES.mkdir(exist_ok=True)

TRAIN_END = pd.Period("2024Q3", freq="Q")
BREAK = pd.Period("2024Q4", freq="Q")
HORIZON = 5  # 2026 Q2 to 2027 Q2

SERIES = {
    "opioid_deaths": ("Opioids", "Deaths"),
    "stimulant_deaths": ("Stimulants", "Deaths"),
    "opioid_hospitalizations": ("Opioids", "Hospitalizations"),
    "stimulant_hospitalizations": ("Stimulants", "Hospitalizations"),
}

q = pd.read_csv(ROOT / "data" / "processed" / "quarterly_on_ca.csv")
q["period"] = pd.PeriodIndex(q["Year_Quarter"].str.replace(" ", ""), freq="Q")


def get_series(substance, source, region="Ontario"):
    s = q[(q.Substance == substance) & (q.Source == source) & (q.Region == region)]
    return s.set_index("period")["Value_num"].sort_index().astype(float)


def seasonal_naive(train, h):
    last_year = train.iloc[-4:].to_numpy()
    return np.array([last_year[i % 4] for i in range(h)])


def holt(train, h):
    fit = ExponentialSmoothing(train.to_numpy(), trend="add", damped_trend=True).fit()
    return fit.forecast(h)


def best_arima(y, exog=None):
    """Grid search p, q in 0..2 and d in 0..1; keep the lowest AIC."""
    best = None
    for p, d, qq in itertools.product(range(3), range(2), range(3)):
        trend = "c" if d == 0 else "n"
        try:
            fit = ARIMA(y, exog=exog, order=(p, d, qq), trend=trend).fit()
        except Exception:
            continue
        if best is None or fit.aic < best[1].aic:
            best = ((p, d, qq), fit)
    return best


def mae(actual, pred):
    return float(np.mean(np.abs(actual - pred)))


def mape(actual, pred):
    return float(np.mean(np.abs((actual - pred) / actual)) * 100)


metrics, predictions, forecasts = [], [], []

for name, (substance, source) in SERIES.items():
    y = get_series(substance, source)
    train, test = y[y.index <= TRAIN_END], y[y.index > TRAIN_END]
    h = len(test)
    y_train = train.to_numpy()

    order, arima_fit = best_arima(y_train)
    arima_fc = arima_fit.get_forecast(h)
    arima_ci = arima_fc.conf_int(alpha=0.05)
    preds = {
        "Seasonal naive": seasonal_naive(train, h),
        "Holt (damped)": holt(train, h),
        f"ARIMA{order}": arima_fc.predicted_mean,
    }
    covered = np.mean((test.to_numpy() >= arima_ci[:, 0]) & (test.to_numpy() <= arima_ci[:, 1]))

    for model, p in preds.items():
        p = np.asarray(p)
        metrics.append({
            "series": name, "model": model, "train_quarters": len(train),
            "MAE": round(mae(test.to_numpy(), p), 1),
            "MAPE": round(mape(test.to_numpy(), p), 1),
            "mean_error": round(float(np.mean(p - test.to_numpy())), 1),
            "pi95_coverage": round(covered * 100) if model.startswith("ARIMA") else None,
        })
        for per, a, f in zip(test.index, test.to_numpy(), p):
            predictions.append({"series": name, "model": model, "quarter": str(per),
                                "actual": a, "predicted": round(float(f), 1)})

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(y.index.to_timestamp(), y.to_numpy(), color="black", lw=1.6, label="Actual")
    test_x = test.index.to_timestamp()
    for (model, p), c in zip(preds.items(), ["#888888", "#1f77b4", "#d62728"]):
        ax.plot(test_x, p, color=c, lw=1.4, ls="--", label=model)
    ax.fill_between(test_x, arima_ci[:, 0], arima_ci[:, 1], color="#d62728", alpha=0.12,
                    label="ARIMA 95% interval")
    ax.axvline(BREAK.to_timestamp(), color="grey", lw=0.8, ls=":")
    ax.set_title(f"Ontario {name.replace('_', ' ')}: holdout Q4 2024 to Q1 2026")
    ax.set_ylabel("Count per quarter")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(IMAGES / f"holdout_{name}.png", dpi=150)
    plt.close(fig)

    # Final forecasts on all quarters, with and without a level shift from 2024 Q4
    y_all = y.to_numpy()
    future = pd.period_range(y.index[-1] + 1, periods=HORIZON, freq="Q")
    shift = (y.index >= BREAK).astype(float).reshape(-1, 1)
    variants = {
        "No level shift": (best_arima(y_all), None),
        "Level shift from 2024 Q4": (best_arima(y_all, exog=shift), np.ones((HORIZON, 1))),
    }
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(y.index.to_timestamp(), y.to_numpy(), color="black", lw=1.6, label="Actual")
    for (variant, ((order_v, fit), exog_f)), c in zip(variants.items(), ["#1f77b4", "#d62728"]):
        fc = fit.get_forecast(HORIZON, exog=exog_f)
        ci80, ci95 = fc.conf_int(alpha=0.20), fc.conf_int(alpha=0.05)
        mean = np.asarray(fc.predicted_mean)
        for i, per in enumerate(future):
            forecasts.append({
                "series": name, "variant": variant, "order": str(order_v),
                "aic": round(fit.aic, 1), "quarter": str(per), "forecast": round(mean[i], 1),
                "lo80": round(ci80[i, 0], 1), "hi80": round(ci80[i, 1], 1),
                "lo95": round(ci95[i, 0], 1), "hi95": round(ci95[i, 1], 1),
            })
        fx = future.to_timestamp()
        ax.plot(fx, mean, color=c, lw=1.4, ls="--", label=f"{variant}, ARIMA{order_v}")
        ax.fill_between(fx, ci95[:, 0], ci95[:, 1], color=c, alpha=0.12)
        ax.fill_between(fx, ci80[:, 0], ci80[:, 1], color=c, alpha=0.18)
    ax.set_title(f"Ontario {name.replace('_', ' ')}: forecast Q2 2026 to Q2 2027 (80% and 95% intervals)")
    ax.set_ylabel("Count per quarter")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(IMAGES / f"forecast_{name}.png", dpi=150)
    plt.close(fig)

metrics = pd.DataFrame(metrics)
metrics.to_csv(RESULTS / "holdout_metrics.csv", index=False)
pd.DataFrame(predictions).to_csv(RESULTS / "holdout_predictions.csv", index=False)
forecasts = pd.DataFrame(forecasts)
forecasts.to_csv(RESULTS / "forecasts.csv", index=False)

pd.set_option("display.width", 200)
print(metrics.to_string(index=False))
print()
print(forecasts.to_string(index=False))
