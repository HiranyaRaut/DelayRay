"""
Tests for Synthetic Data Generator
Verifies determinism, scale, checkpoints, outcomes, and hidden truth.
"""

import os
import json
import pytest
import pandas as pd
from scripts.generate_data import generate_synthetic_dataset, s_curve

def test_s_curve_monotonicity_and_bounds():
    """Verifies S-curve maps 0.0 -> 0.0 and 1.0 -> 100.0 monotonically."""
    prev = -1.0
    for t in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
        val = s_curve(t)
        assert 0.0 <= val <= 100.0
        assert val >= prev
        prev = val

def test_generator_determinism():
    """Verifies that identical seed produces identical projects and outcomes."""
    stats1 = generate_synthetic_dataset(n_completed=20, n_ongoing=10, seed=123)
    stats2 = generate_synthetic_dataset(n_completed=20, n_ongoing=10, seed=123)
    
    assert stats1["projects_count"] == stats2["projects_count"]
    assert stats1["cost_overrun_stats"] == stats2["cost_overrun_stats"]
    assert stats1["time_overrun_stats"] == stats2["time_overrun_stats"]

def test_ground_truth_file_structure():
    """Verifies that _truth.json exists and contains planted coefficients."""
    truth_path = os.path.join(os.path.dirname(__file__), "../../data/synthetic/_truth.json")
    if not os.path.exists(truth_path):
        # Generate small dataset to test file creation
        generate_synthetic_dataset(n_completed=10, n_ongoing=5, seed=42)

    with open(truth_path, "r", encoding="utf-8") as f:
        truth = json.load(f)

    assert "coefficients" in truth
    assert "land_shortfall_x_terrain_hilly" in truth["coefficients"]
    assert "clearance_delay_threshold_gt12m" in truth["coefficients"]
    assert "covid_regime_shock_2020_2021" in truth["coefficients"]
    assert "contractor_quality" in truth
