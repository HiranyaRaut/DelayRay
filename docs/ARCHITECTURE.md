# DelayRay Architecture Specification

## 1. High-Level Architecture

```mermaid
flowchart TB
    subgraph Ingestion & Storage
        GEN[Data Generator] --> DB[(SQLite / PostgreSQL)]
        EXT[Macro / Weather Feed] --> DB
        DB --> VIEWS[Read-Only Analytical Views]
        DB --> FAISS[(FAISS / Chroma Vector Index)]
    end

    subgraph Analytics & EWS
        VIEWS --> DATASET[As-Of Datasets]
        DATASET --> ML[LightGBM / XGBoost / Baselines]
        ML --> CALIB[Isotonic Calibrator 0-100]
        ML --> CONF[Split Conformal P10-P90]
        ML --> SHAP[SHAP TreeExplainer]
        CALIB --> EWS[Rule Engine R1-R8]
        EWS --> LIFECYCLE[Alert Lifecycle]
    end

    subgraph Air-Gapped Assistant
        LLM[Local Ollama / Llama 3.1]
        FAISS --> RAG[Remarks Retriever]
        VIEWS --> SQLGUARD[sqlglot Guarded SQL]
        RAG --> ROUTER[Intent Router]
        SQLGUARD --> ROUTER
        ROUTER --> LLM
    end

    subgraph Mission Control Frontend
        SHELL[Vite + React + Tailwind + shadcn]
        SHELL --> CC[Command Center & Risk Radar]
        SHELL --> PRJ[Project Detail Hero & S-Curve]
        SHELL --> ARENA[Model Arena & Verdict]
        SHELL --> ABLATION[Ablation Lab & Policy Note]
        SHELL --> ALERTS[Early Warning Center]
        SHELL --> CHAT[Guarded Assistant Chat]
    end

    LIFECYCLE & SHAP & CALIB & CONF -->|FastAPI REST + SSE| SHELL
    LLM -->|Streaming SSE| CHAT
```

## 2. Component Responsibilities
- **Data Layer:** Maintains temporal fidelity; monthly snapshots store as-of measurements. Read-only SQL views isolate analytical access.
- **ML Engine:** Implements group-aware, time-aware backtesting (splits: train <= 2016, val 2017-2018, test >= 2019). Produces calibrated 0-100 risk scores and P10-P90 conformal bounds.
- **Prescriptive & Early Warning:** Rule triggers evaluate SPI erosion, cost-progress divergence, and critical bottleneck tags. Lifecycle enforces state progression and cooldown windows.
- **Guarded Assistant:** Text-to-SQL parsing strictly filters queries through `sqlglot` against allowlisted views with forced `LIMIT 200`. Vector store extracts cited remarks.
- **Mission Control UI:** Modern dark-theme control room optimized for executive and analytical oversight.
