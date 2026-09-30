# Problem Statement: AI-Powered Predictive Analytics and Early Warning System for Central Sector Infrastructure Projects

## Background
The Ministry of Statistics and Programme Implementation (MoSPI), Government of India, monitors central sector infrastructure projects costing ₹150 crore and above through the **PAIMANA** (Project Appraisal, Implementation, Monitoring and Analysis) portal. Currently, about **1,981 projects** spanning **17 ministries** and **22 infrastructure sectors** (such as Railways, Road Transport & Highways, Power, Petroleum, Telecommunications, Civil Aviation, Urban Development, Atomic Energy, etc.) are monitored each month.

Historically, infrastructure mega-projects experience substantial schedule delays and cost overruns due to a combination of:
- Land acquisition disputes and right-of-way handover delays
- Environmental and forest clearance bottlenecks
- Utility shifting complexities and geotechnical uncertainties
- Contractor capacity constraints and multi-project overextension
- Design changes mid-execution and fund flow intermittency
- Macroeconomic commodity price fluctuations (steel, cement, crude) and localized climate events (monsoon anomalies)

## Core Challenges with Conventional Monitoring
1. **Lagging Indicators:** Conventional Earned Value Management (EVM) and reporting mechanisms rely on progress reported after delays have already crystallized.
2. **Subjective Red Flags:** Milestone tracking lacks probabilistic foresight and fails to quantify confidence intervals (Value at Risk / Expected Overrun in ₹ Crore).
3. **Black-box Decision Paralysis:** Field engineers and policy officers require transparent, explainable root causes (SHAP-level drivers) before sanctioning interventions.
4. **Data Blindspots:** Existing Common Uniform Formats (CUF) capture static administrative data and reported progress, but omit external macroeconomic, regulatory, and contractor risk variables.

## Objectives
1. **Predictive Analytics:** Train time-aware, leak-free regression, classification, and survival models to forecast cost overrun (%), schedule delay (months), and high-risk classifications.
2. **Early Warning System (EWS):** Real-time automated rule and anomaly detection engines with full alert lifecycles (new → acknowledged → assigned → resolved).
3. **Rigorous Empirical Comparison:** Determine whether AI/ML models offer statistically significant gains over conventional statistical baselines (sector median, linear regression, EVM schedule/cost forecasts).
4. **CUF Value-Add & Ablation:** Quantify the exact percentage of predictive skill derived from current CUF fields vs external indicators (G1-G6 feature groups), providing a policy-grade prioritized roadmap for new data collection.
5. **Interactive Mission Control:** Deliver a fast, responsive, accessible web UI with interactive S-curves, SHAP waterfalls, what-if simulations, peer benchmarking, automated risk briefs, and an air-gapped local LLM assistant.
