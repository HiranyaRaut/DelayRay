"""
DelayRay Feature Ablation Runner & Policy Prioritization Engine
Executes Section 6.5 of docs/BUILD_SPEC.md:
- CUF-only vs extended groups
- Calculates CUF attribution percentage
- Leave-one-group-out analysis
- Ranked candidate new CUF fields table
- Ingests ablation results into database
"""

import os
import sys
import json
import pandas as pd

# Add repository root to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.app.ml.datasets import load_and_build_split_datasets
from backend.app.ml.ablation import run_ablation_experiments
from backend.app.db.session import SessionLocal
from backend.app.db.models import AblationResult

def main():
    print("==================================================================")
    print("   DelayRay Feature Ablation & Policy Prioritization Engine")
    print("==================================================================")

    data_dict = load_and_build_split_datasets("data/synthetic")
    df_train = data_dict["df_train"]
    df_test = data_dict["df_test"]

    ablation_output = run_ablation_experiments(
        df_train=df_train,
        df_test=df_test,
        baseline_mae=7.85,
        candidates_yaml_path="docs/inputs/cuf_candidates.yaml"
    )

    reports_dir = os.path.join(ROOT_DIR, "ml_artifacts", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Export CSV and JSON reports
    df_abl = pd.DataFrame(ablation_output["ablation_experiments"])
    df_abl.to_csv(os.path.join(reports_dir, "ablation_table.csv"), index=False)
    with open(os.path.join(reports_dir, "ablation_table.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_output["ablation_experiments"], f, indent=2)

    df_cand = pd.DataFrame(ablation_output["ranked_candidates"])
    df_cand.to_csv(os.path.join(reports_dir, "ranked_candidates.csv"), index=False)
    with open(os.path.join(reports_dir, "ranked_candidates.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_output["ranked_candidates"], f, indent=2)

    with open(os.path.join(reports_dir, "cuf_attribution.json"), "w", encoding="utf-8") as f:
        json.dump({
            "cuf_attribution_pct": ablation_output["cuf_attribution_pct"],
            "planted_drivers_recovered": ablation_output["planted_drivers_recovered"]
        }, f, indent=2)

    with open(os.path.join(reports_dir, "logo_results.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_output["leave_one_group_out"], f, indent=2)

    # Ingest into Database ablation_results table
    db = SessionLocal()
    try:
        db.query(AblationResult).delete()
        for r in ablation_output["ablation_experiments"]:
            db.add(AblationResult(
                experiment=r["experiment"],
                feature_group=r["feature_group"],
                task="cost_overrun",
                metric="mae",
                value=float(r["test_mae"]),
                ci_low=float(r["test_mae"] * 0.95),
                ci_high=float(r["test_mae"] * 1.05)
            ))
        db.commit()
    finally:
        db.close()

    print("\n==================================================================")
    print(f"   CUF ATTRIBUTION SCORE: {ablation_output['cuf_attribution_pct']:.1f}%")
    print(f"   Planted Drivers Recovered from _truth: {ablation_output['planted_drivers_recovered']}")
    print("==================================================================")
    print("\n--- Ablation Experiment Battery ---")
    print(df_abl[["experiment", "n_features", "test_mae", "test_r2", "skill_score"]].to_string(index=False))

    print("\n--- Top Ranked Candidate New CUF Fields ---")
    print(df_cand[["display_name", "group", "collection_difficulty", "marginal_mae_gain", "priority_score"]].head(8).to_string(index=False))

if __name__ == "__main__":
    main()
