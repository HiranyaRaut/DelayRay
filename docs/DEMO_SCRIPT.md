# DelayRay 3-Minute Demo Walkthrough Script

## 0:00 - 0:30: Introduction & Command Center
- **Hook:** "Honorable judges, MoSPI tracks nearly 2,000 infrastructure projects worth ₹26 lakh crore, but conventional monitoring relies on backward-looking reporting after delays have already occurred. DelayRay brings predictive foresight, empirical rigor, and explainable AI to infrastructure monitoring."
- **Screen:** Command Center.
- **Key Actions:**
  - Point out persistent "Synthetic demo data" badge in the header.
  - Review portfolio KPIs: 1,981 projects, ₹4.82 lakh crore expected overrun, ₹3.12 lakh crore Value-at-Risk.
  - Interact with the **Risk Radar** scatter plot: brush over high-cost/high-risk quadrant to filter the dynamic watchlist.
  - Show the **India State Tile-Grid Map** and highlight state-level risk variations.

## 0:30 - 1:15: Deep Dive: The Project Hero Page
- **Screen:** Drill into a critical infrastructure project (e.g. `PRJ-RAIL-0412`).
- **Key Actions:**
  - Highlight the animated **Risk Gauge** (e.g. 84 - Critical Risk) and Value-at-Risk figure.
  - Walk through the **S-Curve Chart**: explain the Planned S-Curve, Actual Progress, and the Conformal P10-P90 forecast cone.
  - Show **Earned Value Cards**: SPI (0.78) and Cost Efficiency (0.71).
  - Open **Why Flagged**: explain the SHAP Waterfall breaking down exactly what drove the score (e.g. Land Acquisition shortfall +21 pts, Steel price shock +14 pts).
  - Demonstrate **What-If Simulation**: move the Land Handover slider from 40% to 80% — watch the risk score drop to 58 (Moderate) in real time.
  - Click **Download Risk Brief (PDF)** to show executive-ready export.

## 1:15 - 2:00: Early Warning & Live Month Advance
- **Screen:** Early Warning Center.
- **Key Actions:**
  - View active alerts organized by Kanban stage (New, Acknowledged, Assigned, Resolved).
  - Click **Advance Month (Demo Mode)** button in the header.
  - Watch as a new monthly snapshot is simulated, new alerts (e.g. R1 Schedule Slippage) pop up live with toast notifications, and scores update.
  - Acknowledge and assign an alert to show complete audit lifecycle.

## 2:00 - 2:45: Empirical Rigor: Model Arena & Ablation Lab
- **Screen:** Model Arena and Ablation Lab.
- **Key Actions:**
  - Address Question (a): *Do AI/ML models outperform conventional baselines?* Show the **Verdict Card** generated from paired bootstrap tests.
  - Address Question (b): *How much predictive power comes from current CUF fields vs external data?*
  - Point to the **CUF Attribution %** hero statistic (e.g. 68.4% of achievable skill comes from CUF; 31.6% requires external indicators).
  - Show the **Ranked Candidate CUF Fields Table** with marginal gain vs collection difficulty.

## 2:45 - 3:00: Guarded Local LLM Assistant & Conclusion
- **Screen:** Guarded Assistant floating drawer.
- **Key Actions:**
  - Ask: *"Which 5 railway projects face the highest Value-at-Risk due to land acquisition?"*
  - Show guarded Text-to-SQL generation and cited response with project IDs and snapshot months.
  - Reiterate offline capability (local Ollama with deterministic fallback) and close.
