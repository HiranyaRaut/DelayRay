# DelayRay Methodology & Statistical Rigor

## 1. Zero-Leakage Invariant
All features used in training and evaluation are computed strictly *as-of* the snapshot date:
- Outcome metrics (`final_cost_cr`, `actual_completion_date`, `cost_overrun_pct`, `time_overrun_months`) are isolated in the `project_outcomes` table and never accessed by feature extractors.
- Revisions are included only if approved prior to or on the snapshot month.
- Automated leak-detection tests assert no temporal leakage.

## 2. Validation & Split Strategy
Never use random splits for time-series infrastructure projects. DelayRay employs:
- **Group-Aware Temporal Splits:** All snapshots of any given project belong to exactly one split.
  - **Train:** Projects with sanction/start date <= 2016.
  - **Validation:** Projects starting 2017 - 2018 (used strictly for Optuna hyperparameter tuning and isotonic calibration).
  - **Test (Out-of-Time Benchmark):** Projects starting >= 2019 and completed, touched only once during final model scoring.
- **Rolling-Origin Backtesting:** Evaluates predictive resilience over sequential economic cycles.

## 3. Probability Calibration & Conformal Intervals
- Binary classification probabilities are calibrated using **Isotonic Regression** on the hold-out validation set.
- We report Brier score, Expected Calibration Error (ECE), and reliability diagrams.
- 0-100 Risk Score = Calibrated Probability × 100.
- Prediction intervals for regression (P10, P50, P90) are derived using **split conformal calibration** guaranteeing nominal marginal coverage.

## 4. Empirical Significance Testing & Honest Verdict
To answer whether ML outperforms conventional baselines:
- We compute paired bootstrap distributions (1,000 resamples over projects) for Delta-MAE and Delta-AUC.
- A Wilcoxon signed-rank test on absolute errors determines statistical significance.
- An automated rule requires both the 95% CI to exclude zero AND the practical effect size to exceed 5% before emitting an "ML significantly better" verdict. Otherwise, the system transparently recommends the statistical baseline.

## 5. Econometric CUF Feature Attribution
The ablation study systematically removes and adds feature groups (G1 through G6) to calculate:
$$\text{CUF Attribution } \% = \frac{\text{Skill}(\text{CUF Static + Progress})}{\text{Skill}(\text{All Groups})} \times 100$$
Candidate external fields are ranked by marginal AUC/MAE gain divided by empirical collection difficulty.
