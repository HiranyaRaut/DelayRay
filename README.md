# DelayRay: AI-Powered Predictive Analytics & Early Warning System for Infrastructure Projects

[![CI Pipeline](https://github.com/delayray/delayray/actions/workflows/ci.yml/badge.svg)](https://github.com/delayray/delayray/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.3-cyan.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Important Notice:** All demo metrics, project names, and timeline records within this demonstration are generated synthetically. DelayRay outputs are decision-support aids designed to augment human governance and do not replace statutory engineering determinations.

---

## 🌟 Executive Overview
**DelayRay** is an AI-powered early warning and predictive analytics system modelled on the Ministry of Statistics and Programme Implementation (**MoSPI**) **PAIMANA** portal. It tracks central sector infrastructure projects costing ₹150 crore and above across 17 ministries and 22 infrastructure sectors.

### Core Capabilities
1. **Predictive Analytics:** Dual forecasting of cost overrun (%) and schedule delay (months) using tuned gradient boosted ensembles and reference class statistical baselines.
2. **Calibrated Risk Scoring:** 0–100 risk score and categorical bands (*Low, Moderate, High, Critical*) with isotonic probability calibration.
3. **Transparent Explainability:** Granular SHAP waterfall explanations identifying the top-8 causal drivers per project.
4. **Early Warning System (EWS):** Multi-factor automated alert engine (Rules R1–R8) with full lifecycle state management (*New → Acknowledged → Assigned → Resolved*).
5. **Empirical Model Arena:** Paired bootstrap significance testing answering: *Do AI/ML models outperform conventional statistical methods?*
6. **Ablation Lab:** Econometric attribution calculating the **CUF Attribution %** and ranking candidate external data fields by marginal predictive gain versus collection difficulty.
7. **Counterfactual What-If Simulator:** Interactive sliders allowing planners to test the impact of interventions (e.g., accelerating land acquisition) before committing capital.
8. **Air-Gapped Local LLM Assistant:** Guarded Text-to-SQL layer via `sqlglot` and RAG over project remarks running 100% offline via local Ollama.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite (WAL mode) / PostgreSQL, Alembic, APScheduler, sqlglot, ReportLab, pytest.
- **Machine Learning:** LightGBM, XGBoost, Scikit-learn, lifelines (survival analysis), SHAP, Optuna, statsmodels, scipy, joblib.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui (Radix), Framer Motion, TanStack Query, TanStack Table, Apache ECharts, lucide-react.
- **LLM & RAG:** Local Ollama (`llama3.1:8b`, `nomic-embed-text`), FAISS / Chroma vector search, guarded text-to-SQL with single-SELECT and allowlisted analytical views.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11 or 3.12
- Node.js 20 LTS or newer
- (Optional) Docker Desktop
- (Optional) Ollama with `llama3.1:8b` and `nomic-embed-text`

### 1. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/your-org/delayray.git
cd DelayRay

# Copy environment variables
cp .env.example .env

# Run automated setup (installs backend and frontend dependencies)
make setup
# On Windows without make:
# .\make.bat setup
```

### 2. Run Local Development Servers
```bash
make dev
# On Windows:
# .\make.bat dev
```
- **Web UI:** [http://localhost:5173](http://localhost:5173)
- **FastAPI API:** [http://localhost:8000](http://localhost:8000)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Demo Credentials
| Role | Email | Password | Access Level |
|---|---|---|---|
| **Viewer** | `viewer@demo` | `demo123` | Read-only inspection of dashboards & projects |
| **Analyst** | `analyst@demo` | `demo123` | What-if simulation, export briefs, filter radar |
| **Admin** | `admin@demo` | `demo123` | Alert rules tuning, retrain/rescore trigger, audit log |

---

## 📂 Repository Layout
```
/
├─ docs/            # Master spec, architecture, methodology, model card, data dictionary
├─ backend/         # FastAPI application, SQLAlchemy models, EWS engine, guarded assistant
├─ frontend/        # React 18 + Vite + Tailwind + shadcn Mission Control dashboard
├─ scripts/         # Synthetic data generator, training, evaluation, ablation, demo launcher
├─ ml_artifacts/    # Trained models, evaluation reports, and figures
├─ data/            # Synthetic, real, and external indicator datasets
├─ docker-compose.yml
├─ Makefile
├─ make.bat
└─ README.md
```

---

## 🧪 Testing & Verification
```bash
# Run backend test suite
make test

# Run code style & lint checks
make lint
```
