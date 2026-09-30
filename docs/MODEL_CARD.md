# DelayRay Model Card

## Model Details
- **Developer:** DelayRay Engineering Team
- **Model Tasks:**
  - T1: Cost Overrun % Prediction (Regression)
  - T2: Delay Months Prediction (Regression)
  - T3: High-Risk Classification (Calibrated 0-100 Score)
  - T4: Time-to-Delay Survival Analysis (Cox PH / Kaplan-Meier)
  - T5: Prediction Intervals (P10, P50, P90 via Split Conformal Quantile GBM)
- **Model Types:** LightGBM, XGBoost, Random Forest, Stacked Regressor, Reference Baselines (Sector-median, EVM EAC / Schedule).

## Intended Use
- **Primary Use:** Decision support and early warning monitoring for MoSPI and line ministry project appraisal divisions.
- **Out of Scope:** Automatic contractual penalties, replacing statutory engineer certifications, or judicial arbitration evidence.

## Training Data & Splits
- **Source:** Calibrated synthetic dataset mirroring 1,981 ongoing projects and 7,500 historical projects across 17 ministries and 22 sectors.
- **Split Scheme:** Group-aware time split (Train <= 2016, Val 2017-2018, Test >= 2019). Zero leakage enforced across snapshot time boundaries.

## Performance Metrics & Evaluation
- **Regression:** MAE, RMSE, R2, Median Absolute Error, Skill Score relative to Sector Median.
- **Classification:** ROC-AUC, PR-AUC, Brier Score, Expected Calibration Error (ECE).
- **Lead-Time:** Earliest warning month gained at fixed 10% false-alarm threshold.
- **Statistical Significance:** Paired bootstrap (1,000 iterations) with 95% confidence intervals against conventional baselines.

## Ethical Considerations & Human Advisory
- **Synthetic Data Notice:** All demo figures are synthetic.
- **Advisory Only:** All scores and recommendations are advisory tools designed to guide human supervision.
