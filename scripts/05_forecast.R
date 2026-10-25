# Holdout test and forecasts in R with the forecast package.
# Same design as 02_holdout_and_forecast.py: train to 2024 Q3, test 2024 Q4 to 2026 Q1,
# then refit on all quarters and forecast 2026 Q2 to 2027 Q2 with 80% and 95% intervals.
# Models: seasonal naive, ets() chosen automatically, auto.arima(), and auto.arima()
# with a level-shift regressor from 2024 Q4 for the final forecast.
# Run from the repository root: Rscript scripts/05_forecast.R

library(forecast)

q <- read.csv("data/processed/quarterly_on_ca.csv", stringsAsFactors = FALSE)
q <- q[q$Region == "Ontario", ]

series <- list(
  opioid_deaths = c("Opioids", "Deaths"),
  stimulant_deaths = c("Stimulants", "Deaths"),
  opioid_hospitalizations = c("Opioids", "Hospitalizations"),
  stimulant_hospitalizations = c("Stimulants", "Hospitalizations")
)

to_ts <- function(substance, source) {
  d <- q[q$Substance == substance & q$Source == source & !is.na(q$Value_num), ]
  d <- d[order(d$Year_Quarter), ]
  year <- as.integer(substr(d$Year_Quarter[1], 1, 4))
  qtr <- as.integer(substr(d$Year_Quarter[1], 7, 7))
  ts(d$Value_num, start = c(year, qtr), frequency = 4)
}

dir.create("results", showWarnings = FALSE)
dir.create("images", showWarnings = FALSE)
metrics <- list()
forecasts <- list()

for (name in names(series)) {
  y <- to_ts(series[[name]][1], series[[name]][2])
  train <- window(y, end = c(2024, 3))
  test <- window(y, start = c(2024, 4))
  h <- length(test)

  fits <- list(
    "Seasonal naive" = snaive(train, h = h, level = 95),
    "ETS" = forecast(ets(train), h = h, level = 95),
    "auto.arima" = forecast(auto.arima(train), h = h, level = 95)
  )
  for (model in names(fits)) {
    fc <- fits[[model]]
    acc <- accuracy(fc, test)
    inside <- sum(test >= fc$lower[, 1] & test <= fc$upper[, 1])
    metrics[[length(metrics) + 1]] <- data.frame(
      series = name, model = model, spec = fc$method,
      MAE = round(acc["Test set", "MAE"], 1),
      MAPE = round(acc["Test set", "MAPE"], 1),
      mean_error = round(-acc["Test set", "ME"], 1),  # forecast minus actual
      inside_95 = paste(inside, "of", h)
    )
  }

  # Final forecasts on all quarters, with and without a level shift from 2024 Q4
  shift <- as.numeric(time(y) >= 2024.75)
  fit_plain <- auto.arima(y)
  fit_shift <- auto.arima(y, xreg = cbind(shift = shift))
  fc_plain <- forecast(fit_plain, h = 5, level = c(80, 95))
  fc_shift <- forecast(fit_shift, xreg = cbind(shift = rep(1, 5)), level = c(80, 95))

  for (v in list(list("No level shift", fc_plain), list("Level shift from 2024 Q4", fc_shift))) {
    fc <- v[[2]]
    tt <- time(fc$mean)
    forecasts[[length(forecasts) + 1]] <- data.frame(
      series = name, variant = v[[1]], model = fc$method,
      quarter = paste0(floor(tt), " Q", round((tt - floor(tt)) * 4) + 1),
      forecast = round(as.numeric(fc$mean), 1),
      lo80 = round(as.numeric(fc$lower[, 1]), 1), hi80 = round(as.numeric(fc$upper[, 1]), 1),
      lo95 = round(as.numeric(fc$lower[, 2]), 1), hi95 = round(as.numeric(fc$upper[, 2]), 1)
    )
  }

  png(file.path("images", paste0("r_forecast_", name, ".png")), width = 1350, height = 675, res = 150)
  plot(fc_shift, main = paste("Ontario", gsub("_", " ", name), "- R auto.arima with level shift"),
       ylab = "Count per quarter", fcol = "#d62728", shadecols = c("#f4c7c7", "#e89a9a"))
  dev.off()
}

metrics <- do.call(rbind, metrics)
forecasts <- do.call(rbind, forecasts)
write.csv(metrics, "results/r_holdout_metrics.csv", row.names = FALSE)
write.csv(forecasts, "results/r_forecasts.csv", row.names = FALSE)
print(metrics, row.names = FALSE)
print(forecasts, row.names = FALSE)
