# DelayRay Solution Architecture Document: Sections 1-5

## Section 1: System Overview & Theoretical Underpinnings
DelayRay addresses the fundamental informational asymmetries and cognitive delays in mega-infrastructure portfolio management. By unifying 20 years of historical execution patterns with real-time monthly snapshot data, DelayRay establishes a dual-paradigm intelligence layer:
1. **Statistical & Econometric Baselines:** Grounded in reference class forecasting (Flyvbjerg), sector-median Bayesian priors, and classical Earned Value Analysis (EVM / SPI / CPI).
2. **Non-linear Machine Learning & Survival Analytics:** Gradient boosted ensembles (XGBoost, LightGBM, Random Forest), calibrated probabilities via isotonic regression, conformal prediction intervals (P10, P50, P90), and semi-parametric Cox Proportional Hazards for time-to-delay modeling.

## Section 2: Data Engineering & Realistic Synthetic Data Generation
Because public infrastructure portals protect sensitive contractual data while publishing aggregated flash reports, DelayRay features a calibrated data synthesis generator (`scripts/generate_data.py`):
- **Cohort Scale:** 7,500 historical completed projects (2006–2022) with multiple lifecycle checkpoints (25%, 50%, 75% duration) and 1,981 ongoing projects with full monthly snapshot histories up to April 2026.
- **Latent Data Generating Process:** Ground-truth non-linear interaction terms (e.g. land acquisition deficit interacting with mountainous terrain; commodity price shocks hitting early-stage heavy civil engineering).
- **Mess & Realism:** Systematic missingness (MAR/MNAR 5–15%), reporting lags, unit transposition errors, and semi-structured free-text progress remarks.
- **Zero Leakage Invariant:** Features are computed strictly *as-of* the snapshot date. No future outcomes or final revisions appear in training features.

## Section 3: Feature Taxonomy & Group Ablation Architecture
Features are structured into six distinct groups (G1 through G6) to enable formal econometric attribution:
- **G1: CUF Static (Administrative Baseline):** Ministry, sector, funding mode, original sanctioned cost, initial planned duration.
- **G2: CUF Dynamic (Progress Tracking):** Cumulative expenditure, physical progress percentage, elapsed time percentage, revision counts.
- **G3: Derived Earned Value Metrics:** Schedule Performance Index (SPI = Physical / Planned), Cost Efficiency (CPI = Physical / Expenditure), 3-month velocity slopes, milestone slip ratios.
- **G4: Unstructured Text / NLP:** TF-IDF + TruncatedSVD and LLM-extracted challenge tags (land, forest, utility, contractor, legal, weather).
- **G5: Macroeconomic & Climate Regimes:** State-level precipitation anomalies, AR(1) steel, cement, and crude oil indices with injected historical shocks (including the 2020-2021 COVID shock).
- **G6: Project-Specific Latent Risk Factors:** Initial land acquisition percentage, environmental clearance delays, utility shifting count, contractor concurrent workload, geotechnical risk score.

## Section 4: Early Warning System & Lifecycle Playbook
An automated rule engine evaluates monthly updates against multi-factor triggers:
- **R1:** Persistent schedule slippage (SPI < 0.85 for 3 consecutive months).
- **R2:** Spend-progress divergence (Spend % - Physical % > 10%).
- **R3:** Model risk spike (Score >= 75 or single-month jump >= 15 pts).
- **R4:** Anticipated completion slip > 6 months.
- **R5:** Stalled physical progress despite time elapsing.
- **R6:** Consecutive milestone misses.
- **R7:** Multi-dimensional trajectory anomaly (IsolationForest top 2%).
- **R8:** Critical natural language flags in remarks.
Lifecycle: New -> Acknowledged -> Assigned -> Resolved / Dismissed, tracked with comprehensive audit logs and mitigation playbooks.

## Section 5: Air-gapped Generative AI & Guarded Analytics
To satisfy government security protocols:
- Operates 100% offline via local Ollama instances (e.g. `llama3.1:8b`, `qwen2.5:3b`, `nomic-embed-text`).
- Guarded text-to-SQL layer using `sqlglot` strictly constrained to read-only analytical views (`vw_*`), enforcing parameterized `LIMIT 200` queries and stripping unsafe DDL/DML.
- Retrieval-Augmented Generation (RAG) over vector-indexed snapshot remarks with explicit citation lineage (Project ID, Snapshot Month).
- Robust deterministic fallback when local LLM services are offline.
